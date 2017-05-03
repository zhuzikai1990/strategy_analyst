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
startDateNum = 729
longestHoldingDay = 99

if not 'ClosePanel' in vars():
    #rawData = pd.read_csv(path+'\\yieldPCT.csv')
    rawData = pd.read_csv(path+'\\closeStock.csv')
    rawIndexData = pd.read_csv(path+'\\windAIndex.csv')
    [uqDate,uqStock,ClosePanel] = btf.changeRetPanelFormat(rawData,industry)
    ClosePanel = ClosePanel[startDateNum:]
    uqStock.sort()
    
if not 'PortList' in vars():
    [StarUpList,adjustUqStock] = btf.getStarUpList(uqStock,startDateNum)
    holdDays = []
    for i in range(1,2):
        holdDays.append(i)
    
    if len(adjustUqStock)!= len(uqStock):
        adjustedClosePanel = btf.adjustRetPanel(ClosePanel,adjustUqStock)
    else:
        adjustedClosePanel = ClosePanel
        
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
#table_name = "ret_industry_stock_table_try"
# table_names = ["ret_industry_stock_table","ret_industry_stock_table_try","win_industry_stock_table"]
table_name = "abc_industry_stock_table"
db=client[database_name]
table = db[table_name]
winToLoss = -1
    
if not 'BacktestList' in vars():

    BacktestList = []
    closeMat = np.mat(adjustedClosePanel[:])
    rawIndexCloseMat = np.mat(rawIndexData[:]).T
    indexCloseMat = rawIndexCloseMat[startDateNum:]
        
    for i in range(len(PortList)):
        print('Doing back-test on group %d'%i)
        backtestListIndex = []
        for j in range(1,longestHoldingDay):
            backtestListIndex.append('Up'+str(i+2)+'T'+str(j))
        
        tempBacktectList =  pd.DataFrame(columns = ['retPort'],index = backtestListIndex)
     
        for j in range(1,longestHoldingDay):
            positMat = np.mat(PortList[i][0][:])    
            positMat = btf.signalLag_pa(positMat[:], 2) #买卖滞后于信号
            [retPort,retMarket,winToLoss,winMarket] = btf.calculateWinPercentageByClose_reduceMarket_AR_Market(positMat, closeMat,j)
            tempBacktectList.iloc[j-1,:] = [retPort]
            
            ##insert data into MongoDB
            insert_data = {"Industry":industryNames[industry],"name":backtestListIndex[j-1],"retPort":retPort,\
            "retMarket":winMarket,"winToLoss":winToLoss}
            table.insert_one(insert_data)

        BacktestList.append(tempBacktectList)
     
    print('All back-test are done！ Current time:'+time.strftime('%H-%M-%S',time.localtime(time.time())))
