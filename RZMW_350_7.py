# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 10:48:13 2020
File for RZM-350 Dose Calculator - simplified

@author: Mike
"""

from math import exp as exp

# General Formula:
# TUF(Q,UVT,D1Log,ρ)=A1*(Q^B1)*(D1Log^C1)*EXP(D1*(UVT/100)))
# Davg(P,Q,UVT)=Z1*((P^α)/(Q^β))*EXP(γ*(UVT/100))

# Dose Coefficents
VF = 0.86 #Validation Factor
DoseCorrectionFactor = 1.21

Z1 = 0.0282245386468839
alfa = 1
beta = 1
gama = 4.516177254185

A1 = 0.465456286359808
B1 = 0.0540907147468616
C1 = 0.0504334999703928
D1 = 0.22829306629508 

powerDensity = 171.43#[W/cm]
arcLength = 70#[cm]
LampPower = round(powerDensity*arcLength,1) #[W] 171.43 W/cm on 70cm arc-length
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

def RED(P1,P2,P3,P4,P5,P6,P7,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Flow,UVT,D1Log,NLamps):
    
    #This averaging is temporary and shall be changed on a more complicated model
    P = (P1+P2+P3+P4+P5+P6+P7)/7
    Eff = (Eff1+Eff2+Eff3+Eff4+Eff5+Eff6+Eff7)/7

    def AvgDose(P,Eff,Flow,UVT): #Calculates Davg value        
        return VF*Z1*(((arcLength*powerDensity*NLamps)*(P/100)*(Eff/100))**alfa)/(Flow**beta)*exp(gama*(UVT/100))

    def TUF(Flow,UVT,D1Log):        
        return min(A1*(Flow**B1)*(D1Log**C1)*exp(D1*(UVT/100)),1) #TUF<1 always
    
    return round(AvgDose(P,Eff,Flow,UVT)*TUF(Flow,UVT,D1Log),1)*DoseCorrectionFactor

#Flow coefficients

HeadLossFactor = 0.0101971621298 #converting from Pa to cmH2O
C_Flow1 = 0.11049 #!!! Change
C_Flow2 = 2.03679 #!!! Change

def HeadLoss(Flow,NLamps):
    if NLamps == 7: #this is a default one
        return round(HeadLossFactor/1000*(C_Flow1*Flow**2+C_Flow2*Flow),2)
    else:
        return 'Error'
