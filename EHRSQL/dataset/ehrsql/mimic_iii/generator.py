import random
import pandas as pd



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

patients = pd.read_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv")


numGenerate = 300
# startRow = len(patients.index) # number of rows already there -- row counter starts at 0
# print(len(patients.index))

startRow = 50

newData_patients = pd.DataFrame(generateData_patients(numGenerate, startRow))

print(newData_patients)
# print(generateData(10,1))

newData_patients.to_csv("EHRSQL\dataset\ehrsql\mimic_iii\PATIENTS.csv", mode='a', header=False, index=False)

print("Sucessfully added " + str(numGenerate) + " rows to PATIENTS.csv")