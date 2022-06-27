import PQR_optimizer
import opt_config

PQRs = {} #empty dictionary of PQRs
#print(opt_config.systems.keys())
for system in opt_config.systems.keys():
    xOpt, REDOpt, PQROpt = PQR_optimizer.optimize(System=system)
    PQRs[system] = round(PQROpt,1)
    #print(system,'',round(PQROpt,1))

for system in sorted(PQRs, key=PQRs.get) :
     print(f'In system {system}, PQR = {PQRs[system]}[W/(m³/h)]')
