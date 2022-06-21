# -*- coding: utf-8 -*-
"""
File for RS-104 Dose Calculator - single lamp per module
Created on Tue Nov 24 13:44:36 2020

@author: Mike
"""

from math import exp as exp

# General Formula:
# TUF(Q,UVT,D1Log,ρ)=A*(Q^B)*(D1Log^C)*EXP(D*(UVT/100)))
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*EXP(γ*(UVT/100))


# Dose Coefficients

Z1 = 0.00013676525437778
alfa = 1.82647844522826
beta = 1
gama = 8.92498098157656

A1 = 0.264395667227658
B1 = 0.0913821393032035
C1 = 0.0712062582569228
D1 = 0.777359750748686

LampPower = 1050 #[W]
minFlow = 10#m3h
maxFlow = 500#m3h

# Logics
"""
P = Power in [%]
Eff1 = Efficiency in [%]
Flow in [m^3/h]
UVT in [%-1cm]
D1Log in [mJ/cm^2] - 1-Log dose for a specific pathogen
NLamps = 1 (single lamp)
"""

def RED(P,Eff,Flow,UVT,D1Log,NLamps):

    def AvgDose(P,Eff,Flow,UVT): #Calculates Davg value        
        return Z1*(((P*Eff/100)**alfa)/(Flow**beta))*exp(gama*(UVT/100))

    def TUF(Flow,UVT,D1Log):
        return min(A1*(Flow**B1)*(D1Log**C1)*exp(D1*(UVT/100)),1) #TUF<1 always
    
    return round(AvgDose(P,Eff,Flow,UVT)*TUF(Flow,UVT,D1Log),1)

#Flow coefficients

#HeadLossFactor = 0.0101971621298 #converting to cmH2O? Needed?
C_Flow1 = 4.62E-06
C_Flow2 = 2*4.62E-06 #actually not known yet

def HeadLoss(Flow,NLamps):
    if (NLamps == 1) | (NLamps == 3): #this is a default one for single lamp per branch
        return round((C_Flow1*(Flow**2)),1)     
    elif (NLamps == 2) | (NLamps == 4): #to be changed later
        return round((C_Flow2*(Flow**2)),1)     
