#Example of non-linear constrained optimizaton wotj scipy
from scipy.optimize import minimize
import numpy as np
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
import inspect
import sys

System = 'RZ-104-12'
targetRED = 40 # [mJ/cm^2]

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

def callRED(x):
    P = x[0]
    Q = x[1]
    UVT = x[2]
    Status = 100
    #module = 'RZ_104_2L'
    module = systems[System]
    #return RED(module = systems[System],P=P,Flow=Q,UVT=UVT,UVT215=UVT,Status = 100,D1Log=18,NLamps=2)
    return RED(module=module, P=P, Flow=Q, UVT=UVT, UVT215=UVT, Status=100, D1Log=18, NLamps=2)

    #return P/Q*np.log(UVT/100)

def objective(x): #PQR
    # Minimize PQR
    return PQR(x)

def constraint(x):
    #RED >= targetRED
    return callRED(x)-targetRED

con = ({'type':'ineq','fun':constraint})
# Put bounds on variable x[0],x[1],x[2] which is P,Q,UVT
bounds = ((0, 100), (0, 140), (40,99))

P_guess = 100
Q_guess = 100
UVT_guess = 40

x0 = np.array([P_guess,Q_guess,UVT_guess])

sol = minimize(objective,x0, method='SLSQP',constraints=con,options={'disp':True}, bounds=bounds)

#Retrive the optimized solution
xOpt = sol.x
PQROpt = sol.fun

REDOpt = callRED(xOpt)

print(f'P:{round(xOpt[0],1)}')
print(f'Q:{round(xOpt[1],1)}')
print(f'UVT:{round(xOpt[2],1)}')
print(f'PQR:{round(PQROpt,1)}')
print(f'RED:{round(callRED(xOpt),1)}[mJcm^2]')