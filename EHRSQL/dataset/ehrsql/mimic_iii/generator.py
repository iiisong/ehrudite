import random
import pandas as pd



# Completed 
# [x] generateData patients 
# [ ] generateData admissions
# [ ] generateData charterEvents
# [ ] generateData cost
# [ ] generateData d_icd_diag
# [ ] generateData d_icd_proce
# [ ] generateData d_items
# [ ] generateData d_labItems
# [ ] generateData diagnoses_icd
# [ ] generateData icuStays
# [ ] generateData inputEvents
# [ ] generateData labEvents
# [ ] generateData microbiologyEvents
# [ ] generateData outputEvents
# [ ] generateData prescriptions
# [ ] generateData procedures_icd
# [ ] generateData transfers



def generateData_patients(num, startRow) :
    
    additionalData = {
        'row_id': [],
        'subject_id': [],
        'gender': [],
        'dob': [],
        'dod': []
    }

    currentNo = 44228

    for i in range(0, num) :
        additionalData['row_id'].append(startRow)
        additionalData['subject_id'].append(currentNo + int(random.uniform(0, 100)))
        additionalData['gender'].append(random.choice(['m', 'f']))
        # additionalData['dob'].append('1990-01-01')

        birthyear = (random.randint(2010,2100))
        birth = str(birthyear) + '-' + str(random.randint(1,12)) + '-' + str(random.randint(1,28))
        birth += " 00:00"
        additionalData['dob'].append(birth)

        if (random.choice([True, False])) :
            death = str(birthyear + random.randint(30,100)) + '-' + str(random.randint(1,12)) + '-' + str(random.randint(1,28))
            death += " 00:00"
            additionalData['dod'].append(death)
        else :
            additionalData['dod'].append('')

        startRow += 1

    return additionalData


import resetData
resetData.reset()








numGenerate = {
    'patients': 300,
}


startRow = {
    'patients': 50,
}
# startRow = len(patients.index) # number of rows already there -- row counter starts at 0
# print(len(patients.index))


newData_patients = pd.DataFrame(generateData_patients(numGenerate['patients'], startRow['patients']))

print(newData_patients)
# print(generateData(10,1))





# accesssing existing data 
patients = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv")
# admissions = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\ADMISSIONS.csv")
# chartEvents = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\CHARTEVENTS.csv")
# cost = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\cost.csv")
# d_icd_diag = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_DIAGNOSES.csv")
# d_icd_proce = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\D_ICD_PROCEDURES.csv")
# d_items = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\D_ITEMS.csv")
# d_labItems = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\D_LABITEMS.csv")
# diagnoses_icd = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\DIAGNOSES_ICD.csv")
# icuStays = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\ICUSTAYS.csv")
# inputEvents = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\INPUTEVENTS_CV.csv")
# labEvents = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\LABEVENTS.csv")
# microbiologyEvents = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\MICROBIOLOGYEVENTS.csv")
# outputEvents = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\OUTPUTEVENTS.csv")
# prescriptions = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\PRESCRIPTIONS.csv")
# procedures_icd = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\PROCEDURES_ICD.csv")
# transfers = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\TRANSFERS.csv")



newData_patients.to_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv", mode='a', header=False, index=False)



print("Sucessfully added " + str(numGenerate) + " rows to PATIENTS.csv")