# -*- coding: utf-8 -*-
import csv
import os
import numpy as np
import pandas as pd

def changeRetPanelFormat(rawData,industry):
    if industry == 29:
        adjustData = rawData[:]
    else:
        adjustData = rawData[rawData.industry==industry][:]
    tempUqStock = adjustData['time']
    uqStock = []##in case the index of tempUqStock does not start from 0
    for i in tempUqStock:
        uqStock.append(i)
    adjustData = adjustData.set_index(adjustData.iloc[:,1])
    adjustData.drop([adjustData.columns[0]],axis =1, inplace = True)
    adjustData.drop([adjustData.columns[0]],axis =1, inplace = True)
    tempDate = adjustData.T.index
    uqDate = []
    for i in range(len(tempDate)):
        uqDate.append(tempDate[i])
    return [uqDate,uqStock,adjustData.T]
    
def adjustRetPanel(RetPanel,adjustUqStock):
    adjustedRetPanel = pd.DataFrame()
    for i in range(len(adjustUqStock)):
        adjustedRetPanel[adjustUqStock[i]] = RetPanel[adjustUqStock[i]]
    return adjustedRetPanel
    
def getStarUpList(uqStock,startDateNum = 0):
    path = os.path.abspath('.')
    rf = open(path+'\startUpForm.csv')
    reader = csv.reader(rf)
    StarUpForm = [row for row in reader]
    rf.close()
    
    sortedStarUpForm = []
    adjustUqStock = []
    tempUqStockNum =0
    tempStarUpNum = 1 ## StarUpForm[0][0] is time
    for i in range(1,len(uqStock)+len(StarUpForm)):
        if tempUqStockNum>=len(uqStock) or tempStarUpNum>=len(StarUpForm):
            break
        if uqStock[tempUqStockNum] ==StarUpForm[tempStarUpNum][0]:
            adjustUqStock.append(uqStock[tempUqStockNum])
            sortedStarUpForm.append(StarUpForm[tempStarUpNum])
            tempUqStockNum+=1
            tempStarUpNum+=1
        elif StarUpForm[tempStarUpNum][0]> uqStock[tempUqStockNum]:
            tempUqStockNum+=1
        elif StarUpForm[tempStarUpNum][0]< uqStock[tempUqStockNum]:
            tempStarUpNum+=1
            

    if startDateNum != 0: 
        adjustSortedStartUpForm = []
        for i in range(len(sortedStarUpForm)):
            tempRow = sortedStarUpForm[i][startDateNum+1:]
            tempRow.insert(0,adjustUqStock[i])
            adjustSortedStartUpForm.append(tempRow)
        sortedStarUpForm = adjustSortedStartUpForm[:]
    
    StarUpList = []
    for i in range(2,6):
        tempStarUpForm=[]
        print("Dealing with %d star Form"%i)
        for j in range(len(sortedStarUpForm)):
            tempRowStarUpForm = []
            for z in range(1,len(sortedStarUpForm[0])):
                if sortedStarUpForm[j][z] == str(i):
                    tempRowStarUpForm.append(1)
                else:
                    tempRowStarUpForm.append(0)
            tempStarUpForm.append(tempRowStarUpForm[:])
        StarUpList.append(tempStarUpForm)

    return [StarUpList,adjustUqStock]
    
def getStarUpList_holding(StarUpList,holdDays):
    
    StartUpForm = []
    for i in holdDays:
        tempStockUpForm = []
        print("Dealing with Stock Up Form with %d holding days"%i)
        for j in range(len(StarUpList)):
            tempRowStockUpForm = []
            nextOne = False
            holding = 1
            for z in range(len(StarUpList[0])):
                
                if StarUpList[j][z] == 1:
                    nextOne = True
                    holding = i
                    
                if nextOne == True: 
                    holding -=1
                    tempRowStockUpForm.append(1)
                    if holding<=0:
                        nextOne = False
                else:
                    tempRowStockUpForm.append(0)
            tempStockUpForm.append(tempRowStockUpForm)
        StartUpForm.append(map(list,zip(*tempStockUpForm[:])))
    return StartUpForm

