# -*- coding: utf-8 -*-

from WindPy import *
import csv

rf = open('C:/pythonFile/Industry_AnalystRating/startForm.csv','r')
reader = csv.reader(rf)
rawData_l = [row for row in reader]
rf.close()
uqDate = rawData_l[0][1:]
start_date = datetime.strptime(uqDate[0],"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
end_date = datetime.strptime(uqDate[-1],"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

w.start()


tempData = w.wsd("881001.WI", "close", start_date, end_date, "PriceAdj=F")
print("start to get windA data")
if tempData.ErrorCode==0:
    print("Getting windA data succeeded")
    windAData = tempData.Data
    

csvFile = file('windAIndex.csv','wb')
writer = csv.writer(csvFile,dialect = 'excel')

writer.writerow(uqDate)    
for i in range (len(windAData)):
    tempRow = windAData[i][:]
    writer.writerow(tempRow)        

csvFile.close()

