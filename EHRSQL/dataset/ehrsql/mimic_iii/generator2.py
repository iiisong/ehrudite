import random
import pandas as pd






# Useful data and variables


maxNumAdmissions = 7

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


numGenerate = {
    'patients': 300,
    'admissions': 0,
    'chartEvents': 0,
    'cost': 0,
    'd_icd_diag': 0,
    'd_icd_proce': 0,
    'd_items': 0,
    'd_labItems': 0,
    'diagnoses_icd': 0,
    'icuStays': 0,
    'inputEvents': 0,
    'labEvents': 0,
    'microbiologyEvents': 0,
    'outputEvents': 0,
    'prescriptions': 0,
    'procedures_icd': 0,
    'transfers': 0
}


startRow = {
    'patients': 50,
    'admissions': 124,
    'chartEvents': 237004,
    'cost': 0,
    'd_icd_diag': 0,
    'd_icd_proce': 0,
    'd_items': 0,
    'd_labItems': 0,
    'diagnoses_icd': 0,
    'icuStays': 0,
    'inputEvents': 0,
    'labEvents': 0,
    'microbiologyEvents': 0,
    'outputEvents': 0,
    'prescriptions': 0,
    'procedures_icd': 0,
    'transfers': 0
}

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



def generateData_patients(num) :
    currentNo = 44228

    for i in range(0, num) :
        additionalData = {
            'row_id': [],
            'subject_id': [],
            'gender': [],
            'dob': [],
            'dod': []
        }

        additionalData['row_id'].append(startRow['patients'])
        startRow['patients'] += 1

        additionalData['subject_id'].append(currentNo + int(random.uniform(0, 100)))
        additionalData['gender'].append(random.choice(['m', 'f']))
        # additionalData['dob'].append('1990-01-01')

        birthyear = (random.randint(2010,2100))
        birth = str(birthyear) + '-' + str(random.randint(1,12)) + '-' + str(random.randint(1,28))
        birth += " 00:00"
        additionalData['dob'].append(birth)

        if (random.choice([True, False, False])) :
            death = str(birthyear + random.randint(30,100)) + '-' + str(random.randint(1,12)) + '-' + str(random.randint(1,28))
            death += " 00:00"
            additionalData['dod'].append(death)
        else :
            additionalData['dod'].append('')


        newData_patients = pd.DataFrame(additionalData)
        newData_patients.to_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv", mode='a', header=False, index=False)




        #insert calls for other table connections here
        randTemp = random.randint(1, maxNumAdmissions)
        for i in range(0, randTemp) :
            admitTime = str(random.randint(0, 23)) + ':' + str(random.randint(0, 59))
            dischTime = str(random.randint(0, 23)) + ':' + str(random.randint(0, 59))

            origBirthYear = birthyear

            birthyear += random.randint(1, 20)
            birthMonth = random.randint(1, 12)
            birthDay = random.randint(1, 28)

            admit = str(birthyear) + '-' + str(birthMonth) + '-' + str(birthDay) + " " + admitTime
            

            birthMonth += random.randint(0,3)
            birthDay += random.randint(0, 20)
            if (birthDay > 28) :
                birthMonth += 1
                if (birthMonth > 12) : 
                    birthMonth = 1
                    birthyear += 1
                
                birthDay %= 28

            discharge = str(birthyear) + '-' + str(birthMonth) + '-' + str(birthDay) + " " + dischTime


            admissionTypes = ['emergency',
                              'emergency',
                              'elective',
                              'urgent',
                              'urgent']
            admissionLocation = ['emergency room admit', 
                                 'emergency room admit', 
                                 'emergency room admit', 
                                 'transfer from hosp/extram', 
                                 'phys referral/normal deli', 
                                 'phys referral/normal deli', 
                                 'clinic referral/premature', 
                                 'clinic referral/premature']
            dischargeLocation = ['home health care',
                                 'snf',
                                 'rehab/distinct part hosp',
                                 'home',
                                 'hospice-home',
                                 'disch-tran to psych hosp',
                                 'home with home iv providr',
                                 'long term care hospital',
                                 'icf']
            insurance = ['Medicare',
                         'Medicaid',
                         'Private',
                         'Self Pay']
            languages = ['ENGL',
                         'SPAN',
                         'RUSS',
                         'PTUN',
                         'CANT',
                         'MAND',
                         'ARAB',
                         'VIET',
                         'PORT',
                         'HAIT',
                         'ITAL',
                         'GREE',
                         'PERS',
                         'CAMB',
                         'POLI',
                         'GERM',
                         'DUTC',
                         'ALBA',
                         'FREN',
                         'HIND',
                         'URDU',
                         'SERB',
                         'HMNG',
                         'LAOT',
                         'THAI',
                         'BURM',
                         'JAPN',
                         'KORE',
                         'CHIN']
            maritalStatus = ['MARRIED',
                             'SINGLE',
                             'DIVORCED',
                             'WIDOWED'
                             'SEPARATED']
            ethinicity = ['WHITE',
                          'BLACK/AFRICAN AMERICAN',
                          'HISPANIC OR LATINO',
                          'ASIAN',
                          'AMERICAN INDIAN/ALASKA NATIVE',
                          'OTHER']



            generateData_admissions(additionalData['subject_id'][0], 
                                    admit, discharge, 
                                    random.choice(admissionTypes), 
                                    random.choice(admissionLocation), 
                                    ('dead/expired' if i == randTemp and random.choice(True, False, False, False) else random.choice(dischargeLocation)), 
                                    random.choice(insurance), 
                                    ('' if random.randint(0, 10) < 7 else random.choice(languages)), 
                                    random.choice(maritalStatus), 
                                    random.choice(ethinicity), 
                                    origBirthYear - birthyear)



def generateData_admissions(subjId, 
                            admitTime, 
                            dischTime, 
                            admissionType, 
                            admissionLocation, 
                            dischargeLocation, 
                            insurance, 
                            language, 
                            maritalStatus,
                            ethinicity, 
                            age) :
    
    additionalData = {
        'row_id': [startRow['admissions']],
        'subject_id': [subjId],
        'hadm_id': [],
        'admittime': [admitTime],
        'dischtime': [dischTime],
        'admission_type': [admissionType],
        'admission_location': [admissionLocation],
        'discharge_location': [dischargeLocation],
        'insurance': [insurance],
        'language': [language],
        'marital_status': [maritalStatus],
        'ethnicity': [ethinicity],
        'AGE': [age]
    }
    startRow['admissions'] += 1
    admissions = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\ADMISSIONS.csv")



    # generate hadm_id
    hadmPot = random.randint(100376, 420000)
    while(hadmPot in admissions['hadm_id']) :
        hadmPot = random.randint(100376, 420000)
        
    additionalData['hadm_id'].append(hadmPot)





# generate patient
# calls generate admission at least once
# each admission has a HADM_ID which calls multiple CHARTEVENTS



import resetData

generateData_patients(numGenerate['patients'])




# accesssing existing data 
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



# print("Sucessfully added " + str(numGenerate) + " rows to PATIENTS.csv")

print("Sucessfully added " + str(numGenerate['patients']) + " patients")

print("\nDetails about addition:")
print(numGenerate)