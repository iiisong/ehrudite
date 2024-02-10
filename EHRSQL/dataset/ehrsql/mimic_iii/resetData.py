# import pandas as pd

# patients = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\originalData\PATIENTS.csv")
# patients.to_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv", mode='w', header=True, index=False)


import os
import shutil


def reset() :
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\ADMISSIONS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\CHARTEVENTS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\cost.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_DIAGNOSES.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_PROCEDURES.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\D_ITEMS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\D_LABITEMS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\DIAGNOSES_ICD.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\ICUSTAYS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\INPUTEVENTS_CV.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\LABEVENTS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\MICROBIOLOGYEVENTS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\OUTPUTEVENTS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\PRESCRIPTIONS.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\PROCEDURES_ICD.csv")
    os.remove("EHRSQL\dataset\ehrsql\mimic_iii\TRANSFERS.csv")


    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\PATIENTS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\ADMISSIONS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\ADMISSIONS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\CHARTEVENTS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\CHARTEVENTS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\cost.csv", "EHRSQL\dataset\ehrsql\mimic_iii\cost.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\D_ICD_DIAGNOSES.csv", "EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_DIAGNOSES.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\D_ICD_PROCEDURES.csv", "EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_PROCEDURES.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\D_ITEMS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\D_ITEMS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\D_LABITEMS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\D_LABITEMS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\DIAGNOSES_ICD.csv", "EHRSQL\dataset\ehrsql\mimic_iii\DIAGNOSES_ICD.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\ICUSTAYS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\ICUSTAYS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\INPUTEVENTS_CV.csv", "EHRSQL\dataset\ehrsql\mimic_iii\INPUTEVENTS_CV.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\LABEVENTS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\LABEVENTS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\MICROBIOLOGYEVENTS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\MICROBIOLOGYEVENTS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\OUTPUTEVENTS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\OUTPUTEVENTS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\PRESCRIPTIONS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\PRESCRIPTIONS.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\PROCEDURES_ICD.csv", "EHRSQL\dataset\ehrsql\mimic_iii\PROCEDURES_ICD.csv")
    shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\TRANSFERS.csv", "EHRSQL\dataset\ehrsql\mimic_iii\TRANSFERS.csv")

    print("Sucessfully reset all .csv files to original data.")
    print("===============================================")


reset()