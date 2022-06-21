"""
Example:
Minimize PQR by means of flow, UVT for the RED > 40
Next step - maximum RED for minimum PQR
"""
from gekko import GEKKO
import RZ_300_HDR

m = GEKKO()

def RED(P,Q,UVT):
    P = P.value
    Q = Q.value
    UVT = UVT.value
    Status = 100 # [%]
    D1Log = 18 # [mJ/cm^2]
    N_lamps = 1
    return RZ_300_HDR.RED(P, Status, Q, UVT, D1Log, N_lamps)

def PQR(P,Q):
    P = P.value
    Q = Q.value
    return P/Q

# Set up the accuracy
#m.options.RTOL = 0.1
#m.options.OTOL = 0.1

# Set up the variables, parameters, constants and limits
xP = m.Var(value=53,lb=40,ub=100)
#xP = m.Const(100)
#xP = m.Param(55)
xQ = m.Var(value=10,lb=1,ub=100)
xUVT = m.Var(value=70,lb=40,ub=95)

xRED = m.Var()
xPQR = m.Var()

m.Equation(xRED == RED(xP,xQ,xUVT))
m.Equation(xPQR == PQR(xP,xQ))

#targetRED = 40 # [mJ/cm^2]
targetRED = m.Param(value=40)

# Limiting factors and Objectives
m.Equation(xRED > targetRED)

m.options.IMODE = 3 #steady-state optimizer = 1-3
#m.options.SEQUENTIAL = 1
m.options.SOLVER = 3 # IPOPT
#m.options.SOLVER = 1 # APOPT

m.options.AUTO_COLD = 5 # Cold start after X cycles
# m.options.CV_TYPE = 2 # Quadric

#m.Obj(xPQR)

m.Minimize(xPQR)
#m.Maximize(xRED)
m.solve(disp=False) #disp is True by default

print(f'P = {xP.value}')
print(f'Q = {xQ.value}')
print(f'UVT = {xUVT.value}')

print(f'PQR = {xPQR.value}')
print(f'RED = {xRED.value}')