"""
Example:
Minimize PQR by means of flow, UVT for the RED > 40
"""

from scipy.optimize import minimize
import numpy as np
import RZ_300_HDR

def RED(P,Q,UVT):
    Status = 100 # [%]
    D1Log = 18 # [mJ/cm^2]
    N_lamps = 1
    return RZ_300_HDR.RED(P, 100, Q, UVT, 18, 1)

def PQR(P,Q):
    return P/Q

def objective(x):
# Minimize PQR which is a cost per treated volume
    return PQR(x[0],x[1])

def constraint(x):
# RED > target -> Constant
    target = 40 # Target RED

    P = x[0] # [%]
    Q = x[1] # [m3h]
    UVT = x[2] # [%-1cm]

    return (RED(P, Q, UVT) - target)

# list of constraints
con = ({'type':'ineq','fun':constraint}) #inequality constraint

# list of initial guesses
Pguess = 100
QGuess = 5
UVTGuess = 40

x0 = np.array([Pguess,QGuess,UVTGuess])
sol = minimize(objective,x0, method='SLSQP',constraints=con,options={'disp':True})

#print(PQR(100,65)) # PQR = f(Red,UVT)
# print(objective(100,65))

#Retrive the optimized solution
xOpt = sol.x
PQROpt = sol.fun

RedOpt = RED(xOpt)

print(f'P:{xOpt[0]}')
print(f'Q:{xOpt[1]}')
print(f'UVT:{xOpt[2]}')
print(f'RED:{REDOpt}')