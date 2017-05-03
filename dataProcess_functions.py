# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 17:01:27 2017

@author: zzk
"""

def num_to_WindCode(num):
    if type(num)==int:
        windCode = "%.6d"%num
    else:
        windCode = num
        
    if windCode[0] == '6' or windCode[0] == '9':
        windCode = windCode + ".SH"
    elif windCode[0] == '0' or windCode[0] == '2' or windCode[0] == '3':
        windCode = windCode + ".SZ"
    return windCode