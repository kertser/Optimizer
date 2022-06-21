# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 08:39:55 2020

File for RZ-300-HDR Dose Calculator

@author: Mike
"""
from math import log10 as log

## Dose Coefficents
a = 1.9723460342
b = 1.1342181946
c = -0.89447843101
d = 1.6521724013
e = 0.1018468648
f = -0.0060928379303
g = 1.1855262222

VF_A = 1.006642717 #VF calculation
VF_B = 6.181224702 #VF calculation

LampPower = 2300 #[W]
minFlow = 30#m3h
maxFlow = 500#m3h

#General scheme: 
"""
RED = 10a * (P/100)b * (Q)c * (1/Abs)d * * (UVS)e * 10(f/abs) * Ng
abs = -LOG(UVT/100)
UVS = D1Log average inactivation
N = number of lamps
Flow units - [m3/h]
"""

def RED(P,Status,Flow,UVT,D1Log,NLamps):
    if NLamps>2:
        RED = (10**a)*((P/100*Status/100)**b)*((Flow/0.2271)**c)*((1/(-log(UVT/100)))**d)*(D1Log**e)*(10**(f/(-log(UVT/100))))*(NLamps/2*(2**g))
    else:
        RED = (10**a)*((P/100*Status/100)**b)*((Flow/0.2271)**c)*((1/(-log(UVT/100)))**d)*(D1Log**e)*(10**(f/(-log(UVT/100))))*(NLamps**g)
    return round(RED,1)

def VF_RED(RED):
    VF = VF_A*(1+VF_B/RED)
    return round(RED/VF,1)

#HeadLossFactor = 10.1974 #converting bar to mH2O
HeadLossFactor = 1000  # To match the values of the old calculator

# C-flow [bar/(m^3/hour)^2]
C_Flow1 = 0.000000012/2
C_Flow2 = 0.000000022/2
C_Flow3 = 0.000000032/2
C_Flow4 = 0.000000041/2


def HeadLoss(Flow,NLamps):
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    if NLamps == 1:
        return round((HeadLossFactor*C_Flow1*Flow**2)/100,2)
    if NLamps == 2:
        return round((HeadLossFactor*C_Flow2*Flow**2)/100,2)
    if NLamps == 3:
        return round((HeadLossFactor*C_Flow3*Flow**2)/100,2)
    if NLamps == 4:
        return round((HeadLossFactor*C_Flow4*Flow**2)/100,2)
    