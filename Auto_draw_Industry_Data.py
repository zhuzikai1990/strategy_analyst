# -*- coding: utf-8 -*-

import pymongo
import matplotlib.pyplot as plt

class Auto_draw_Industry_Data:
    
    def __init__(self,industry):
        self.industry = industry
        print('start to deal with %d industry'%industry)
        
    def startAutoSaveData(self):
        industryNames = {1:'extractive',2:'chemical',3:'steel',4:'metal',5:'building_materials',6:'architectural_ornament',\
7:'electrical_equipment',8:'mechanical_equipment',9:'defence_military',10:'automobile',11:'household_appliances',\
12:'textile_clothing',13:'light_manufacturing',14:'commercial_trade',15:'agriculture',16:'food',17:'leisure_service',\
18:'biological',19:'public_utility',20:'traffic',21:'reality',22:'electronic',23:'computer',24:'media',25:'communication',\
26:'bank',27:'non_bank_financial',28:'synthesize',29:'all'}
        try:
            client=pymongo.MongoClient("localhost",27017)
            print("ConnectedSuccessfully!!!")
        except pymongo.errors.ConnectionFailure,e:
            print("Counld not connect to MongoDb")
    
        database_name = "industry_stock_db1"
        table_name = "win_industry_stock_table"
        db=client[database_name]
        table = db[table_name]

        cursor = table.find({'Industry':industryNames[self.industry]})
        BacktestList = [[],[],[],[]]
        dataMarket = []

        for i in range(cursor.count()):
            data = cursor.next()
            starlevel = int(str(data['name'])[2])
            #BacktestList[starlevel-2].append(data['winToLoss'])
            BacktestList[starlevel-2].append(data['retPort'])
            if starlevel == 3:
                dataMarket.append(data['retMarket'])


        holdDays = []
        longestHoldingDays = len(BacktestList[0])+1
        for i in range(1,longestHoldingDays):
            holdDays.append(i)
        
        #plt.figure(figsize=(8,6))
        for i in range(len(BacktestList)): 
            data = BacktestList[i]
            plt.plot(holdDays,data,lw=1.5,label='Up'+str(i+2))
        plt.plot(holdDays,dataMarket,lw=1.5,label='Market')
        plt.title('2009-2016  Industry: %s'%industryNames[self.industry])
        plt.xlabel('Holding period')
        plt.ylabel('Winning percentage')
        #plt.ylabel('Relative yield')
        plt.grid(True)
        plt.legend()
        plt.show()
 


for i in range(1,30):
    t = Auto_draw_Industry_Data(i)
    t.startAutoSaveData()