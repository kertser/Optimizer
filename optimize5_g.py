# PQR optimizer
from scipy.optimize import shgo
import numpy as np
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
from opt_config import NLamps
import inspect
import sys

System = 'RZ-300-11'
targetRED = 40 # [mJ/cm^2]

minP = 40
maxP = 100
minFlow = 150
maxFlow = 1000
minUVT = 25
maxUVT = 98

#def RED(P,Q,UVT,Status,module):
def RED(**kwargs):
    try:
        modulename = __import__(kwargs['module'])
    except ImportError:
        print('No module found')
        sys.exit(1)

    moduleargs = inspect.getfullargspec(modulename.RED).args
    params = [kwargs[namespace[argument]] for argument in moduleargs]
    return modulename.RED(*params)

def PQR(x):
    P = x[0]
    Q = x[1]
    PQR = P/Q
    return PQR

def callRED(x,**kwargs):

    # Parametric values for UVT215:
    UVT215_A = 0.2804
    UVT215_B = 0.0609

    #Lamp Status:
    Status = 100 #[%]

    #Lamp Module:
    module = kwargs['module']
    NLamps = kwargs['NLamps']
    D1Log = kwargs['D1Log']
    Status = 100 # Will be changed later

    # P,Q,UVT254
    P = x[0]
    Q = x[1]
    UVT = x[2]

    # Evaluation of UVT215 value:
    UVT215 = round(UVT215_A * np.exp(UVT215_B * UVT), 1)
    if UVT215 > UVT:  # Limiting mechanism. May be changed in future
        UVT215 = UVT

    return RED(module=module, P=P, Flow=Q, UVT=UVT, UVT215=UVT215, Status=Status, D1Log=D1Log, NLamps=NLamps)

def objective(x): #PQR
    # Minimize PQR
    return PQR(x)

def c1(x):
    #RED >= targetRED
    return callRED(x,module=systems[System],NLamps=NLamps[System],D1Log=18) - targetRED

def c2(x):
    # RED <= targetRED+5
    return callRED(x, module=systems[System], NLamps=NLamps[System], D1Log=18) - (targetRED+5)

# Inequality constants:
cons = ({'type':'ineq','fun':c1},
        {'type':'ineq','fun':c2})

# Put bounds on variable x[0],x[1],x[2] which is P,Q,UVT
bounds = ((minP, maxP), (minFlow, maxFlow), (minUVT,maxUVT))

# Optimal Solution:
sol = shgo(objective, bounds=bounds, iters=5, constraints=cons)
#print(sol['success'])

#Retrive the optimized solution
xOpt = sol.x
PQROpt = sol.fun

REDOpt = callRED(xOpt,module=systems[System],NLamps=NLamps[System],D1Log=18)

print(f'P:{round(xOpt[0],1)}[%]')
print(f'Q:{round(xOpt[1],1)}[m³/h]')
print(f'UVT:{round(xOpt[2],1)}[%-1cm]')
print(f'PQR:{round(LampPower(System)*NLamps[System]*xOpt[0]/xOpt[1],1)}[W/(m³/h)]')
print(f'RED:{round(REDOpt,1)}[mJ/cm²]')
