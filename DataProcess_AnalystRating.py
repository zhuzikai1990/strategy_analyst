# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 09:58:12 2017

@author: zzk
"""

import dataProcess_functions
import csv

#rawData = pd.read_table('C:/pythonFile/python_AnalystRating/SCORE_D_FACT.txt',sep=",",header=None)
rf = open('C:/pythonFile/Industry_AnalystRating/SCORE_D_FACT.txt','r')
reader = csv.reader(rf)
rawData = [row for row in reader]
rf.close()

stockList = []
dataList = []

stockStartData = []
for i in range(len(rawData)):
    stockStartData.append(rawData[i][:])
    stockList.append(rawData[i][0])
    dataList.append(rawData[i][1])

temp=set(stockList)
uqStc=list(temp)
uqStc.sort()

temp=set(dataList)
uqDate=list(temp)
uqDate.sort()

tempNum = 0 
for i in uqStc:
    uqStc[tempNum]=dataProcess_functions.num_to_WindCode(i)
    tempNum +=1

adjustStockStartData = []
tempNum = 0
for i in range(len(uqStc)):
    stock = []
    tempStcId = uqStc[i]
    stock.append(tempStcId)
    for j in range(len(uqDate)):
         tempDateStr = stockStartData[tempNum][1]#'DateStr'
         if tempDateStr == uqDate[j]:
             tempScore = stockStartData[tempNum][2]#'Score'
             tempNum+=1
         elif tempDateStr > uqDate[j]:
             tempScore = 0
         else:
             if stockStartData[tempNum][0] != tempStcId:#'StcID'
                 tempScore = 0
             else:
                 print("there is something wrong")
         stock.append(tempScore)
    adjustStockStartData.append(stock)
    
csvFile = file('startForm.csv','wb')
writer = csv.writer(csvFile,dialect = 'excel')
if uqDate[0] != "time":
    uqDate.insert(0,"time")
writer.writerow(uqDate)
for i in range(len(adjustStockStartData)):
    writer.writerow(adjustStockStartData[i])

csvFile.close()

stockStartUpData = []
for i in range(len(adjustStockStartData)):
    tempStockUp = []
    tempStockUp.append(adjustStockStartData[i][0])
    for j in range(1,len(adjustStockStartData[0])):
        if adjustStockStartData[i][j]>adjustStockStartData[i][j-1] and j!=1:
            tempStockUp.append(adjustStockStartData[i][j])
        else:
            tempStockUp.append(0)
    stockStartUpData.append(tempStockUp) 
    
csvFile = file('startUpForm.csv','wb')
writer = csv.writer(csvFile,dialect = 'excel')
if uqDate[0] != "time":
    uqDate.insert(0,"time")
writer.writerow(uqDate)
for i in range(len(stockStartUpData)):
    writer.writerow(stockStartUpData[i])

csvFile.close()
    