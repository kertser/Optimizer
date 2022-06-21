# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 10:48:13 2020
File for RZM-200 Dose Calculator - simplified

@author: Mike
"""

from math import exp as exp

# General Formula:
# TUF(Q,UVT,D1Log,ρ)=A1*(Q^B1)*(D1Log^C1)*EXP(D1*(UVT/100)))
# Davg(P,Q,UVT)=Z1*((P^α)/(Q^β))*EXP(γ*(UVT/100))

# Dose Coefficents
VF = 1.3 #Validation Factor

Z1 = 0.060339841231047
alfa = 1
beta = 1
gama = 3.37360015072348

A1 = 0.462185705660002
B1 = 0.0749097124175999
C1 = 0.0592308260592836
D1 = 0.0870074638311847 

powerDensity = 171.43#[W/cm]
arcLength = 39.8#[cm]
LampPower = round(powerDensity*arcLength,1) #[W] 171.43 W/cm on 39.8cm arc-length
minFlow = 10#m3h
maxFlow = 1000#m3h

# Logics
"""
P = Power in [%]
Eff1 = Efficiency in [%]
Flow in [m^3/h]
UVT in [%-1cm]
D1Log in [mJ/cm^2] - 1-Log dose for a specific pathogen
NLamps = 1 (single lamp)
"""

def RED(P1,P2,P3,P4,P5,Eff1,Eff2,Eff3,Eff4,Eff5,Flow,UVT,D1Log,NLamps):
    
    #This averaging is temporary and shall be changed on a more complicated model
    P = (P1+P2+P3+P4+P5)/5
    Eff = (Eff1+Eff2+Eff3+Eff4+Eff5)/5

    def AvgDose(P,Eff,Flow,UVT): #Calculates Davg value        
        return VF*Z1*(((arcLength*powerDensity*NLamps)*(P/100)*(Eff/100))**alfa)/(Flow**beta)*exp(gama*(UVT/100))

    def TUF(Flow,UVT,D1Log):        
        return min(A1*(Flow**B1)*(D1Log**C1)*exp(D1*(UVT/100)),1) #TUF<1 always
    
    return round(AvgDose(P,Eff,Flow,UVT)*TUF(Flow,UVT,D1Log),1)

#Flow coefficients

HeadLossFactor = 0.0101971621298 #converting from Pa to cmH2O
C_Flow1 = 0.11049
C_Flow2 = 2.03679

def HeadLoss(Flow,NLamps):
    if NLamps == 2: #this is a default one
        return round(HeadLossFactor/1000*(C_Flow1*Flow**2+C_Flow2*Flow),2)
    else:
        return 'Error'
