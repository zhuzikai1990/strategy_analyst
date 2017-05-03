# -*- coding: utf-8 -*-

import pymongo
import matplotlib.pyplot as plt

industryNames = {1:'extractive',2:'chemical',3:'steel',4:'metal',5:'building_materials',6:'architectural_ornament',\
7:'electrical_equipment',8:'mechanical_equipment',9:'defence_military',10:'automobile',11:'household_appliances',\
12:'textile_clothing',13:'light_manufacturing',14:'commercial_trade',15:'agriculture',16:'food',17:'leisure_service',\
18:'biological',19:'public_utility',20:'traffic',21:'reality',22:'electronic',23:'computer',24:'media',25:'communication',\
26:'bank',27:'non_bank_financial',28:'synthesize',29:'all'}
industry = 29
try:
    client=pymongo.MongoClient("localhost",27017)
    print("ConnectedSuccessfully!!!")
except pymongo.errors.ConnectionFailure,e:
    print("Counld not connect to MongoDb")
    
database_name = "industry_stock_db1"
table_name = "industry_stock_table"
db=client[database_name]
table = db[table_name]

cursor = table.find({'Industry':industryNames[industry]})
BacktestList = [[],[],[],[]]

for i in range(cursor.count()):
    data = cursor.next()
    starlevel = int(str(data['name'])[2])
    BacktestList[starlevel-2].append(data['retPort'])

holdDays = []
for i in range(1,100):
    holdDays.append(i)
    
plt.figure(figsize=(8,6))
for i in range(len(BacktestList)): 
    data = BacktestList[i]
    plt.plot(holdDays,data,lw=1.5,label='Up'+str(i+2))
plt.grid(True)
plt.legend()
plt.show()
