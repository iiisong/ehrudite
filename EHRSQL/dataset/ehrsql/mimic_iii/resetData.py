# import pandas as pd

# patients = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\originalData\PATIENTS.csv")
# patients.to_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv", mode='w', header=True, index=False)


import os
import shutil


def reset() :
    files = ["PATIENTS.csv",
             "ADMISSIONS.csv",
             "CHARTEVENTS.csv",
             "cost.csv", 
             "D_ICD_DIAGNOSES.csv", 
             "D_ICD_PROCEDURES.csv", 
             "D_ITEMS.csv", 
             "D_LABITEMS.csv", 
             "DIAGNOSES_ICD.csv", 
             "ICUSTAYS.csv", 
             "INPUTEVENTS_CV.csv", 
             "LABEVENTS.csv", 
             "MICROBIOLOGYEVENTS.csv", 
             "OUTPUTEVENTS.csv", 
             "PRESCRIPTIONS.csv", 
             "PROCEDURES_ICD.csv", 
             "TRANSFERS.csv"]
    
    for file in files:
        if os.path.exists("EHRSQL\dataset\ehrsql\mimic_iii\originalData\\" + file):
            print("Resetting " + file + " to original data.")
            os.remove("EHRSQL\dataset\ehrsql\mimic_iii\\" + file)
            shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\\" + file, "EHRSQL\dataset\ehrsql\mimic_iii\\" + file)
        else:
            print("Error: " + file + " does not exist in originalData folder. Adding new.")
            shutil.copy("EHRSQL\dataset\ehrsql\mimic_iii\originalData\\" + file, "EHRSQL\dataset\ehrsql\mimic_iii\\" + file)



    print("Sucessfully reset all .csv files to original data.")
    print("===============================================")


reset()