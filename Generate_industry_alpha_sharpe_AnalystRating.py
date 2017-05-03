# -*- coding: utf-8 -*-

import pymongo
import pandas as pd

industryNames =  {1:'extractive',2:'chemical',3:'steel',4:'metal',5:'building_materials',6:'architectural_ornament',\
7:'electrical_equipment',8:'mechanical_equipment',9:'defence_military',10:'automobile',11:'household_appliances',\
12:'textile_clothing',13:'light_manufacturing',14:'commercial_trade',15:'agriculture',16:'food',17:'leisure_service',\
18:'biological',19:'public_utility',20:'traffic',21:'reality',22:'electronic',23:'computer',24:'media',25:'communication',\
26:'bank',27:'non_bank_financial',28:'synthesize',29:'all'}

industryList = []
for i in range(len(industryNames)):
    industryList.append(industryNames[i+1])

industryAlphaShapeColumns = []
for i in range(4):
    for j in range(3):
        tempAlpha = 'Up'+str(i+2)+'T'+str(j*2+1)+'alpha'
        tempShape = 'Up'+str(i+2)+'T'+str(j*2+1)+'sharpe'
        tempInfo = 'Up'+str(i+2)+'T'+str(j*2+1)+'info'
        tempRet = 'Up'+str(i+2)+'T'+str(j*2+1)+'ret'
        industryAlphaShapeColumns.append(tempAlpha)
        industryAlphaShapeColumns.append(tempShape)
        industryAlphaShapeColumns.append(tempInfo)
        industryAlphaShapeColumns.append(tempRet)
    tempAlpha = 'Up'+str(i+2)+'T10'+'alpha'
    tempShape = 'Up'+str(i+2)+'T10'+'sharpe'
    tempInfo = 'Up'+str(i+2)+'T10'+'info'
    tempRet = 'Up'+str(i+2)+'T10'+'ret'
    industryAlphaShapeColumns.append(tempAlpha)
    industryAlphaShapeColumns.append(tempShape)
    industryAlphaShapeColumns.append(tempInfo)
    industryAlphaShapeColumns.append(tempRet)
        
industryAlphaShapeList = pd.DataFrame(columns=industryAlphaShapeColumns,index = industryList)

try:
    client=pymongo.MongoClient("localhost",27017)
    print("ConnectedSuccessfully!!!")
except pymongo.errors.ConnectionFailure,e:
    print("Counld not connect to MongoDb")
    
database_name = "industry_stock_db1"
table_name = "industry_stock_table"
db=client[database_name]
table = db[table_name]

for i in range(1,30):
    cursor = table.find({'Industry':industryNames[i]})
    tempList = []
    tempNum = 0
    for j in range(cursor.count()):
        data = cursor.next()
        if tempNum <len(industryAlphaShapeColumns) and industryAlphaShapeColumns[tempNum][0:-5]==str(data['name']):
            tempNum +=4
            tempList.append(data['alpha'])
            tempList.append(data['sharpeRatio'])
            tempList.append(data['infoRatio'])
            tempList.append(data['retPort'])
    industryAlphaShapeList.iloc[i-1,:] = tempList
    print('finish %d industry'%i)
    





