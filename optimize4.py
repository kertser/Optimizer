#Example of non-linear constrained optimizaton wotj scipy
from scipy.optimize import minimize
import numpy as np
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
import inspect

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
    module = 'RZ-104-11'

    return P/Q*np.log(UVT/100)

def objective(x): #PQR
    # Minimize PQR
    return PQR(x)

def constraint(x):
    #RED >= 10
    return callRED(x)-10

con = ({'type':'ineq','fun':constraint})
P_guess = 100
Q_guess = 100
UVT_guess = 40

x0 = np.array([P_guess,Q_guess,UVT_guess])

sol = minimize(objective,x0, method='SLSQP',constraints=con,options={'disp':True})

#Retrive the optimized solution
xOpt = sol.x
PQROpt = sol.fun

REDOpt = callRED(xOpt)

print(f'P:{xOpt[0]}')
print(f'Q:{xOpt[1]}')
print(f'UVT:{xOpt[2]}')
print(f'PQR:{PQROpt}')