# PQR optimizer
from scipy.optimize import shgo
import numpy as np
import opt_config
from opt_config import systems, LampPower
from opt_config import namespace
from opt_config import NLamps
import inspect
import sys

def optimize(targetRED = 40, System = 'RZ-163-11',
             minP=40, maxP = 100,
             minFlow = 5, maxFlow = 3500,
             minUVT = 25, maxUVT = 98,
             iters=5, redMargin=5, D1Log=18):
    # Optimization function will return minimum PQR at the set range of parameters

    # Check the boundary conditions:
    if minP<int(opt_config.Pmin_max(System)[0]):
        minP = int(opt_config.Pmin_max(System)[0])
    if maxP>int(opt_config.Pmin_max(System)[1]):
        maxP = int(opt_config.Pmin_max(System)[1])

    if minFlow<int(opt_config.Qmin_max(System)[0]):
        minFlow = int(opt_config.Qmin_max(System)[0])
    if maxFlow>int(opt_config.Qmin_max(System)[1]):
        maxFlow = int(opt_config.Qmin_max(System)[1])

    if minUVT<int(opt_config.UVTmin_max(System)[0]):
        minUVTm = int(opt_config.UVTmin_max(System)[0])
    if maxUVT>int(opt_config.UVTmin_max(System)[1]):
        maxUVTm = int(opt_config.UVTmin_max(System)[1])

    def objective(x):  # PQR
        # Minimize PQR
        return PQR(x)

    def c1(x):
        # RED >= targetRED
        return callRED(x, module=systems[System], NLamps=NLamps[System], D1Log=D1Log) - (targetRED)

    def c2(x):
        # RED <= targetRED+10
        return (targetRED + 10) - callRED(x, module=systems[System], NLamps=NLamps[System], D1Log=D1Log)

    # def RED(P,Q,UVT,Status,module):
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
        PQR = P / Q
        return PQR

    def callRED(x, **kwargs):

        # Parametric values for UVT215:
        UVT215_A = 0.2804
        UVT215_B = 0.0609

        # Lamp Status:
        Status = 100  # [%]

        # Lamp Module:
        module = kwargs['module']
        NLamps = kwargs['NLamps']
        D1Log = kwargs['D1Log']
        Status = 100  # Will be changed later

        # P,Q,UVT254
        P = x[0]
        Q = x[1]
        UVT = x[2]

        # Evaluation of UVT215 value:
        UVT215 = round(UVT215_A * np.exp(UVT215_B * UVT), 1)
        if UVT215 > UVT:  # Limiting mechanism. May be changed in future
            UVT215 = UVT

        return RED(module=module, P=P, Flow=Q, UVT=UVT, UVT215=UVT215, Status=Status, D1Log=D1Log, NLamps=NLamps)

    # Inequality constants:
    cons = ({'type': 'ineq', 'fun': c1},
            {'type': 'ineq', 'fun': c2})

    # Put bounds on variable x[0],x[1],x[2] which is P,Q,UVT
    bounds = ((minP, maxP), (minFlow, maxFlow), (minUVT, maxUVT))

    # Optimal Solution:
    sol = shgo(objective, bounds=bounds, iters=iters, n=128, constraints=cons)
    # print(sol['success'])

    # Retrive the optimized solution

    for solution in sol.xl:
        tempRED = callRED(solution, module=systems[System], NLamps=NLamps[System], D1Log=D1Log)
        if abs(tempRED - targetRED) < redMargin: # Default Margin is 5, but might be changed later on

            break

    xOpt = solution
    PQROpt = solution[0]/solution[1] * LampPower(System) * NLamps[System]  # PQR
    REDOpt = tempRED

    return (xOpt, REDOpt, PQROpt)