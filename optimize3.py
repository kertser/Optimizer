"""
Example:
Minimize PQR by means of flow, UVT for the RED > 40
Next step - maximum RED for minimum PQR
"""
from gekko import GEKKO
import opt_config
from opt_config import systems, LampPower
from statistics import mean

m = GEKKO()

def RED(P,Q,UVT,module):
    '''
    Returns a RED value of the selected UV system
    param 'module': name of the system
    '''
    try:
        modulename = __import__(module)
        #print(modulename)
        #print(modulename.LampPower)
    except ImportError:
        print('No module found')
        sys.exit(1)

    Status = 100 # [%]
    D1Log = 18 # [mJ/cm^2]
    N_lamps = 1
    return modulename.RED(P, Status, Q, UVT, D1Log, N_lamps)

targetRed = m.Param(value=40)

P,Q,UVT = [m.Var() for _ in range(3)]

#lower bounds
P.lower = 30
Q.lower = 5
UVT.lower = 40

#upper bounds
P.upper = 100
Q.upper = 300
UVT.upper = 99

#initial values
P.value = mean([P.upper,P.lower])
Q.value = mean([Q.upper,Q.lower])
UVT.value = mean([UVT.upper,UVT.lower])

#Equations
xRED = m.Var(value=RED(P.value,Q.value,UVT.value,systems['RZ-300']))
PQR = m.Var()

m.Equation(xRED>=targetRed)
m.Equation(xRED<(targetRed+5))
m.Equation(PQR == P/Q)
#m.Obj(xPQR)
m.Minimize(PQR)

#Set global options
m.options.IMODE = 3 #steady state optimization
m.options.SOLVER = 3 # IPOPT
m.options.AUTO_COLD = 5 # Cold start after X cycles

#Solve simulation
m.solve(disp=False) #disp is True by default

print(f'P = {round(P.value[0],1)}[%]')
print(f'Q = {round(Q.value[0],1)}[m³/h]')
print(f'UVT = {round(UVT.value[0],1)}[%-1cm]')

print(f'PQR = {round(LampPower("RZ-300")*P.value[0]/Q.value[0],1)}[W/(m³/h)]')
print(f'RED = {round(xRED.value[0],1)}[mJ/cm²]')