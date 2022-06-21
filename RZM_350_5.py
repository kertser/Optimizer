# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:03:05 2020

File for RZM-1/2 Dose Calculator - single or dual module with 8 lamps per module

@author: Mike
"""

from math import exp as exp
from statistics import mean as avg

## General Formula:
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*EXP(γ*(UVT/100))
# TUF(Q,UVT,D1Log,ρ)=A*(Q^B)*(D1Log^C)*EXP(D*(UVT/100)))
# Schematic lamp placement:
"""
2		8X
	1	
3		7X
	5	
4		6X
"""
Dose_VF = {'Regular': 1.3,
           'Marine' : 1.7
          }

# C-flow [bar/(m^3/hour)^2]
C_Flow1_11 = 0.01318957
C_Flow2_11 = 0.90015788
C_Flow1_12 = 0.01318957
C_Flow2_12 = 0.90015788

## Dose Coefficents
# RZM-11: - Base
LampPower = 12000 #[W]
minFlow = 50#m3h
maxFlow = 1000#m3h

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

A1L = 0.0029330354013571
B1L = 0.559110762585846
C1L = 0.551485708959622
D1L = 0.191231787550938

# L2:
Z_2L = 0.0460004215693581
alfa_2L = 1
beta_2L = 1
gama_2L = 3.47822521230922

A2L = 0.00140897975230076
B2L = 0.61078312588621
C2L = 0.635391483015667
D2L = 0

# L3:
Z_3L = 0.0527635268600559
alfa_3L = 1
beta_3L = 1
gama_3L = 3.92565591029147

A3L = 0.00769435233290522
B3L = 0.404441425629256
C3L = 0.334340940578571
D3L = 1.40297958816377

# L4: - like L2 (symmetry)
Z_4L = Z_2L
alfa_4L = alfa_2L
beta_4L = beta_2L
gama_4L = gama_2L

A4L = A2L
B4L = B2L
C4L = C2L
D4L = D2L

# L5: - like L1 (symmetry)
Z_5L = Z_1L
alfa_5L = alfa_1L
beta_5L = beta_1L
gama_5L = gama_1L

A5L = A1L
B5L = B1L
C5L = C1L
D5L = D1L

# L7:
Z_7L = 0.0509388164423499
alfa_7L = 1
beta_7L = 1
gama_7L = 3.61098810710419

A7L = 0.027549827752193
B7L = 0.233436748808719
C7L = 0.272108471414808
D7L = 1.36580422402348

# L8:
Z_8L = 0.0537133653112592
alfa_8L = 1
beta_8L = 1
gama_8L = 3.04568395486429

A8L = 0.00171727284713336
B8L = 0.642189398962404
C8L = 0.591566437213566
D8L = 0

# L6: - like L8 (symmetry)
Z_6L = Z_8L
alfa_6L = alfa_8L
beta_6L = beta_8L
gama_6L = gama_8L

A6L = A8L
B6L = B8L
C6L = C8L
D6L = D8L

def RED(P1,P2,P3,P4,P5,P6,P7,P8,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Eff8,Flow,UVT,D1Log,NLamps):
    if NLamps == 5:
        P6=0
        P7=0
        P8=0
        
    Davg_base = Z_base*((((avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8])/100)/100*LampPower)**alfa_base)/(Flow**beta_base))*exp(gama_base*UVT/100)
    TUF_base = A_base*(Flow**B_base)*(D1Log**C_base)*exp(D_base*(UVT/100))
    if TUF_base > 1: TUF_base = 1 #Prevent the situation, where base Track Uniformity is larger than 1
    
    Davg1L = Z_1L*(((((P1*Eff1-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_1L)/(Flow**beta_1L))*exp(gama_1L*(UVT/100))
    TUF1L = A1L*(Flow**B1L)*(D1Log**C1L)*exp(D1L*(UVT/100))
    if TUF1L<0:TUF1L = 0
        
    Davg2L = Z_2L*(((((P2*Eff2-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_2L)/(Flow**beta_2L))*exp(gama_2L*(UVT/100))
    TUF2L = A2L*(Flow**B2L)*(D1Log**C2L)*exp(D2L*(UVT/100))
    if TUF2L<0:TUF1L = 0
    
    Davg3L = Z_3L*(((((P3*Eff3-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_3L)/(Flow**beta_3L))*exp(gama_3L*(UVT/100))
    TUF3L = A3L*(Flow**B3L)*(D1Log**C3L)*exp(D3L*(UVT/100))
    if TUF3L<0:TUF3L = 0
    
    Davg4L = Z_4L*(((((P4*Eff4-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_4L)/(Flow**beta_4L))*exp(gama_4L*(UVT/100))
    TUF4L = A4L*(Flow**B4L)*(D1Log**C4L)*exp(D4L*(UVT/100))
    if TUF4L<0:TUF4L = 0
        
    Davg5L = Z_5L*(((((P5*Eff5-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_5L)/(Flow**beta_5L))*exp(gama_5L*(UVT/100))
    TUF5L = A5L*(Flow**B5L)*(D1Log**C5L)*exp(D5L*(UVT/100))
    if TUF5L<0:TUF5L = 0
    
    Davg6L = Z_6L*(((((P6*Eff6-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_6L)/(Flow**beta_6L))*exp(gama_6L*(UVT/100))
    TUF6L = A6L*(Flow**B6L)*(D1Log**C6L)*exp(D6L*(UVT/100))
    if TUF6L<0:TUF6L = 0
    
    Davg7L = Z_7L*(((((P7*Eff7-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_7L)/(Flow**beta_7L))*exp(gama_7L*(UVT/100))
    TUF7L = A7L*(Flow**B7L)*(D1Log**C7L)*exp(D7L*(UVT/100))
    if TUF7L<0:TUF7L = 0
    
    Davg8L = Z_8L*(((((P8*Eff8-avg([P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4,P5*Eff5,P6*Eff6,P7*Eff7,P8*Eff8]))/100)/100*LampPower)**alfa_8L)/(Flow**beta_8L))*exp(gama_8L*(UVT/100))
    TUF8L = A8L*(Flow**B8L)*(D1Log**C8L)*exp(D8L*(UVT/100))
    if TUF8L<0:TUF8L = 0
    
    RED_Base = Davg_base*TUF_base
    RED = RED_Base + (Davg1L*TUF1L + Davg2L*TUF2L + Davg3L*TUF3L + Davg4L*TUF4L + Davg5L*TUF5L+ Davg6L*TUF6L + Davg7L*TUF7L + Davg8L*TUF8L)
    
    if NLamps == 5:
        return round(RED,1)
    elif NLamps == 10: #This is a simplification, but should be valid in this stage
        return round(2*RED,1)

def HeadLoss(Flow,NLamps):
    
    # HeadLoss[cmH2O] = HeadLossFactor*C_Flow*Flow^2
    HeadLossFactor = 0.01 # To match the old calculator
    if NLamps == 5:
        return round(HeadLossFactor*(C_Flow1_11*Flow**2+C_Flow2_11*Flow)/100,2)
    if NLamps == 10:
        return round(HeadLossFactor*2*(C_Flow1_12*Flow**2+C_Flow2_12*Flow)/100,2) # shall be changed later on
    