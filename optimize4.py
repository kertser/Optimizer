# PQR optimizer
from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
from opt_config import NLamps
import inspect
import sys

System = 'RZ-163-13'
targetRED = 40 # [mJ/cm^2]
minUVT = 40
maxUVT = 99
minFlow = 30
maxFlow = 140
minP = 99
maxP = 100

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

def constraint(x):
    #RED >= targetRED
    return callRED(x,module=systems[System],NLamps=NLamps[System],D1Log=18)-targetRED

cons = ({'type':'ineq','fun':constraint})

def confunc(x):
    return callRED(x, module=systems[System], NLamps=NLamps[System], D1Log=18)

nlc = NonlinearConstraint(confunc, targetRED, targetRED+1)

# Put bounds on variable x[0],x[1],x[2] which is P,Q,UVT
bounds = ((minP, maxP), (minFlow, maxFlow), (minUVT,maxUVT))

# Initial Guesses:
P_guess = maxP#maxP#np.average(minP,maxP)
Q_guess = minFlow#np.average(minFlow,maxFlow)
UVT_guess = maxUVT#maxUVT#np.average(minUVT,maxUVT)

x0 = np.array([P_guess,Q_guess,UVT_guess])

#sol = minimize(objective,x0, method='SLSQP',constraints=nlc,options={'disp':True,'maxiter':1000}, bounds=bounds)
sol = minimize(objective,x0, method='COBYLA',constraints=cons,options={'disp':True,'maxiter':1000}, bounds=bounds)
#sol = minimize(objective,x0, method='trust-constr',constraints=nlc,options={'disp':True,'maxiter':1000}, bounds=bounds)



#Retrive the optimized solution
xOpt = sol.x
PQROpt = sol.fun

REDOpt = callRED(xOpt,module=systems[System],NLamps=NLamps[System],D1Log=18)

print(f'P:{round(xOpt[0],1)}[%]')
print(f'Q:{round(xOpt[1],1)}[m³/h]')
print(f'UVT:{round(xOpt[2],1)}[%-1cm]')
print(f'PQR:{round(LampPower(System)*xOpt[0]/xOpt[1],1)}[W/(m³/h)]')
print(f'RED:{round(REDOpt,1)}[mJ/cm²]')