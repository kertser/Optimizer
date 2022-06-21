# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 09:18:21 2020
File for RZ163-1L Dose Calculator - single lamp per module

@author: Mike
"""

from math import log as ln

# C-flow [bar/(m^3/hour)^2]
C_Flow_1L = 2.61E-07
C_Flow_2L = 5.31E-07
C_Flow_3L = 7.35E-07
C_Flow_4L = 9.14E-07

# HeadLossFactor = 1019.72 #bar to cmH2O
HeadLossFactor = 1000  # To match the values of the old calculator


## Dose Coefficents
# RZM-11: - Base
LampPower = 2325 #[W] - 300W/cm for 140mm arc-length lamp
minFlow = 4 #[m3h]
maxFlow = 2000 #[m3h]

minUVT_extended = 1 #[%-1cm]
minUVT = 79 #[%-1cm]
maxUVT = 96.6 #[%-1cm]
maxUVT_extended = 99.8 #[%-1cm]
minDrive = 25 #[%] It was 30%
maxDrive = 100 #[%]
minLeff = 50 #[%]
maxLeff = 100 #[%]
maxLampSpecificPower = 150 #[W/cm]

#constants
TAD0 = 500
TUF0 = 4.0112222222
TUF1 = -0.0882222222
TUF2 = 0.0005555556
TUF_minimum = 0.05

n_coeff_0 = 18.9956903731179
n_coeff_1 = -0.150039130073
n_coeff_2 = -0.000377119685
n_limit = 1

L_eff_coeff_0 =	1271.8934153816
L_eff_coeff_1 =	-72.4457478963446
L_eff_coeff_2 =	1.52438553120442
L_eff_coeff_3 =	-0.014089865266356
L_eff_coeff_4 =	0.000048456108395

NL0 = 0.122959698122207
NL1 = 0.015753059974049
NL2 = -0.000069826569553
eta_g =	0.1161
UVT_step = 75
n_delta_ext = 16
q_min = 0.1

eta_coupling = 1
L_react_L_eff_ratio = 3.5
Unit_converter_1 = 1/3.6
Unit_converter_2 = 157.725 #(m3h to MGD)



def RED(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT,D1Log,NLamps): #Here we shall modify for ML - P1,P2,P3,P4 Eff1,Eff2,Eff3,Eff4    

   
    # Taking an average power and/or efficiency for multiple lamps:
    P = (P1+P2+P3+P4)/4
    Eff1 = (Eff1+Eff2+Eff3+Eff4)/4
    
    NLF = NL0+NL1*P+NL2*P**2
    Eta_UV = eta_g*eta_coupling*(Eff1/100)*NLF
    PQR = LampPower/Flow
    L_eff_step = L_eff_coeff_0+L_eff_coeff_1*UVT_step+L_eff_coeff_2*UVT_step**2+L_eff_coeff_3*UVT_step**3+L_eff_coeff_4*UVT_step**4
    alfa_step =-ln(UVT_step/100)
    alfa = -ln(UVT/100)
    L_eff_scale = L_eff_step*alfa_step
    
    if (UVT>UVT_step):
        L_eff = L_eff_coeff_0+L_eff_coeff_1*UVT+L_eff_coeff_2*UVT**2+L_eff_coeff_3*UVT**3+L_eff_coeff_4*UVT**4
    else: 
        L_eff = (L_eff_scale/alfa)
    
    NLF = NL0+NL1*P+NL2*P**2
        
    TAD = (1/Unit_converter_1)*Eta_UV*PQR*L_eff#[mJ/cm^2]
    
    q_step = TUF0+TUF1*UVT_step+TUF2*UVT_step**2
    q_slope = (q_min-q_step)/UVT_step
    
    if (UVT > UVT_step):
        q = TUF0+TUF1*UVT+TUF2*UVT**2
    else:
        q = q_step+q_slope*(UVT_step-UVT)
    
    n_step = n_coeff_0+n_coeff_1*UVT_step+n_coeff_2*UVT_step**2
    n_slope = n_delta_ext/UVT_step
    
    if (UVT > UVT_step):
        n_intermediate = n_coeff_0+n_coeff_1*UVT+n_coeff_2*UVT**2
    else:
        n_intermediate = n_step+n_slope*(UVT_step-UVT)
        
    if (n_intermediate > n_limit):
        n = n_intermediate
    else:
        n = n_limit
    
    TAD_TAD0 = ((TAD0-TAD)/TAD0)**2
    if (TAD <= TAD0):
        TAD_N = TAD_TAD0**n
    else:
        TAD_N = 0
    
    TUF_inter=q+(1-q)*TAD_N
    
    if (TUF_inter < TUF_minimum):
        TUF = TUF_minimum
    else:
        TUF = TUF_inter

    if ((UVT < minUVT_extended) | (UVT > maxUVT_extended) | (P < minDrive) | (Flow < minFlow) | (Eff1 < minLeff)):
        RED = -1# 'Error' 
    else:
        RED = TUF*TAD
   
    return round(RED,1)

def HeadLoss(Flow,NLamps):
    
    #dP[bar]=10*Cflow*Flow^2
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    if NLamps == 1:
        return round(HeadLossFactor*(C_Flow_1L*Flow**2)/100,2)
    if NLamps == 2:
        return round(HeadLossFactor*(C_Flow_2L*Flow**2)/100,2)
    if NLamps == 3:
        return round(HeadLossFactor*(C_Flow_3L*Flow**2)/100,2)
    if NLamps == 4:
        return round(HeadLossFactor*(C_Flow_4L*Flow**2)/100,2)