import PQR_optimizer
import opt_config

PQRs = {} #empty dictionary of PQRs

for system in opt_config.systems.keys():
    try:
        iters = 5
        max_iters = 8
        REDOpt = 0
        redMargin = 5
        tagetRED = 35
        while not ((tagetRED-redMargin) <= REDOpt <= (tagetRED + redMargin)) and (iters < max_iters):

            xOpt, REDOpt, PQROpt = PQR_optimizer.optimize(System=system,
                                                          targetRED=tagetRED,
                                                          iters=iters)
            print('Iterations = ',iters)  # Debug print
            print(f'for system {system} the calculated RED is {REDOpt}')
            iters += 1
            if iters == max_iters:
                raise Exception("not converging good enough")

        PQRs[system] = round(PQROpt,1)
        print(system,'',round(PQROpt,1))
        print(system,'',round(REDOpt,1))
    except:
        print('Solution not found for ',system)

for system in sorted(PQRs, key=PQRs.get):
     print(f'In system {system}, PQR = {PQRs[system]}[W/(m³/h)]')
