# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 09:43:16 2020

File for EP-600 Dose Calculator - single module of 2-4 lamps
@author: Mike
"""
from math import log as ln,exp as exp

## General Formula:
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*(1/(LN(100/UVT)))^γ
# TUF(Q,UVT,D1Log,ρ)=A*LN((B*Q)*(1/ρ)*(D1Log^C)*EXP(-D*(100/UVT)))
# Schematic lamp placement:
# <<(L1) (L3)>>
# <<(L2) (L4)>>


## Dose Coefficents
# EP-4L: - Base
Z1 = 1.22061316462651
alfa4L = 1
beta4L = 1
gama4L = 0.873010931124947

A1 = 0.1162607858509
B1 = 0.371030699431417
C1 = 1.22077503287731
D1 = 3.73561624639757

# EP-4L: Single lamp "lead"
Z1_lead = 0.404420945319522
alfa4L_lead = 1
beta4L_lead = 1
gama4L_lead = 0.83535465366486

A1_lead = 0.148510660115206
B1_lead = 0.0123403695243628
C1_lead = 0.87263620883785
D1_lead = 1.91929195322967

# EP-4L: Single lamp "lag"
Z1_lag = 0.300850569870035
alfa4L_lag = 1
beta4L_lag = 1
gama4L_lag = 0.912852990058308

A1_lag = 0.147655833107015
B1_lag = 0.00492768115732762
C1_lag = 0.942395843866067
D1_lag = 1.21088165728498

# EP-2L: Base
Z2 = 0.612763221395606
alfa2L = 1
beta2L = 1
gama2L = 0.812375160491567

A2 = 0.128121865880793
B2 = 1.36377755754535
C2 = 1.0721706738148
D2 = 4.17084478397804

LampPower = 12000 #[W]
minFlow = 50#m3h
maxFlow = 2000#m3h

# Logics
"""
P1 = Power-L1 in [%]
P2 = Power-L2 in [%]
P3 = Power-L3 in [%]
P4 = Power-L4 in [%]
Eff1 = Efficiency-L1 in [%]
Eff2 = Efficiency-L2 in [%]
Eff3 = Efficiency-L3 in [%]
Eff4 = Efficiency-L4 in [%]
Flow in [m^3/h]
UVT in [%-1cm]
D1Log in [mJ/cm^2] - 1-Log dose for a specific pathogen
NLamps - Number of lamps in total (2 or 4)
"""

def RED(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT,D1Log,NLamps):

    def AvgDose(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT): #Calculates Davg value
        if NLamps == 4:
            DAvgBase = (Z1*((((min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4)/100)/100*LampPower)**alfa4L)/(Flow**beta4L))*(1/(ln(100/UVT)))**gama4L)
            DAvgL1 = Z1_lead*(((((P1*Eff1-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4))/100)/100*LampPower)**alfa4L_lead)/(Flow**beta4L_lead))*(1/(ln(100/UVT)))**gama4L_lead
            DAvgL2 = Z1_lead*(((((P2*Eff2-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4))/100)/100*LampPower)**alfa4L_lead)/(Flow**beta4L_lead))*(1/(ln(100/UVT)))**gama4L_lead
        elif NLamps == 2:
            DAvgBase = (Z2*((((min(P1*Eff1,P2*Eff2)/100)/100*LampPower)**alfa2L)/(Flow**beta2L))*(1/(ln(100/UVT)))**gama2L)
            DAvgL1 = Z1_lead*(((((P1*Eff1-min(P1*Eff1,P2*Eff2))/100)/100*LampPower)**alfa4L_lead)/(Flow**beta4L_lead))*(1/(ln(100/UVT)))**gama4L_lead
            DAvgL2 = Z1_lead*(((((P2*Eff2-min(P1*Eff1,P2*Eff2))/100)/100*LampPower)**alfa4L_lead)/(Flow**beta4L_lead))*(1/(ln(100/UVT)))**gama4L_lead
        
        DavgL3 = Z1_lag*(((((P3*Eff3-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4))/100)/100*LampPower)**alfa4L_lag)/(Flow**beta4L_lag))*(1/(ln(100/UVT)))**gama4L_lag
        DavgL4 = Z1_lag*(((((P4*Eff4-min(P1*Eff1,P2*Eff2,P3*Eff3,P4*Eff4))/100)/100*LampPower)**alfa4L_lag)/(Flow**beta4L_lag))*(1/(ln(100/UVT)))**gama4L_lag
        return DAvgBase,DAvgL1,DAvgL2,DavgL3,DavgL4
    
    def TUF(Flow,UVT,D1Log):
        #return (A1*(Flow**B1)*(D1Log**C1)*exp(D1*(UVT/100)))
        if NLamps == 4:
            TUFBase = A1*ln((B1*Flow)*(D1Log**C1)*exp(-D1*(100/UVT)))
        elif NLamps ==2:
            TUFBase = A2*ln((B2*Flow)*(D1Log**C2)*exp(-D2*(100/UVT)))
        
        if A1_lead*ln((B1_lead*Flow)*(D1Log**C1_lead)*exp(-D1_lead*(100/UVT))) < 0:
            TUF_L1 = 0
            TUF_L2 = 0
        else:
            TUF_L1 = A1_lead*ln((B1_lead*Flow)*(D1Log**C1_lead)*exp(-D1_lead*(100/UVT)))
            TUF_L2 = A1_lead*ln((B1_lead*Flow)*(D1Log**C1_lead)*exp(-D1_lead*(100/UVT)))
            
        if A1_lag*ln((B1_lag*Flow)*(D1Log**C1_lag)*exp(-D1_lag*(100/UVT))) < 0:
            TUF_L3 = 0
            TUF_L4 = 0
        else:
            TUF_L3 = A1_lag*ln((B1_lag*Flow)*(D1Log**C1_lag)*exp(-D1_lag*(100/UVT)))
            TUF_L4 = A1_lag*ln((B1_lag*Flow)*(D1Log**C1_lag)*exp(-D1_lag*(100/UVT)))
        
        return TUFBase,TUF_L1,TUF_L2,TUF_L3,TUF_L4
            
    
    return round(AvgDose(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT)[0]*TUF(Flow,UVT,D1Log)[0],1) #Returns RED Base - not taking into account non-equal lamp power
        
    # return differentiated RED value for non-equal lamps - will be done later-on

##Flow coefficients
HeadLossFactor = 0.000101971621298 #converting to cmH2O
C_Flow1_4,C_Flow2_4 = 0.000522558681014014,0.161453947864067 # 2-lamps system
C_Flow1_2,C_Flow2_2 = 0.000396304728986223,0.107774905178786 # 4-lamps system

def HeadLoss(Flow,NLamps):
    if NLamps == 2:
        return round((C_Flow1_2*Flow**2+C_Flow2_2*Flow)*HeadLossFactor,1)
    elif NLamps == 4:
        return round((C_Flow1_4*Flow**2+C_Flow2_4*Flow)*HeadLossFactor,1)
    else:
        return 'Error'
