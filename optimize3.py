"""
Example:
Minimize PQR by means of flow, UVT for the RED > 40
Next step - maximum RED for minimum PQR
"""
from gekko import GEKKO
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
from statistics import mean
import inspect

m = GEKKO()
System = 'RZ-104'
targetRED = 40 # [mJ/cm^2]

#def RED(P,Q,UVT,Status,module):
def RED(**kwargs):
    '''
    Returns a RED value of the selected UV system
    param 'module': name of the system
    '''
    try:
        modulename = __import__(kwargs['module'])
    except ImportError:
        print('No module found')
        sys.exit(1)

    # Get the arguments of the specific RED function
    moduleargs = inspect.getfullargspec(modulename.RED).args

    # TODO: UVT215
    params = [kwargs[namespace[argument]] for argument in moduleargs]

    return modulename.RED(*params)

targetRed = m.Param(value=targetRED)

P,Q,UVT = [m.Var() for _ in range(3)]

#lower bounds
P.lower = 40
Q.lower = 5
UVT.lower = 40

#upper bounds
P.upper = 100
Q.upper = 200
UVT.upper = 60

# Initial values considered to be a mean between the bounds, since the RED function is monotonic
P.value = mean([P.upper,P.lower])
Q.value = mean([Q.upper,Q.lower])
UVT.value = mean([UVT.upper,UVT.lower])

#Equations
xRED = m.Var(value=RED(module = systems[System],P=P.value,Flow=Q.value,UVT=UVT.value,UVT215=UVT.value,Status = 100,D1Log=18,NLamps=2))
PQR = m.Var()

m.Equation(xRED>=targetRed)
#m.Equation(xRED<(targetRed+5))
m.Equation(PQR == P/Q)
m.Minimize(PQR)
#m.Obj(PQR)

#Set global options
m.options.IMODE = 3 #steady state optimization
m.options.SOLVER = 3 # IPOPT
m.options.AUTO_COLD = 5 # Cold start after X cycles

#Solve simulation
m.solve(disp=False) #disp is True by default

print(f'P = {round(P.value[0],1)}[%]')
print(f'Q = {round(Q.value[0],1)}[m³/h]')
print(f'UVT = {round(UVT.value[0],1)}[%-1cm]')

print(f'PQR = {round(LampPower(System)*P.value[0]/Q.value[0],1)}[W/(m³/h)]') # multiply by N_Lamps
print(f'RED = {round(xRED.value[0],1)}[mJ/cm²]')