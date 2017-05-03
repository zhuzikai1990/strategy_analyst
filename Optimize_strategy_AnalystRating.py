# -*- coding: utf-8 -*-

import os
import pandas as pd
import backTest_function as btf
import numpy as np
import time
import pymongo

path = os.path.abspath('.')
industryNames = {1:'extractive',2:'chemical',3:'steel',4:'metal',5:'building_materials',6:'architectural_ornament',\
7:'electrical_equipment',8:'mechanical_equipment',9:'defence_military',10:'automobile',11:'household_appliances',\
12:'textile_clothing',13:'light_manufacturing',14:'commercial_trade',15:'agriculture',16:'food',17:'leisure_service',\
18:'biological',19:'public_utility',20:'traffic',21:'reality',22:'electronic',23:'computer',24:'media',25:'communication',\
26:'bank',27:'non_bank_financial',28:'synthesize',29:'all'}
industry = 29

if not 'RetPanel' in vars():
    rawData = pd.read_csv(path+'\\yieldPCT.csv')
    [uqDate,uqStock,RetPanel] = btf.changeRetPanelFormat(rawData,industry)
    uqStock.sort()
    
if not 'PortList' in vars():
    [StarUpList,adjustUqStock] = btf.getStarUpList(uqStock)
    holdDays = []
    for i in range(1,100):
        holdDays.append(i)
    
    if len(adjustUqStock)!= len(uqStock):
        adjustedRetPanel = btf.adjustRetPanel(RetPanel,adjustUqStock)
    else:
        adjustedRetPanel = RetPanel
        
    PortList = []
    for i in StarUpList:
        PortList.append(btf.getStarUpList_holding(i,holdDays))
        
#add one for up two
#cmd c:\mongos\bin\mongod.exe -dbpath f:\mongodb\data\db
try:
    client=pymongo.MongoClient("localhost",27017)
    print("ConnectedSuccessfully!!!")
except pymongo.errors.ConnectionFailure,e:
    print("Counld not connect to MongoDb")
    
database_name = "industry_stock_db1"
table_name = "industry_stock_table"
db=client[database_name]
table = db[table_name]
    
if not 'BacktestList' in vars():

    BacktestList = []
    for i in range(len(PortList)):
        print('Doing back-test on group %d'%i)
        backtestListIndex = []
        for j in range(1,100):
            backtestListIndex.append('Up'+str(i+2)+'T'+str(j))
        
        tempBacktectList =  pd.DataFrame(columns = ['valSeriesPort','valSeriesMarket','retSeriesPort',\
        'retSeriesMarket','retPort','retMarket','alpha','drawdownPort','drawdownMarket','sharpeRatio',\
        'infoRatio'],index = backtestListIndex)
    
        retMat = np.mat(adjustedRetPanel[:])
        dynamicPosit = np.ones(len(retMat)) *1
        riskFreeRate = 0.03
     
        for j in range(len(PortList[i])):
            positMat = np.mat(PortList[i][j][:])    
            positMat = btf.signalLag_pa(positMat[:], 1) #买卖滞后于信号
            [valSeriesPort,valSeriesMarket,retSeriesPort,retSeriesMarket,retPort,retMarket,alpha,drawdownPort,\
            drawdownMarket,sharpeRatio,infoRatio] = btf.dynamicPosit_pa(positMat, retMat, dynamicPosit,\
            riskFreeRate)
            tempBacktectList.iloc[j,:] = [valSeriesPort,valSeriesMarket,retSeriesPort,retSeriesMarket,retPort,retMarket,\
            alpha,drawdownPort,drawdownMarket,sharpeRatio,infoRatio]
            
            ##insert data into MongoDB
            insert_data = {"Industry":industryNames[industry],"name":backtestListIndex[j],"retPort":retPort,\
            "retMarket":retMarket,"alpha":alpha,"drawdownPort":drawdownPort,"drawdownMarket":drawdownMarket,\
            "sharpeRatio":sharpeRatio,"infoRatio":infoRatio}
            table.insert_one(insert_data)

        BacktestList.append(tempBacktectList)
     
    print('All back-test are done！ Current time:'+time.strftime('%H-%M-%S',time.localtime(time.time())))

#==============================================================================
#     plt.figure(figsize=(8,6))
#     for i in range(len(BacktestList)): 
#         data = BacktestList[i]['retPort']
#         plt.plot(holdDays,data,lw=1.5,label='Up'+str(i+2))
#     plt.grid(True)
#     plt.legend()
#     plt.show()
#==============================================================================
