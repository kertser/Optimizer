from gekko import gekko
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace,NLamps
from statistics import mean
import inspect

m = gekko()
System = 'RZ-104-11'
targetRED = 40 # [mJ/cm^2]
#targetRED = m.Param(value=40)

P = m.Var(50,40,100)
Q = m.Var(100,5,140)
UVT = m.Var(60,40,99)

def RED(**kwargs):

    try:
        modulename = __import__(kwargs['module'])
    except ImportError:
        print('No module found')
        sys.exit(1)

    # Get the arguments of the specific RED function
    module_args = inspect.getfullargspec(modulename.RED).args

    params = [kwargs[namespace[argument]] for argument in module_args]
    params = [param.value.value if not (isinstance(param,int) or isinstance(param,float)) else param for param in params]
    return m.Var(value=modulename.RED(*params))
    #return modulename.RED(*params)

def PQR(**kwargs):
    P = kwargs['P']
    Q = kwargs['Flow']
    return P/Q

#Equations
m.Equation(RED(module = systems[System],P=P,Flow=Q,UVT=UVT,UVT215=UVT,Status = 100,D1Log=18,NLamps=NLamps[System])>=targetRED)
#m.Equation(xPQR == PQR(P=P, Flow=Q))

#m.Equation(xRED>=targetRED)
#m.Minimize(P/Q)
m.Obj(P/Q)

#Solve simulation
m.options.IMODE = 3 #steady-state optimizer
#m.solve(disp=False) #disp is True by default
m.solve() #disp is True by default

print(f'P = {round(P.value[0],1)}[%]')
print(f'Q = {round(Q.value[0],1)}[m³/h]')
print(f'UVT = {round(UVT.value[0],1)}[%-1cm]')

print(f'PQR = {round(LampPower(System)*P.value[0]/Q.value[0],1)}[W/(m³/h)]') # multiply by N_Lamps
print(f'RED = {round(xRED.value[0],1)}[mJ/cm²]')
print(f'RED = {round(RED(module = systems[System],P=P.value[0],Flow=Q.value[0],UVT=UVT.value[0],UVT215=UVT.value[0],Status = 100,D1Log=18,NLamps=NLamps[System]).value.value,1)}[mJ/cm²]')
