# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 09:22:00 2020

File for RZ-163-UHP Dose Calculator

@author: Mike
This is an updated version for UHP with fixed UVT254>96[%-1cm]
"""
from math import log10 as log, log as ln

## Dose Coefficents

AH = 6.68586909613977
BH = 0.931505620533178
CH = -0.762243989524516
DH = 2.45902603509457
EH = -0.904980935576177
FH = 1.3572137958403
GH = -5.64328172563936
HH = -0.924600741065049
IH = -27.9378034190639
JH = 49.2460500117299
KH = 0.125320453051158
LH = 1.30623706193718
MH = -13.3376614904183
NH = 1.20023530288472

AL = 7.3638E+00
BL = 1.1023E+00
CL = -1.4006E+01
DL = 8.4624E+01
EL = -3.1899E-01
FL = 0.0000E+00
GL = -1.1846E+00
HL = -2.6847E+00
IL = -4.6157E+01
JL = 6.6242E+01
KL = 6.0676E-01
LL = 4.7538E+00
ML = -1.9015E+01
NL = 5.1284E-01

BRED_fixed = 1.2428 #Fixed BRED for any UVT - for 3-log?
STDEV = 6.2103# standard deviation for the calculated
tVal = 1.9771# t-value for the calculated

LampPower = 3000 #[W]
minFlow = 10#m3h
maxFlow = 3000#m3h

#General scheme: 
"""
RED_HL=10^A*(P/100)^(B+C*A254+D*A254^2)*Q^(E+F*A254+G*A254^2)*(1/A254)^(H+I*A254+J*A254^2)*UVS^(K+L*A254+M*A254^2)*NOL^N													
RED_LL=10^A'*(P/100)^(B'+C'*A215+D'*A215^2)*Q^(E'+F'*A215+G'*A215^2)*(1/A215)^(H'+I'*A215+J'*A215^2)*UVS^(K'+L'*A215+M'*A215^2)*NOL^N'													
RED = RED_LL+RED_HL
abs = -LOG(UVT/100)
UVS = D1Log average inactivation
N = number of lamps
Flow units - [m3/h] - in this calculator converted to us_gpm for calculation
"""

def RED(P,Status,Flow,UVT254,UVT215,D1Log,NLamps):


    A254 = -log(UVT254/100)
    A215 = -log(UVT215/100)
    Flow = Flow*4.402868# in this specific case it is a conversion to gpm

    if UVT254 < 96:

        RED_HL=10**AH*((Status/100)*(P/100))**(BH+CH*A254+DH*A254**2)*Flow**(EH+FH*A254+GH*A254**2)*(1/A254)**(HH+IH*A254+JH*A254**2)*D1Log**(KH+LH*A254+MH*A254**2)*NLamps**NH
        RED_LL=10**AL*((Status/100)*(P/100))**(BL+CL*A215+DL*A215**2)*Flow**(EL+FL*A215+GL*A215**2)*(1/A215)**(HL+IL*A215+JL*A215**2)*D1Log**(KL+LL*A215+ML*A215**2)*NLamps**NL
        RED = RED_HL+RED_LL

    else:
        A254_96 = -log(96/100)
        A215_96 = -log(96/100)

        RED_HL96 = 10**AH*((Status/100)*(P/100))**(BH+CH*A254_96+DH*A254_96**2)*Flow**(EH+FH*A254_96+GH*A254_96**2)*(1/A254_96)**(HH+IH*A254_96+JH*A254_96**2)*D1Log**(KH+LH*A254_96+MH*A254_96**2)*NLamps**NH
        RED_LL96=10**AL*((Status/100)*(P/100))**(BL+CL*A215_96+DL*A215_96**2)*Flow**(EL+FL*A215_96+GL*A215_96**2)*(1/A215_96)**(HL+IL*A215_96+JL*A215_96**2)*D1Log**(KL+LL*A215_96+ML*A215_96**2)*NLamps**NL

        RED96 = round((RED_HL96+RED_LL96),2)
        RED = RED96 * (1.3**(UVT254-96))
    
    return round(RED,1)

def VF_RED(RED): # consider to be changed...
    #fixed BRED, bias at 3-log, conservative
    UIN=STDEV*tVal/(RED)
    #VF=(RED)/((1+UIN)*BRED_fixed)
    VF=((1+UIN)*BRED_fixed)
    
    return round(RED/VF,1)

def VF_RED_cripto(RED,UVT,LI):
    
    log_abc = [0.5,1,1.5,2,2.5,3,3.5,4] # Choose the desired LI
    # required_dose = [1.6,2.5,3.9,5.8,8.5,12,15,22] #Required per LI

    ## These are a,b,c constants to calculate the BRED per log-inactivation of target (Criptosporidium)
    a = [-7.956807,-14.617616,-12.844755,-10.18365,-7.038886,-4.375281,-3.261568,-0.060176]
    b = [4.896899,7.185111,5.999709,4.46189,2.957013,1.766574,1.277332,0.12976]
    c = [0.993118,1.031131,1.071125,1.090283,1.083221,1.065181,1.053526,1.019059]
    A254 = -ln(UVT/100)
    
    a1,b1,c1 = a[log_abc.index(LI)],b[log_abc.index(LI)],c[log_abc.index(LI)]
    
    UIN=STDEV*tVal/(RED)
    BRED = a1*A254**2+b1*A254+c1
    
    VF=((1+UIN)*BRED)
    return round(RED/VF,1) #Return the credited dose after the validation factor

#HeadLossFactor = 1019.72 #converting bar to cmH2O
HeadLossFactor = 1000  # To match the values of the old calculator

# C-flow [bar/(m^3/hour)^2]
C_Flow_1L = 2.61E-07
C_Flow_2L = 5.31E-07
C_Flow_3L = 7.35E-07
C_Flow_4L = 9.14E-07

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
    