def isUpStock(rawDataJ,HoldDays,z,i):
    if HoldDays == 0 or z <0:
        return False
        
    if rawDataJ[z] == str(i):
        return True
    else:
        return isUpStock(rawDataJ,HoldDays-1,z-1,i)
    
def signalLag_pa(positMat, day):
    tempMat=np.mat(np.zeros(positMat.shape))
    if day>0:
        tempMat[day:][:] =positMat[0:len(positMat)-day][:]
    else:
        tempMat[0:len(positMat)+day][:] = positMat[-day:][:]
    return tempMat
    
    
def dynamicPositToValSeries_pa(positMat,retMat,dynamicPosit):
    #multiply(positMat,dynamicPosit) is to change int to float
    adjustPosit = np.multiply(positMat,np.ones((len(retMat),1)))/np.sum(positMat,1)
    adjustPosit = np.nan_to_num(adjustPosit)# remove nan and inf
    retMat = np.nan_to_num(retMat)# remove nan and inf
    retSeries = np.sum(np.multiply(adjustPosit, retMat),1)*0.01
    valSeries=np.exp(np.tril(np.ones(len(retMat)))*np.log(1+retSeries))

    return [retSeries, valSeries]
    
def sharpe(returns,rf):
    tempReturn = []
    for i in range(len(returns)):
        if type(rf) != float:
            tempReturn.append(returns[i]-rf[i])
        else:
            tempReturn.append(returns[i]-rf)
    return np.mean(tempReturn)/np.std(returns)

def maxdrawdown(valSeries):
    # pnl profit and loss
    highValue = 0
    drawdown = []
    
    for t in range(len(valSeries)):
        if valSeries[t]> highValue:
            highValue = valSeries[t] 
        drawdown.append((highValue - valSeries[t])/highValue)
        
        
    drawdown.sort()
    temVal = drawdown[-1]
    return temVal.tolist()[0][0]
    
