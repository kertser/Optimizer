# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 20:36:00 2020

File for R200-SL/DL Dose Calculator - single lamp per module

@author: Mike
"""

from math import log as ln

# C-flow [bar/(m^3/hour)^2]
C_Flow_SL = 2.216E-06
C_Flow_DL = 0.0000041
#HeadLossFactor = 1019.72 #bar to cmH2O
HeadLossFactor = 1000 # This change is to make it equal to the old calculator


## Dose Coefficents
# RZM-11: - Base
LampPower = 4200 #[W] - 300W/cm for 140mm arc-length lamp
minFlow = 50 #[m3h]
maxFlow = 1000 #[m3h]

minUVT_fit = 76 #[%-1cm]
minUVT = 65 #[%-1cm]
maxUVT = 99.5 #[%-1cm]
minDrive = 25 #[%]
maxDrive = 100 #[%]
minLeff = 50 #[%]
maxLeff = 100 #[%]

#constants
TAD0 = 300
TAD_h = 220
TUF1 = 1/7000
TUF2 = -1/36
TUF3 = -1.26
TUF4 = 0.02
WAT1 = 80
WAT2 = 0.88
n_max = 16
BTS_factor = 1

b0 = 0.755
b1 = 0.0933
b2 = -0.0083

eta_g = 0.1


Arc_length = 14#[cm]
L_react_L_eff_ratio = 3.5
Unit_converter_1 = 3.6
Unit_converter_2 = 157.725 #(m3h to MGD)


def RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps): #Here we shall modify for DL - P1,P2 Eff1, Eff2    

    if NLamps == 1:
        eta_coupling = 0.6
    else: #NLamps ==2
        eta_coupling = 0.79
    
    # Taking an average power and/or efficiency for 2 lamps:
    P = (P1+P2)/2
    Eff1 = (Eff1+Eff2)/2
        
    P_Gmax = NLamps*LampPower*eta_g*eta_coupling*(Eff1/100) #[W]    
        
    P_electrical=NLamps*LampPower*(P/100)        
    WAT_1cm = WAT1+WAT2*(UVT-WAT1) #[%-1cm]
    x_NL = (P_electrical/NLamps)/1000#[kW - one lamp]
    
    NLF = b0+b1*x_NL+b2*x_NL**2
    P_G = P_Gmax*(P/100)*NLF #[W]
    Alfa_WAT = -ln(WAT_1cm/100)
    
    TAD = BTS_factor*Unit_converter_1*(P_G/Flow)*(1/Alfa_WAT) #[mJ/cm^2]
    
    if (UVT<minUVT_fit):
        q = -0.46+0.01*WAT_1cm
        N = 96-UVT
    else:
        q = TUF3+TUF4*WAT_1cm
        N = n_max+TUF2*(WAT_1cm-WAT1)**2
    
    if (TAD < TAD0):
        TAD_TAD0 = 1
    else:
        TAD_TAD0 = 0
        
    if (TAD<TAD_h):
        TUF1_TAD1 = TUF1*TAD
    else:
        TUF1_TAD1 = TUF1*TAD_h

    
    TUF = q+(1-q)*((TAD_TAD0 *((TAD0-TAD)/TAD0))**2)**N-TUF1_TAD1
    
    RED = TUF*TAD    

    return round(RED,1)

def HeadLoss(Flow,NLamps):
    
    #dP[bar]=10*Cflow*Flow^2
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    if NLamps == 1:
        return round(HeadLossFactor*(C_Flow_SL*Flow**2)/100,2)
    if NLamps == 2:
        return round(HeadLossFactor*(C_Flow_DL*Flow**2)/100,2)
    