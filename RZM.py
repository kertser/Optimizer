# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:03:05 2020

File for RZM-1/2 Dose Calculator - single or dual module with 8 lamps per module

@author: Mike
"""

from math import exp as exp

## General Formula:
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*EXP(γ*(UVT/100))
# TUF(Q,UVT,D1Log,ρ)=A*(Q^B)*(D1Log^C)*EXP(D*(UVT/100)))
# Schematic lamp placement:
"""
1		2
	3	
4		5
	6	
7		8
"""

# C-flow [bar/(m^3/hour)^2]
C_Flow1_11 = 0.01318957
C_Flow2_11 = 0.90015788
C_Flow1_12 = 0.01318957
C_Flow2_12 = 0.90015788

## Dose Coefficents
# RZM-11: - Base
LampPower = 12000 #[W]

Z_base = 0.610173974032547
alfa_base = 1
beta_base = 1
gama_base = 2.80917232123146


A_base = 0.388730011750849
B_base = 0.0553499298263537
C_base = 0.0522199065009149
D_base = 0.505744414519666

# L1:
Z_1L = 0.0460004215693581
alfa_1L = 1
beta_1L = 1
gama_1L = 3.47822521230922

A1L = 0.00140897975230076
B1L = 0.61078312588621
C1L = 0.635391483015667
D1L = 0

# L2:
Z_2L = 0.0537133653112592
alfa_2L = 1
beta_2L = 1
gama_2L = 3.04568395486429

A2L = 0.00171727284713336
B2L = 0.642189398962404
C2L = 0.591566437213566
D2L = 0

# L3:
Z_3L = 0.0460004215693581
alfa_3L = 1
beta_3L = 1
gama_3L = 3.47822521230922

A3L = 0.0029330354013571
B3L = 0.559110762585846
C3L = 0.551485708959622
D3L = 0.191231787550938

# L4:
Z_4L = 0.0527635268600559
alfa_4L = 1
beta_4L = 1
gama_4L = 3.92565591029147

A4L = 0.00769435233290522
B4L = 0.404441425629256
C4L = 0.334340940578571
D4L = 1.40297958816377

# L5:
Z_5L = 0.0509388164423499
alfa_5L = 1
beta_5L = 1
gama_5L = 3.61098810710419

A5L = 0.027549827752193
B5L = 0.233436748808719
C5L = 0.272108471414808
D5L = 1.36580422402348

def RED(P1,P2,P3,P4,P5,P6,P7,P8,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Eff8,Flow,UVT,D1Log,NLamps):
    # if NLamps == 8:
    Davg_base = Z_base*((((min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8)/100)/100*LampPower)**alfa_base)/(Flow**beta_base))*exp(gama_base*UVT/100)
    TUF_base = A_base*(Flow**B_base)*(D1Log**C_base)*exp(D_base*(UVT/100))
    
    Davg1L = Z_1L*(((((P1*Eff1-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_1L)/(Flow**beta_1L))*exp(gama_1L*(UVT/100))
    TUF1L = A1L*(Flow**B1L)*(D1Log**C1L)*exp(D1L*(UVT/100))
    if TUF1L<0:TUF1L = 0
        
    Davg2L = Z_2L*(((((P2*Eff2-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_2L)/(Flow**beta_2L))*exp(gama_2L*(UVT/100))
    TUF2L = A2L*(Flow**B2L)*(D1Log**C2L)*exp(D2L*(UVT/100))
    if TUF2L<0:TUF1L = 0
    
    Davg3L = Z_3L*(((((P3*Eff3-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_3L)/(Flow**beta_3L))*exp(gama_3L*(UVT/100))
    TUF3L = A3L*(Flow**B3L)*(D1Log**C3L)*exp(D3L*(UVT/100))
    if TUF3L<0:
        TUF3L = 0
    
    Davg4L = Z_4L*(((((P4*Eff4-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_4L)/(Flow**beta_4L))*exp(gama_4L*(UVT/100))
    TUF4L = A4L*(Flow**B4L)*(D1Log**C4L)*exp(D4L*(UVT/100))
    if TUF4L<0:TUF4L = 0
        
    Davg5L = Z_5L*(((((P5*Eff5-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_5L)/(Flow**beta_5L))*exp(gama_5L*(UVT/100))
    TUF5L = A5L*(Flow**B5L)*(D1Log**C5L)*exp(D5L*(UVT/100))
    if TUF5L<0:TUF5L = 0
    
    Davg6L = Z_3L*(((((P6*Eff6-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_3L)/(Flow**beta_3L))*exp(gama_3L*(UVT/100))
    TUF6L = A3L*(Flow**B3L)*(D1Log**C3L)*exp(D3L*(UVT/100))
    if TUF6L<0:TUF6L = 0
    
    Davg7L = Z_1L*(((((P7*Eff7-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_1L)/(Flow**beta_1L))*exp(gama_1L*(UVT/100))
    TUF7L = A1L*(Flow**B1L)*(D1Log**C1L)*exp(D1L*(UVT/100))
    if TUF7L<0:TUF7L = 0
    
    Davg8L = Z_2L*(((((P8*Eff8-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8))/100)/100*LampPower)**alfa_2L)/(Flow**beta_2L))*exp(gama_2L*(UVT/100))
    TUF8L = A2L*(Flow**B2L)*(D1Log**C2L)*exp(D2L*(UVT/100))
    if TUF8L<0:TUF8L = 0
    
    RED_Base = Davg_base*TUF_base
    RED = RED_Base + Davg1L*TUF1L + Davg2L*TUF2L + Davg3L*TUF3L + Davg4L*TUF4L + Davg5L*TUF5L+ Davg6L*TUF6L + Davg7L*TUF7L + Davg8L*TUF8L
    
    if NLamps == 8:
        return round(RED,1)
    elif NLamps == 16: #This is a simplification, but should be valid in this stage
        return round(2*RED,1)

def HeadLoss(Flow,NLamps):
    
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    if NLamps == 8:
        return round((C_Flow1_11*Flow**2+C_Flow2_11*Flow)/100,2)
    if NLamps == 16:
        return round(2*(C_Flow1_12*Flow**2+C_Flow2_12*Flow)/100,2) # shall be changed later on
    