def calculateRetMarketByClose(closeMat, holdingDay,indexCloseMat):
    adjustCloseMatBefore = signalLag_pa(closeMat[:], 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat[:], -(holdingDay-1)) 
    adjustIndexCloseMatBefore = signalLag_pa(indexCloseMat, 1) 
    adjustIndexCloseMatAfter = signalLag_pa(indexCloseMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    retIndexMat = np.nan_to_num((adjustIndexCloseMatAfter - adjustIndexCloseMatBefore)/adjustIndexCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retIndexMat[0][:] = 0
    retIndexMat[len(retIndexMat)-(holdingDay-1):][:] = 0
    
    retMarketAll = np.sum(np.nan_to_num(retMat))
    retMarket = retMarketAll/np.sum(np.size(closeMat))
    
    retIndexAll = np.sum(np.nan_to_num(retIndexMat))
    retIndex = retIndexAll/np.sum(np.size(indexCloseMat))
    return [retMarket,retIndex]
    
def calculateAnnualizeReturnByClose(closeMat, holdingDay,indexCloseMat):
    adjustCloseMatBefore = signalLag_pa(closeMat[:], 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat[:], -(holdingDay-1)) 
    adjustIndexCloseMatBefore = signalLag_pa(indexCloseMat, 1) 
    adjustIndexCloseMatAfter = signalLag_pa(indexCloseMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    retIndexMat = np.nan_to_num((adjustIndexCloseMatAfter - adjustIndexCloseMatBefore)/adjustIndexCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retIndexMat[0][:] = 0
    retIndexMat[len(retIndexMat)-(holdingDay-1):][:] = 0
    
    retMarketAll = np.sum(np.nan_to_num(retMat))
    retMarket = retMarketAll/np.sum(np.size(closeMat))/holdingDay*220
    
    retIndexAll = np.sum(np.nan_to_num(retIndexMat))
    retIndex = retIndexAll/np.sum(np.size(indexCloseMat))/holdingDay*220
    return [retMarket,retIndex]
    
def calculateRetListByClose(positMat, closeMat, holdingDay,years):
    retPort = []
    retMarket = []
    tempNum = len(closeMat)/years
    for i in range(years):
        start = i * tempNum
        end =  start + tempNum -1
        [tempRetPort,tempRetMarket] = calculateRetByClose(positMat[start:end][:], closeMat[start:end][:],holdingDay)
        retPort.append(tempRetPort)
        retMarket.append(tempRetMarket)
    return [retPort,retMarket]
    
def calculateRet(positMat, retMat):
    retAll = np.sum(np.nan_to_num(np.multiply(positMat, retMat)))
    retPort = retAll/np.sum(positMat)
    retMarketAll = np.sum(np.nan_to_num(retMat))
    retMarket = retMarketAll/np.sum(np.size(positMat))
    return [retPort,retMarket]

def calculateRetList(positMat, retMat,years):
    retPort = []
    retMarket = []
    tempNum = len(positMat)/years
    for i in range(years):
        start = i * tempNum
        end =  start + tempNum -1
        [tempRetPort,tempRetMarket] = calculateRet(positMat[start:end][:], retMat[start:end][:])
        retPort.append(tempRetPort)
        retMarket.append(tempRetMarket)
    return [retPort,retMarket]
    
def calculateRetByClose_reduceIndex(positMat, closeMat, holdingDay,indexCloseMat):
    adjustCloseMatBefore = signalLag_pa(closeMat, 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat, -(holdingDay-1)) 
    adjustIndexCloseMatBefore = signalLag_pa(indexCloseMat, 1) 
    adjustIndexCloseMatAfter = signalLag_pa(indexCloseMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore-\
    (adjustIndexCloseMatAfter - adjustIndexCloseMatBefore)/adjustIndexCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retAll = np.sum(np.nan_to_num(np.multiply(positMat, retMat)))
    retPort = retAll/np.sum(positMat)
    retMarketAll = np.sum(np.nan_to_num(retMat))
    retMarket = retMarketAll/np.sum(np.size(positMat))
    return [retPort,retMarket]
    
def calculateRetByClose(positMat, closeMat, holdingDay):
    adjustCloseMatBefore = signalLag_pa(closeMat[:], 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat[:], -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retAll = np.sum(np.nan_to_num(np.multiply(positMat, retMat)))
    retPort = retAll/np.sum(positMat)
    retMarketAll = np.sum(np.nan_to_num(retMat))
    retMarket = retMarketAll/np.sum(np.size(positMat))
    return [retPort,retMarket]
    
def calculateRetByClose_reduceMarket_AR(positMat, closeMat, holdingDay):
    adjustCloseMatBefore = signalLag_pa(closeMat, 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retMatMarket = np.mean(retMat,1)
    retMatPortSum = np.sum(np.nan_to_num(np.multiply(positMat, retMat-retMatMarket)))
    retPort = retMatPortSum/np.sum(positMat)/holdingDay*220
    return [retPort,0]
    
def calculateWinPercentageByClose_reduceMarket_AR(positMat, closeMat, holdingDay):
    adjustCloseMatBefore = signalLag_pa(closeMat, 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retMatMarket = np.mean(retMat,1)
    #retMatMarket =np.nan_to_num(np.sum(retMat,1)/np.sum(retMat!=0,1))
    retMatPort = np.nan_to_num(np.multiply(positMat, retMat-retMatMarket))
    retMatRelativeMarket = np.nan_to_num(retMat-retMatMarket)
    winRate = (retMatPort>0).sum()*1.0/np.count_nonzero(retMatPort)
    winRateMarket = (retMatRelativeMarket>0).sum()*1.0/np.count_nonzero(retMatRelativeMarket)
    
    winMat = retMatPort >0
    winMatRate = np.sum(np.multiply(winMat, retMatPort))/np.sum(winMat)
    lossMat = retMatPort <0
    lossMatRate = np.sum(np.multiply(lossMat, retMatPort))/np.sum(lossMat)
    winToLossRatio = abs(winMatRate/lossMatRate)
    return [winRate,winRateMarket,winToLossRatio]
    
def calculateWinPercentageByClose_reduceMarket_AR_Market(positMat, closeMat, holdingDay):
    adjustCloseMatBefore = signalLag_pa(closeMat, 1) 
    adjustCloseMatAfter = signalLag_pa(closeMat, -(holdingDay-1)) 
    #买卖滞后于信号,所以用当天收盘价   
    retMat = np.nan_to_num((adjustCloseMatAfter - adjustCloseMatBefore)/adjustCloseMatBefore)
    # handle wrong data
    retMat[0][:] = 0
    retMat[len(retMat)-(holdingDay-1):][:] = 0
    
    retMatMarket = np.mean(retMat,1)
    #retMatMarket =np.nan_to_num(np.sum(retMat,1)/np.sum(retMat!=0,1))
    retMatPort = np.nan_to_num(np.multiply(positMat, retMat-retMatMarket))
    retMatRelativeMarket = np.nan_to_num(retMat-retMatMarket)
    winRate = (retMatPort>0).sum()*1.0/np.count_nonzero(retMatPort)
    winRateMarket = (retMatRelativeMarket>0).sum()*1.0/np.count_nonzero(retMatRelativeMarket)
    
    winMat = retMatPort >0
    winMatRate = np.sum(np.multiply(winMat, retMatPort))/np.sum(winMat)
    lossMat = retMatPort <0
    lossMatRate = np.sum(np.multiply(lossMat, retMatPort))/np.sum(lossMat)
    winToLossRatio = abs(winMatRate/lossMatRate)
    
    retWinMarket = np.nan_to_num(retMat-retMatMarket)
    winMarketMat = retWinMarket >0
    winMatRate = np.sum(np.multiply(winMarketMat, retWinMarket))/np.sum(winMarketMat)
    losMarketsMat = retWinMarket <0
    lossMatRate = np.sum(np.multiply(losMarketsMat, retWinMarket))/np.sum(losMarketsMat)
    winToLossRatioMarket = abs(winMatRate/lossMatRate)
    return [winRate,winRateMarket,winToLossRatio,winToLossRatioMarket]    
    
def calculateRetListByClose_reduceIndex(positMat, closeMat,holdingDay,years,indexCloseMat):
    retPort = []
    retMarket = []
    tempNum = len(closeMat)/years
    for i in range(years):
        start = i * tempNum
        end =  start + tempNum -1
        [tempRetPort,tempRetMarket] = calculateRetByClose_reduceIndex(positMat[start:end][:], closeMat[start:end][:],holdingDay,\
        indexCloseMat[start:end][:])
        retPort.append(tempRetPort)
        retMarket.append(tempRetMarket)
    return [retPort,retMarket]
    
def dynamicPosit_pa(positMat, retMat, dynamicPosit,riskFreeRate):
    #收益、净值时间序列
    [retSeriesPort, valSeriesPort] = dynamicPositToValSeries_pa(positMat,retMat,dynamicPosit);  
    
    positMat0=np.mat(np.ones(positMat.shape))
    positMat0[0][:] = 0
    dynamicPositMarket = np.ones((positMat.shape[0],1))
    [retSeriesMarket, valSeriesMarket] = dynamicPositToValSeries_pa(positMat0,retMat,dynamicPositMarket)
    
    #总收益、风控指标
    retPort=float(valSeriesPort[len(valSeriesPort)-1]-1)
    retMarket=float(valSeriesMarket[len(valSeriesMarket)-1]-1)
    alpha=retPort-retMarket
    drawdownPort=maxdrawdown(valSeriesPort)
    drawdownMarket=maxdrawdown(valSeriesMarket)

    Daynum=retMat.shape[0]
    Rate=riskFreeRate/Daynum
    sharpeRatio=sharpe(retSeriesPort,Rate)*np.sqrt(Daynum)
    infoRatio=sharpe(retSeriesPort,retSeriesMarket)*np.sqrt(Daynum)
    
    return [valSeriesPort,valSeriesMarket,retSeriesPort,retSeriesMarket,retPort,retMarket,alpha,drawdownPort,\
        drawdownMarket,sharpeRatio,infoRatio]