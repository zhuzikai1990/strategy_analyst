# -*- coding: utf-8 -*-

import os
import pandas as pd
import backTest_function as btf
import numpy as np
import time
import pymongo

class Autosave_Industry_Data:
    
    def __init__(self,industry):
        self.industry = industry
        print('start to deal with %d industry'%industry)
        
    def startAutoSaveData(self):
        path = os.path.abspath('.')
        industryNames = {1:'extractive',2:'chemical',3:'steel',4:'metal',5:'building_materials',6:'architectural_ornament',\
7:'electrical_equipment',8:'mechanical_equipment',9:'defence_military',10:'automobile',11:'household_appliances',\
12:'textile_clothing',13:'light_manufacturing',14:'commercial_trade',15:'agriculture',16:'food',17:'leisure_service',\
18:'biological',19:'public_utility',20:'traffic',21:'reality',22:'electronic',23:'computer',24:'media',25:'communication',\
26:'bank',27:'non_bank_financial',28:'synthesize',29:'all'}
        startDateNum = 729
        longestHoldingDay = 99
    
        rawData = pd.read_csv(path+'\\closeStock.csv')
        rawIndexData = pd.read_csv(path+'\\windAIndex.csv')
        [uqDate,uqStock,ClosePanel] = btf.changeRetPanelFormat(rawData,self.industry)
        ClosePanel = ClosePanel[startDateNum:]
        uqStock.sort()
        
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

        try:
            client=pymongo.MongoClient("localhost",27017)
            print("ConnectedSuccessfully!!!")
        except pymongo.errors.ConnectionFailure,e:
            print("Counld not connect to MongoDb")
    
        database_name = "industry_stock_db1"
        table_name = "win_industry_stock_table"
        db=client[database_name]
        table = db[table_name]
        
        BacktestList = []
        closeMat = np.mat(adjustedClosePanel[:])
        #rawIndexCloseMat = np.mat(rawIndexData[:]).T
        #indexCloseMat = rawIndexCloseMat[startDateNum:]
        winToLoss = -1
        
        for i in range(len(PortList)):
            print('Doing back-test on group %d'%i)
            backtestListIndex = []
            for j in range(1,longestHoldingDay):
                backtestListIndex.append('Up'+str(i+2)+'T'+str(j))
        
            tempBacktectList =  pd.DataFrame(columns = ['retPort','retMarket'],index = backtestListIndex)
     
            for j in range(1,longestHoldingDay):
                positMat = np.mat(PortList[i][0][:])    
                positMat = btf.signalLag_pa(positMat[:], 2) #买卖滞后于信号
                [retPort,retMarket,winToLoss] = btf.calculateWinPercentageByClose_reduceMarket_AR(positMat, closeMat,j)
                tempBacktectList.iloc[j-1,:] = [retPort,retMarket]
            
            ##insert data into MongoDB
                insert_data = {"Industry":industryNames[self.industry],"name":backtestListIndex[j-1],"retPort":retPort,\
                "retMarket":retMarket,"winToLoss":winToLoss}
                table.insert_one(insert_data)

            BacktestList.append(tempBacktectList)
     
        print('All back-test are done！ Current time:'+time.strftime('%H-%M-%S',time.localtime(time.time())))


for i in range(1,29):
    t = Autosave_Industry_Data(i)
    t.startAutoSaveData()