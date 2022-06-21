# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 09:43:16 2020

File for RZB-300-1X Dose Calculator - single module of 2 lamps
@author: Mike
"""
from math import log as ln,exp as exp

# General Formula:
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*(1/(LN(100/UVT)))^γ
# TUF(Q,UVT,D1Log,ρ)=A*(Q^B)*(D1Log^C)*EXP(D*(UVT/100)))


# Dose Coefficents
# 2 lamps:
Z1 = 1.73388373339374
alfa2L = 0.793100554872894
beta2L = 0.84248663116176
gama2L = 0.654305893279355

A1 = 0.0696569303096432
B1 = 0.0803790453053116
C1 = 0.11643116418818
D1 = 1.89455003428108

# for lampd different power, when they are running at different drive (unused in general case)
Z2 = 0.395152724682959
alfa1L = 1
beta1L = 1
gama1L = 0.691674473925155

A2 = 0.000121301900463444
B2 = 0.302772713177836
C2 = 0.369722425245504
D2 = 5.91491910054795

LampPower = 4200 #[W]
minFlow = 5#m3h
maxFlow = 1000#m3h

# Logics
"""
P1 = Power-L1 in [%]
P2 = Power-L2 in [%]
Eff1 = Efficiency-L1 in [%]
Eff2 = Efficiency-L2 in [%]
Flow in [m^3/h]
UVT in [%-1cm]
D1Log in [mJ/cm^2] - 1-Log dose for a specific pathogen
NLamps - Number of lamps in total
"""

def RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps):

    def AvgDose(P1,P2,Eff1,Eff2,Flow,UVT): #Calculates Davg value
        return (Z1*(((min(P1*Eff1/100,P2*Eff2/100)/100*LampPower*2)**alfa2L)/(Flow**beta2L))*(1/(ln(100/UVT)))**gama2L)

    def TUF(Flow,UVT,D1Log):
        return (A1*(Flow**B1)*(D1Log**C1)*exp(D1*(UVT/100)))
    
    return round((NLamps/2)*AvgDose(P1,P2,Eff1,Eff2,Flow,UVT)*TUF(Flow,UVT,D1Log),1)


#Flow coefficients

#HeadLossFactor = 0.0101971621298 #converting to cmH2O
HeadLossFactor = 0.01  # To match the values of the old calculator


C_Flow1_11,C_Flow2_11 = 0.01349, 0.28123
C_Flow1_12,C_Flow2_12 = 0.02185, 0.42439
C_Flow1_13,C_Flow2_13 = 0.02843, 0.55116
C_Flow1_14,C_Flow2_14 = 0.0353, 0.84923



def HeadLoss(Flow,NLamps):
    if NLamps == 2:
        return round((C_Flow1_11*Flow**2+C_Flow2_11*Flow)/100*HeadLossFactor,1)
    elif NLamps == 4:
        return round((C_Flow1_12*Flow**2+C_Flow2_12*Flow)/100*HeadLossFactor,1)
    elif NLamps == 6:
        return round((C_Flow1_13*Flow**2+C_Flow2_13*Flow)/100*HeadLossFactor,1)
    elif NLamps == 8:
        return round((C_Flow1_14*Flow**2+C_Flow2_14*Flow)/100*HeadLossFactor,1)
    else:
        return 'Error'
