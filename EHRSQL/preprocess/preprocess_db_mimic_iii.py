import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import pymysql
import sqlite3

import warnings

warnings.filterwarnings("ignore")

from preprocess_utils import Sampler, adjust_time, read_csv


class Build_MIMIC_III(Sampler):
    def __init__(
        self,
        data_dir,
        out_dir,
        db_name,
        num_patient,
        sample_icu_patient_only,
        deid=False,
        timeshift=False,
        cur_patient_ratio=0.0,
        start_year=None,
        time_span=None,
        current_time=None,
    ):
        super().__init__()

        self.data_dir = data_dir
        self.out_dir = os.path.join(out_dir, db_name)

        self.deid = deid
        self.timeshift = timeshift

        self.sample_icu_patient_only = sample_icu_patient_only
        self.num_patient = num_patient
        self.num_cur_patient = int(self.num_patient * cur_patient_ratio)
        self.num_non_cur_patient = self.num_patient - int(self.num_patient * cur_patient_ratio)

        if timeshift:
            self.start_year = start_year
            self.start_pivot_datetime = datetime(year=self.start_year, month=1, day=1)
            self.time_span = time_span
            self.current_time = current_time

        # self.conn = sqlite3.connect(os.path.join(self.out_dir, db_name + ".sqlite"))
            
        self.conn = pymysql.connect(os.path.join(self.out_dir, db_name + ".sqlite"))
            
        self.cur = self.conn.cursor()
        with open(os.path.join(self.out_dir, db_name + ".sql"), "r") as sql_file:
            sql_script = sql_file.read()
        self.cur.executescript(sql_script)

        self.chartevent2itemid = {
            "Temperature C (calc)".lower(): "677",  # body temperature
            "SaO2".lower(): "834",  # Sao2
            "heart rate".lower(): "211",  # heart rate
            "Respiratory Rate".lower(): "618",  # respiration rate
            "Arterial BP [Systolic]".lower(): "51",  # systolic blood pressure
            "Arterial BP [Diastolic]".lower(): "8368",  # diastolic blood pressure
            "Arterial BP Mean".lower(): "52",  # mean blood pressure
            "Admit Wt".lower(): "762",  # weight
            "Admit Ht".lower(): "920",  # height
        }

    def build_admission_table(self):
        print("Processing PATIENTS, ADMISSIONS, ICUSTAYS, TRANSFERS")
        start_time = time.time()

        # read patients
        PATIENTS_table = read_csv(self.data_dir, "PATIENTS.csv", columns=["row_id", "subject_id", "gender", "dob", "dod"], lower=True)
        print(PATIENTS_table)
        subjectid2dob = {pid: dob for pid, dob in zip(PATIENTS_table["subject_id"].values, PATIENTS_table["dob"].values)}

        # read admissions
        ADMISSIONS_table = read_csv(
            self.data_dir,
            "ADMISSIONS.csv",
            columns=["row_id", "subject_id", "hadm_id", "admittime", "dischtime", "admission_type", "admission_location", "discharge_location", "insurance", "language", "marital_status", "ethnicity"],
            lower=True,
        )
        ADMISSIONS_table["AGE"] = [
            int((datetime.strptime(admtime, "%Y-%m-%d %H:%M:%S") - datetime.strptime(subjectid2dob[pid], "%Y-%m-%d %H:%M:%S")).days / 365.25)
            for pid, admtime in zip(ADMISSIONS_table["subject_id"].values, ADMISSIONS_table["admittime"].values)
        ]

        # # remove age outliers
        # ADMISSIONS_table = ADMISSIONS_table[(ADMISSIONS_table["AGE"] > 10) & (ADMISSIONS_table["AGE"] < 90)]

        # # remove hospital stay outlier
        # hosp_stay_dict = {
        #     hosp: (datetime.strptime(dischtime, "%Y-%m-%d %H:%M:%S") - datetime.strptime(admtime, "%Y-%m-%d %H:%M:%S")).days
        #     for hosp, admtime, dischtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["admittime"].values, ADMISSIONS_table["dischtime"].values)
        # }
        # threshold_offset = np.percentile(list(hosp_stay_dict.values()), q=95)  # remove greater than 95% ≈ 28 days
        # ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["hadm_id"].isin([hosp for hosp in hosp_stay_dict if hosp_stay_dict[hosp] < threshold_offset])]

        # save original admittime
        self.hadm_id2admtime_dict = {hadm: admtime for hadm, admtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["admittime"].values)}
        self.hadm_id2dischtime_dict = {hadm: dischtime for hadm, dischtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["dischtime"].values)}

        # get earlist admission time
        admittime_earliest = {subj_id: min(ADMISSIONS_table["admittime"][ADMISSIONS_table["subject_id"] == subj_id].values) for subj_id in ADMISSIONS_table["subject_id"].unique()}
        if self.timeshift:
            self.subjectid2admittime_dict = {
                subj_id: self.first_admit_year_sampler(self.start_year, self.time_span, datetime.strptime(admittime_earliest[subj_id], "%Y-%m-%d %H:%M:%S").year)
                for subj_id in ADMISSIONS_table["subject_id"].unique()
            }

        # read icustays
        ICUSTAYS_table = read_csv(
            self.data_dir, "ICUSTAYS.csv", columns=["row_id", "subject_id", "hadm_id", "icustay_id", "first_careunit", "last_careunit", "first_wardid", "last_wardid", "intime", "outtime"], lower=True
        )
        # subset only icu patients
        if self.sample_icu_patient_only:
            ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["subject_id"].isin(set(ICUSTAYS_table["subject_id"]))]

        # read transfer
        TRANSFERS_table = read_csv(
            self.data_dir, "TRANSFERS.csv", columns=["row_id", "subject_id", "hadm_id", "icustay_id", "eventtype", "curr_careunit", "curr_wardid", "intime", "outtime"], lower=True
        )
        TRANSFERS_table = TRANSFERS_table.rename(columns={"curr_careunit": "careunit", "curr_wardid": "wardid"})
        TRANSFERS_table = TRANSFERS_table.dropna(subset=["intime"])

        # process patients
        if self.timeshift:
            PATIENTS_table["dob"] = adjust_time(PATIENTS_table, "dob", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PATIENTS_table["dod"] = adjust_time(PATIENTS_table, "dod", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PATIENTS_table = PATIENTS_table.dropna(subset=["dob"])

        # process admissions
        if self.timeshift:
            ADMISSIONS_table["admittime"] = adjust_time(ADMISSIONS_table, "admittime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ADMISSIONS_table = ADMISSIONS_table.dropna(subset=["admittime"])
            ADMISSIONS_table["dischtime"] = adjust_time(ADMISSIONS_table, "dischtime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ADMISSIONS_table['discharge_location'] = [loc if pd.notnull(t) else None for loc, t in zip(ADMISSIONS_table["discharge_location"], ADMISSIONS_table["dischtime"])]

        # process icustays
        if self.timeshift:
            ICUSTAYS_table["intime"] = adjust_time(ICUSTAYS_table, "intime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ICUSTAYS_table["outtime"] = adjust_time(ICUSTAYS_table, "outtime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ICUSTAYS_table = ICUSTAYS_table.dropna(subset=["intime"])

        # process transfers
        if self.timeshift:
            TRANSFERS_table["intime"] = adjust_time(TRANSFERS_table, "intime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            TRANSFERS_table["outtime"] = adjust_time(TRANSFERS_table, "outtime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            TRANSFERS_table = TRANSFERS_table.dropna(subset=["intime"])

        ################################################################################        
        """
        Decide the final cohort of patients: `self.cur_patient_list` and `self.non_cur_patient`
        """
        # sample current patients
        try:
            self.cur_patient_list = self.rng.choice(
                ADMISSIONS_table["subject_id"][ADMISSIONS_table["dischtime"].isnull()].unique(),
                self.num_cur_patient,
                replace=False,
            ).tolist()
        except:
            print("Cannot take a larger sample than population when 'replace=False")
            print("Use all available patients instead.")
            self.cur_patient_list = ADMISSIONS_table["subject_id"][ADMISSIONS_table["dischtime"].isnull()].unique().tolist()

        # sample non-current patients
        try:
            self.non_cur_patient = self.rng.choice(
                ADMISSIONS_table["subject_id"][(ADMISSIONS_table["dischtime"].notnull()) & (~ADMISSIONS_table["subject_id"].isin(self.cur_patient_list))].unique(),
                self.num_non_cur_patient,
                replace=False,
            ).tolist()
        except:
            print("Cannot take a larger sample than population when 'replace=False")
            print("Use all available patients instead.")
            self.non_cur_patient = ADMISSIONS_table["subject_id"][(ADMISSIONS_table["dischtime"].notnull()) & (~ADMISSIONS_table["subject_id"].isin(self.cur_patient_list))].unique().tolist()

        self.patient_list = self.cur_patient_list + self.non_cur_patient
        print(f"num_cur_patient: {len(self.cur_patient_list)}")
        print(f"num_non_cur_patient: {len(self.non_cur_patient)}")
        print(f"num_patient: {len(self.patient_list)}")

        PATIENTS_table = PATIENTS_table[PATIENTS_table["subject_id"].isin(self.patient_list)]
        ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["subject_id"].isin(self.patient_list)]

        self.hadm_list = list(set(ADMISSIONS_table["hadm_id"]))
        ICUSTAYS_table = ICUSTAYS_table[ICUSTAYS_table["hadm_id"].isin(self.hadm_list)]
        TRANSFERS_table = TRANSFERS_table[TRANSFERS_table["hadm_id"].isin(self.hadm_list)]

        if self.deid:
            icu2careunit = {}
            icu2wardid = {}
            random_indices = self.rng.choice(len(ICUSTAYS_table), len(ICUSTAYS_table), replace=False).tolist()
            for idx, icu in enumerate(ICUSTAYS_table["icustay_id"]):
                icu2careunit[icu] = {}
                icu2careunit[icu][ICUSTAYS_table["first_careunit"][ICUSTAYS_table["icustay_id"] == icu].values[0]] = ICUSTAYS_table["first_careunit"].iloc[random_indices[idx]]
                icu2careunit[icu][ICUSTAYS_table["last_careunit"][ICUSTAYS_table["icustay_id"] == icu].values[0]] = ICUSTAYS_table["last_careunit"].iloc[random_indices[idx]]
                ICUSTAYS_table["first_careunit"][ICUSTAYS_table["icustay_id"] == icu] = ICUSTAYS_table["first_careunit"].iloc[random_indices[idx]]
                ICUSTAYS_table["last_careunit"][ICUSTAYS_table["icustay_id"] == icu] = ICUSTAYS_table["last_careunit"].iloc[random_indices[idx]]
                icu2wardid[icu] = {}
                icu2wardid[icu][ICUSTAYS_table["first_wardid"][ICUSTAYS_table["icustay_id"] == icu].values[0]] = ICUSTAYS_table["first_wardid"].iloc[random_indices[idx]]
                icu2wardid[icu][ICUSTAYS_table["last_wardid"][ICUSTAYS_table["icustay_id"] == icu].values[0]] = ICUSTAYS_table["last_wardid"].iloc[random_indices[idx]]
                ICUSTAYS_table["first_wardid"][ICUSTAYS_table["icustay_id"] == icu] = ICUSTAYS_table["first_wardid"].iloc[random_indices[idx]]
                ICUSTAYS_table["last_wardid"][ICUSTAYS_table["icustay_id"] == icu] = ICUSTAYS_table["last_wardid"].iloc[random_indices[idx]]

            for icu in ICUSTAYS_table["icustay_id"]:
                TRANSFERS_table["careunit"][TRANSFERS_table["icustay_id"] == icu] = TRANSFERS_table["careunit"][TRANSFERS_table["icustay_id"] == icu].replace(icu2careunit[icu])
                TRANSFERS_table["wardid"][TRANSFERS_table["icustay_id"] == icu] = TRANSFERS_table["wardid"][TRANSFERS_table["icustay_id"] == icu].replace(icu2wardid[icu])

        PATIENTS_table["row_id"] = range(len(PATIENTS_table))
        ADMISSIONS_table["row_id"] = range(len(ADMISSIONS_table))
        ICUSTAYS_table["row_id"] = range(len(ICUSTAYS_table))
        TRANSFERS_table["row_id"] = range(len(TRANSFERS_table))

        PATIENTS_table.to_csv(os.path.join(self.out_dir, "PATIENTS.csv"), index=False)
        ADMISSIONS_table.to_csv(os.path.join(self.out_dir, "ADMISSIONS.csv"), index=False)
        ICUSTAYS_table.to_csv(os.path.join(self.out_dir, "ICUSTAYS.csv"), index=False)
        TRANSFERS_table.to_csv(os.path.join(self.out_dir, "TRANSFERS.csv"), index=False)

        print(f"PATIENTS, ADMISSIONS, ICUSTAYS, TRANSFERS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_dictionary_table(self):
        print("Processing D_ICD_DIAGNOSES, D_ICD_PROCEDURES, D_LABITEMS, D_ITEMS")
        start_time = time.time()

        D_ICD_DIAGNOSES_table = read_csv(self.data_dir, "D_ICD_DIAGNOSES.csv", columns=["row_id", "icd9_code", "short_title", "long_title"], lower=True)
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.astype({"icd9_code": str})
        self.D_ICD_DIAGNOSES_dict = {item: val for item, val in zip(D_ICD_DIAGNOSES_table["icd9_code"].values, D_ICD_DIAGNOSES_table["short_title"].values)}

        D_ICD_PROCEDURES_table = read_csv(self.data_dir, "D_ICD_PROCEDURES.csv", columns=["row_id", "icd9_code", "short_title", "long_title"], lower=True)
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.astype({"icd9_code": str}).drop_duplicates(subset=["icd9_code"])
        self.D_ICD_PROCEDURES_dict = {item: val for item, val in zip(D_ICD_PROCEDURES_table["icd9_code"].values, D_ICD_PROCEDURES_table["short_title"].values)}

        D_LABITEMS_table = read_csv(self.data_dir, "D_LABITEMS.csv", columns=["row_id", "itemid", "label"], lower=True)
        self.D_LABITEMS_dict = {item: val for item, val in zip(D_LABITEMS_table["itemid"].values, D_LABITEMS_table["label"].values)}

        D_ITEMS_table = read_csv(self.data_dir, "D_ITEMS.csv", columns=["row_id", "itemid", "label", "linksto"], lower=True)
        D_ITEMS_table = D_ITEMS_table.dropna(subset=["label"])
        D_ITEMS_table = D_ITEMS_table[D_ITEMS_table["linksto"].isin(["inputevents_cv", "outputevents", "chartevents"])]
        self.D_ITEMS_dict = {item: val for item, val in zip(D_ITEMS_table["itemid"].values, D_ITEMS_table["label"].values)}

        D_ICD_DIAGNOSES_table["row_id"] = range(len(D_ICD_DIAGNOSES_table))
        D_ICD_PROCEDURES_table["row_id"] = range(len(D_ICD_PROCEDURES_table))
        D_LABITEMS_table["row_id"] = range(len(D_LABITEMS_table))
        D_ITEMS_table["row_id"] = range(len(D_ITEMS_table))

        D_ICD_DIAGNOSES_table.to_csv(os.path.join(self.out_dir, "D_ICD_DIAGNOSES.csv"), index=False)
        D_ICD_PROCEDURES_table.to_csv(os.path.join(self.out_dir, "D_ICD_PROCEDURES.csv"), index=False)
        D_LABITEMS_table.to_csv(os.path.join(self.out_dir, "D_LABITEMS.csv"), index=False)
        D_ITEMS_table.to_csv(os.path.join(self.out_dir, "D_ITEMS.csv"), index=False)

        print(f"D_ICD_DIAGNOSES, D_ICD_PROCEDURES, D_LABITEMS, D_ITEMS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_diagnosis_table(self):
        print("Processing DIAGNOSES_ICD table")
        start_time = time.time()

        DIAGNOSES_ICD_table = read_csv(self.data_dir, "DIAGNOSES_ICD.csv", columns=["row_id", "subject_id", "hadm_id", "icd9_code"], lower=True)
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.astype({"icd9_code": str})
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.dropna(subset=["icd9_code"])
        DIAGNOSES_ICD_table["charttime"] = [
            self.hadm_id2admtime_dict[hadm] if hadm in self.hadm_id2admtime_dict else None for hadm in DIAGNOSES_ICD_table["hadm_id"].values
        ]  # assume charttime is at the hospital admission

        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[DIAGNOSES_ICD_table["icd9_code"].isin(self.D_ICD_DIAGNOSES_dict)]
        if self.deid:
            DIAGNOSES_ICD_table = self.condition_value_shuffler(DIAGNOSES_ICD_table, target_cols=["icd9_code"])
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[DIAGNOSES_ICD_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            DIAGNOSES_ICD_table["charttime"] = adjust_time(DIAGNOSES_ICD_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in DIAGNOSES_ICD_table["charttime"].values])
            DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[TIME >= self.start_pivot_datetime]

        DIAGNOSES_ICD_table["row_id"] = range(len(DIAGNOSES_ICD_table))
        DIAGNOSES_ICD_table.to_csv(os.path.join(self.out_dir, "DIAGNOSES_ICD.csv"), index=False)

        print(f"DIAGNOSES_ICD processed (took {round(time.time() - start_time, 4)} secs)")

    def build_procedure_table(self):
        print("Processing PROCEDURES_ICD table")
        start_time = time.time()

        PROCEDURES_ICD_table = read_csv(self.data_dir, "PROCEDURES_ICD.csv", columns=["row_id", "subject_id", "hadm_id", "icd9_code"], lower=True)
        PROCEDURES_ICD_table = PROCEDURES_ICD_table.astype({"icd9_code": str})
        PROCEDURES_ICD_table["charttime"] = [
            self.hadm_id2dischtime_dict[hadm] if hadm in self.hadm_id2dischtime_dict else None for hadm in PROCEDURES_ICD_table["hadm_id"].values
        ]  # assume charttime is at the hospital discharge

        PROCEDURES_ICD_table = PROCEDURES_ICD_table[PROCEDURES_ICD_table["icd9_code"].isin(self.D_ICD_PROCEDURES_dict)]
        if self.deid:
            PROCEDURES_ICD_table = self.condition_value_shuffler(PROCEDURES_ICD_table, target_cols=["icd9_code"])
        PROCEDURES_ICD_table = PROCEDURES_ICD_table[PROCEDURES_ICD_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            PROCEDURES_ICD_table["charttime"] = adjust_time(PROCEDURES_ICD_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PROCEDURES_ICD_table = PROCEDURES_ICD_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in PROCEDURES_ICD_table["charttime"].values])
            PROCEDURES_ICD_table = PROCEDURES_ICD_table[TIME >= self.start_pivot_datetime]

        PROCEDURES_ICD_table["row_id"] = range(len(PROCEDURES_ICD_table))
        PROCEDURES_ICD_table.to_csv(os.path.join(self.out_dir, "PROCEDURES_ICD.csv"), index=False)

        print(f"PROCEDURES_ICD processed (took {round(time.time() - start_time, 4)} secs)")

    def build_labevent_table(self):
        print("Processing LABEVENTS table")
        start_time = time.time()

        LABEVENTS_table = read_csv(self.data_dir, "LABEVENTS.csv", columns=["row_id", "subject_id", "hadm_id", "itemid", "charttime", "valuenum", "valueuom"], lower=True)
        LABEVENTS_table = LABEVENTS_table.dropna(subset=["hadm_id", "valuenum", "valueuom"])

        LABEVENTS_table = LABEVENTS_table[LABEVENTS_table["itemid"].isin(self.D_LABITEMS_dict)]
        if self.deid:
            LABEVENTS_table = self.condition_value_shuffler(LABEVENTS_table, target_cols=["itemid", "valuenum", "valueuom"])
        LABEVENTS_table = LABEVENTS_table[LABEVENTS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            LABEVENTS_table["charttime"] = adjust_time(LABEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            LABEVENTS_table = LABEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in LABEVENTS_table["charttime"].values])
            LABEVENTS_table = LABEVENTS_table[TIME >= self.start_pivot_datetime]

        LABEVENTS_table["row_id"] = range(len(LABEVENTS_table))
        LABEVENTS_table.to_csv(os.path.join(self.out_dir, "LABEVENTS.csv"), index=False)

        print(f"LABEVENTS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_prescriptions_table(self):
        print("Processing PRESCRIPTIONS table")
        start_time = time.time()

        PRESCRIPTIONS_table = read_csv(
            self.data_dir, "PRESCRIPTIONS.csv", columns=["row_id", "subject_id", "hadm_id", "startdate", "enddate", "drug", "dose_val_rx", "dose_unit_rx", "route"], lower=True
        )
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["startdate", "enddate", "dose_val_rx", "dose_unit_rx", "route"])
        PRESCRIPTIONS_table["dose_val_rx"] = [int(str(v).replace(",", "")) if str(v).replace(",", "").isnumeric() else None for v in PRESCRIPTIONS_table["dose_val_rx"].values]
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["dose_val_rx"])  # remove not int elements

        drug2unit_dict = {}
        for item, unit in zip(PRESCRIPTIONS_table["drug"].values, PRESCRIPTIONS_table["dose_unit_rx"].values):
            if item in drug2unit_dict:
                drug2unit_dict[item].append(unit)
            else:
                drug2unit_dict[item] = [unit]
        drug_name2unit_dict = {item: Counter(drug2unit_dict[item]).most_common(1)[0][0] for item in drug2unit_dict}  # pick only the most frequent unit of measure

        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["drug"].isin(drug2unit_dict)]
        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["dose_unit_rx"] == [drug_name2unit_dict[drug] for drug in PRESCRIPTIONS_table["drug"]]]
        if self.deid:
            PRESCRIPTIONS_table = self.condition_value_shuffler(PRESCRIPTIONS_table, target_cols=["drug", "dose_val_rx", "dose_unit_rx", "route"])
        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            PRESCRIPTIONS_table["startdate"] = adjust_time(PRESCRIPTIONS_table, "startdate", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PRESCRIPTIONS_table["enddate"] = adjust_time(PRESCRIPTIONS_table, "enddate", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["startdate"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in PRESCRIPTIONS_table["startdate"].values])
            PRESCRIPTIONS_table = PRESCRIPTIONS_table[TIME >= self.start_pivot_datetime]

        PRESCRIPTIONS_table["row_id"] = range(len(PRESCRIPTIONS_table))
        PRESCRIPTIONS_table.to_csv(os.path.join(self.out_dir, "PRESCRIPTIONS.csv"), index=False)

        print(f"PRESCRIPTIONS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_cost_table(self):
        print("Processing cost table")
        start_time = time.time()

        DIAGNOSES_ICD_table = read_csv(self.out_dir, "DIAGNOSES_ICD.csv").astype({"icd9_code": str})
        LABEVENTS_table = read_csv(self.out_dir, "LABEVENTS.csv")
        PROCEDURES_ICD_table = read_csv(self.out_dir, "PROCEDURES_ICD.csv").astype({"icd9_code": str})
        PRESCRIPTIONS_table = read_csv(self.out_dir, "PRESCRIPTIONS.csv")

        cnt = 0
        data_filter = []
        mean_costs = self.rng.poisson(lam=10, size=4)

        cost_id = cnt + np.arange(len(DIAGNOSES_ICD_table))
        person_id = DIAGNOSES_ICD_table["subject_id"].values
        hospitaladmit_id = DIAGNOSES_ICD_table["hadm_id"].values
        cost_event_table_concept_id = DIAGNOSES_ICD_table["row_id"].values
        charge_time = DIAGNOSES_ICD_table["charttime"].values
        diagnosis_cost_dict = {item: round(self.rng.normal(loc=mean_costs[0], scale=1.0), 2) for item in sorted(DIAGNOSES_ICD_table["icd9_code"].unique())}
        cost = [diagnosis_cost_dict[item] for item in DIAGNOSES_ICD_table["icd9_code"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "DIAGNOSES_ICD".lower(),
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(DIAGNOSES_ICD_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(LABEVENTS_table))
        person_id = LABEVENTS_table["subject_id"].values
        hospitaladmit_id = LABEVENTS_table["hadm_id"].values
        cost_event_table_concept_id = LABEVENTS_table["row_id"].values
        charge_time = LABEVENTS_table["charttime"].values
        lab_cost_dict = {item: round(self.rng.normal(loc=mean_costs[1], scale=1.0), 2) for item in sorted(LABEVENTS_table["itemid"].unique())}
        cost = [lab_cost_dict[item] for item in LABEVENTS_table["itemid"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "LABEVENTS".lower(),
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(LABEVENTS_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(PROCEDURES_ICD_table))
        person_id = PROCEDURES_ICD_table["subject_id"].values
        hospitaladmit_id = PROCEDURES_ICD_table["hadm_id"].values
        cost_event_table_concept_id = PROCEDURES_ICD_table["row_id"].values
        charge_time = PROCEDURES_ICD_table["charttime"].values
        procedure_cost_dict = {item: round(self.rng.normal(loc=mean_costs[2], scale=1.0), 2) for item in sorted(PROCEDURES_ICD_table["icd9_code"].unique())}
        cost = [procedure_cost_dict[item] for item in PROCEDURES_ICD_table["icd9_code"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "PROCEDURES_ICD".lower(),
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(PROCEDURES_ICD_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(PRESCRIPTIONS_table))
        person_id = PRESCRIPTIONS_table["subject_id"].values
        hospitaladmit_id = PRESCRIPTIONS_table["hadm_id"].values
        cost_event_table_concept_id = PRESCRIPTIONS_table["row_id"].values
        charge_time = PRESCRIPTIONS_table["startdate"].values
        prescription_cost_dict = {item: round(self.rng.normal(loc=mean_costs[3], scale=1.0), 2) for item in sorted(PRESCRIPTIONS_table["drug"].unique())}
        cost = [prescription_cost_dict[item] for item in PRESCRIPTIONS_table["drug"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "PRESCRIPTIONS".lower(),
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(PRESCRIPTIONS_table)
        data_filter.append(temp)

        cost_table = pd.concat(data_filter, ignore_index=True)
        cost_table.to_csv(os.path.join(self.out_dir, "cost.csv"), index=False)
        print(f"cost processed (took {round(time.time() - start_time, 4)} secs)")

    def build_chartevent_table(self):
        print("Processing CHARTEVENTS table")
        start_time = time.time()

        CHARTEVENTS_table = read_csv(self.data_dir, "CHARTEVENTS.csv", columns=["row_id", "subject_id", "hadm_id", "icustay_id", "itemid", "charttime", "valuenum", "valueuom"], lower=True)
        CHARTEVENTS_table = CHARTEVENTS_table.dropna(subset=["row_id", "subject_id", "hadm_id", "icustay_id", "itemid", "charttime", "valuenum", "valueuom"])

        if self.timeshift:  # changed order due to the large number of rows in CHARTEVENTS_table
            CHARTEVENTS_table["charttime"] = adjust_time(CHARTEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            CHARTEVENTS_table = CHARTEVENTS_table.dropna(subset=["charttime"])

        if self.deid:
            CHARTEVENTS_table = self.condition_value_shuffler(CHARTEVENTS_table, target_cols=["itemid", "valuenum", "valueuom"])
        CHARTEVENTS_table = CHARTEVENTS_table[CHARTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in CHARTEVENTS_table["charttime"].values])
            CHARTEVENTS_table = CHARTEVENTS_table[TIME >= self.start_pivot_datetime]

        CHARTEVENTS_table["row_id"] = range(len(CHARTEVENTS_table))
        CHARTEVENTS_table.to_csv(os.path.join(self.out_dir, "CHARTEVENTS.csv"), index=False)
        print(f"CHARTEVENTS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_inputevent_table(self):
        print("Processing INPUTEVENTS_CV table")
        start_time = time.time()

        INPUTEVENTS_table = read_csv(self.data_dir, "INPUTEVENTS_CV.csv", columns=["row_id", "subject_id", "hadm_id", "icustay_id", "charttime", "itemid", "amount", "amountuom"], lower=True)
        INPUTEVENTS_table = INPUTEVENTS_table.dropna(subset=["hadm_id", "icustay_id", "amount", "amountuom"])
        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["amountuom"] == "ml"]
        del INPUTEVENTS_table["amountuom"]

        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["itemid"].isin(self.D_ITEMS_dict)]
        if self.deid:
            INPUTEVENTS_table = self.condition_value_shuffler(INPUTEVENTS_table, target_cols=["itemid", "amount"])
        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            INPUTEVENTS_table["charttime"] = adjust_time(INPUTEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            INPUTEVENTS_table = INPUTEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in INPUTEVENTS_table["charttime"].values])
            INPUTEVENTS_table = INPUTEVENTS_table[TIME >= self.start_pivot_datetime]

        INPUTEVENTS_table["row_id"] = range(len(INPUTEVENTS_table))
        INPUTEVENTS_table.to_csv(os.path.join(self.out_dir, "INPUTEVENTS_CV.csv"), index=False)

        print(f"INPUTEVENTS_CV processed (took {round(time.time() - start_time, 4)} secs)")

    def build_outputevent_table(self):
        print("Processing OUTPUTEVENTS table")
        start_time = time.time()

        OUTPUTEVENTS_table = read_csv(self.data_dir, "OUTPUTEVENTS.csv", columns=["row_id", "subject_id", "hadm_id", "icustay_id", "charttime", "itemid", "value", "valueuom"], lower=True)
        OUTPUTEVENTS_table = OUTPUTEVENTS_table.dropna(subset=["hadm_id", "icustay_id", "value", "valueuom"])
        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["valueuom"] == "ml"]
        del OUTPUTEVENTS_table["valueuom"]

        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["itemid"].isin(self.D_ITEMS_dict)]
        if self.deid:
            OUTPUTEVENTS_table = self.condition_value_shuffler(OUTPUTEVENTS_table, target_cols=["itemid", "value"])
        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            OUTPUTEVENTS_table["charttime"] = adjust_time(OUTPUTEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            OUTPUTEVENTS_table = OUTPUTEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in OUTPUTEVENTS_table["charttime"].values])
            OUTPUTEVENTS_table = OUTPUTEVENTS_table[TIME >= self.start_pivot_datetime]

        OUTPUTEVENTS_table["row_id"] = range(len(OUTPUTEVENTS_table))
        OUTPUTEVENTS_table.to_csv(os.path.join(self.out_dir, "OUTPUTEVENTS.csv"), index=False)

        print(f"OUTPUTEVENTS processed (took {round(time.time() - start_time, 4)} secs)")

    def build_microbiology_table(self):
        print("Processing MICROBIOLOGYEVENTS table")
        start_time = time.time()

        MICROBIOLOGYEVENTS_table = read_csv(self.data_dir, "MICROBIOLOGYEVENTS.csv", columns=["row_id", "subject_id", "hadm_id", "chartdate", "charttime", "spec_type_desc", "org_name"], lower=True)
        MICROBIOLOGYEVENTS_table["charttime"] = MICROBIOLOGYEVENTS_table["charttime"].fillna(MICROBIOLOGYEVENTS_table["chartdate"])
        MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table.drop(columns=["chartdate"])
        if self.deid:
            MICROBIOLOGYEVENTS_table = self.condition_value_shuffler(MICROBIOLOGYEVENTS_table, target_cols=["spec_type_desc", "org_name"])
        MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table[MICROBIOLOGYEVENTS_table["hadm_id"].isin(self.hadm_list)]

        if self.timeshift:
            MICROBIOLOGYEVENTS_table["charttime"] = adjust_time(
                MICROBIOLOGYEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id"
            )
            MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in MICROBIOLOGYEVENTS_table["charttime"].values])
            MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table[TIME >= self.start_pivot_datetime]

        MICROBIOLOGYEVENTS_table["row_id"] = range(len(MICROBIOLOGYEVENTS_table))
        MICROBIOLOGYEVENTS_table.to_csv(os.path.join(self.out_dir, "MICROBIOLOGYEVENTS.csv"), index=False)

        print(f"MICROBIOLOGYEVENTS processed (took {round(time.time() - start_time, 4)} secs)")

    def generate_db(self):
        rows = read_csv(self.out_dir, "PATIENTS.csv")
        rows.to_sql("PATIENTS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "ADMISSIONS.csv")
        rows.to_sql("ADMISSIONS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "D_ICD_DIAGNOSES.csv").astype({"icd9_code": str})
        rows.to_sql("D_ICD_DIAGNOSES", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "D_ICD_PROCEDURES.csv").astype({"icd9_code": str})
        rows.to_sql("D_ICD_PROCEDURES", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "D_ITEMS.csv")
        rows.to_sql("D_ITEMS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "D_LABITEMS.csv")
        rows.to_sql("D_LABITEMS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "DIAGNOSES_ICD.csv").astype({"icd9_code": str})
        rows.to_sql("DIAGNOSES_ICD", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "PROCEDURES_ICD.csv").astype({"icd9_code": str})
        rows.to_sql("PROCEDURES_ICD", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "LABEVENTS.csv")
        rows.to_sql("LABEVENTS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "PRESCRIPTIONS.csv")
        rows.to_sql("PRESCRIPTIONS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "cost.csv")
        rows.to_sql("COST", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "CHARTEVENTS.csv")
        rows.to_sql("CHARTEVENTS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "INPUTEVENTS_CV.csv")
        rows.to_sql("INPUTEVENTS_CV", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "OUTPUTEVENTS.csv")
        rows.to_sql("OUTPUTEVENTS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "MICROBIOLOGYEVENTS.csv")
        rows.to_sql("MICROBIOLOGYEVENTS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "ICUSTAYS.csv")
        rows.to_sql("ICUSTAYS", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "TRANSFERS.csv")
        rows.to_sql("TRANSFERS", self.conn, if_exists="append", index=False)

        query = "SELECT * FROM sqlite_master WHERE type='table'"
        print(pd.read_sql_query(query, self.conn)["name"])  # 17 tables
