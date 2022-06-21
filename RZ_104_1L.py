# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 11:43:00 2020

File for RZ104-1L Dose Calculator - single lamp per module

@author: Mike
"""

from math import log as ln

# C-flow [bar/(m^3/hour)^2]
C_Flow_SL = 2.216E-06 #???
C_Flow_DL = 0.0000041 #???
#HeadLossFactor = 1019.72 #bar to cmH2O
HeadLossFactor = 1000  # To match the values of the old calculator


## Dose Coefficents
# RZM-11: - Base
LampPower = 1045 #[W] - 110W/cm for 140mm arc-length lamp
minFlow = 1 #[m3h]
maxFlow = 1000 #[m3h]

minUVT_extended = 1 #[%-1cm]
minUVT = 77.2 #[%-1cm]
maxUVT = 96.6 #[%-1cm]
maxUVT_extended = 99.8 #[%-1cm]
minDrive = 30 #[%]
maxDrive = 100 #[%]
minLeff = 50 #[%]
maxLeff = 100 #[%]
maxLampSpecificPower = 110 #[W/cm]

#constants
TAD0 = 545
TUF0 = -1.063177042876
TUF1 = 0.041843710685
TUF2 = -0.000243971153
TUF_minimum = 0.05

n_coeff_0 = -79.0014768866989
n_coeff_1 = 2.035311447198
n_coeff_2 = -0.012482568638
n_limit = 1.25

L_eff_coeff_0 =	952.8190517
L_eff_coeff_1 =	-53.55370469
L_eff_coeff_2 =	1.116900875
L_eff_coeff_3 =	-0.010254966
L_eff_coeff_4 =	3.50475E-05

NL0 =0.49722026
NL1 = 0.004759352
NL2 = 2.68446E-06
eta_g =	0.128491836
UVT_step = 75
n_delta_ext = 5
q_min = 0.1

eta_coupling = 1
L_react_L_eff_ratio = 3.5
Unit_converter_1 = 1/3.6
Unit_converter_2 = 157.725 #(m3h to MGD)



def RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps): #Here we shall modify for DL - P1,P2 Eff1, Eff2    

   
    # Taking an average power and/or efficiency for 2 lamps:
    P = (P1+P2)/2
    Eff1 = (Eff1+Eff2)/2
    
    NLF = NL0+NL1*P+NL2*P**2
    Eta_UV = eta_g*eta_coupling*(Eff1/100)*NLF
    PQR = (LampPower*(P/100))/Flow
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
        RED = -1 #'Error'
    else:
        RED = TUF*TAD
       
    return round(RED,1)

def HeadLoss(Flow,NLamps):
    
    #dP[bar]=10*Cflow*Flow^2
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    if NLamps == 1:
        return round(HeadLossFactor*(C_Flow_SL*Flow**2)/100,2)
    if NLamps == 2:
        return round(HeadLossFactor*(C_Flow_DL*Flow**2)/100,2)
    