"""
Example:
Minimize PQR by means of flow, UVT for the RED > 40
Next step - maximum RED for minimum PQR
"""
from gekko import GEKKO
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace,NLamps
from statistics import mean
import inspect

m = GEKKO()
System = 'RZ-104-11'

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
    #print([type(param) for param in params])

    return modulename.RED(*params)

P,Q,UVT = [m.Var() for _ in range(3)]
PQR = m.Var()
xRED = m.Var()

#lower bounds
P.lower = 60
Q.lower = 5
UVT.lower = 40

#upper bounds
P.upper = 100
Q.upper = 140
UVT.upper = 99

# Initial values considered to be a mean between the bounds, since the RED function is monotonic
P.value = mean([P.upper,P.lower])
Q.value = mean([Q.upper,Q.lower])
UVT.value = mean([UVT.upper,UVT.lower])

#Equations
m.Equation(xRED == RED(module = systems[System],P=P,Flow=Q,UVT=UVT,UVT215=UVT,Status = 100,D1Log=18,NLamps=NLamps[System]))
m.Equation(PQR == P/Q)

m.Equation(xRED>10)
m.Minimize(PQR)
#m.Obj(PQR)

#Set global options
m.options.IMODE = 3 #steady state optimization
#m.options.SOLVER = 3 # IPOPT
#m.options.AUTO_COLD = 5 # Cold start after X cycles

#Solve simulation
m.solve(disp=False) #disp is True by default

print(f'P = {round(P.value[0],1)}[%]')
print(f'Q = {round(Q.value[0],1)}[m³/h]')
print(f'UVT = {round(UVT.value[0],1)}[%-1cm]')

print(f'PQR = {round(LampPower(System)*P.value[0]/Q.value[0],1)}[W/(m³/h)]') # multiply by N_Lamps
#print(f'RED = {round(xRED.value[0],1)}[mJ/cm²]')
print(f'RED = {round(RED(module = systems[System],P=P.value[0],Flow=Q.value[0],UVT=UVT.value[0],UVT215=UVT.value[0],Status = 100,D1Log=18,NLamps=NLamps[System]),1)}[mJ/cm²]')
