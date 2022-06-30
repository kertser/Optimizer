from pandas import read_excel as rX
import sys,os

# Parametric Namespace is required for the back-compatibility with the different RED functions
# In general, all the RED functions in all the modules shall be reformatted to **kwargs settings
# However it will affect the back-compatibility with the calculator app
"""
R-200: RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps)
EP-600: RED(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT,D1Log,NLamps)
RS-104: RED(P,Eff,Flow,UVT,D1Log,NLamps)
RZ-104: RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps)
RZ-163: RED(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT,D1Log,NLamps)
RZ-163-UHP: RED(P,Status,Flow,UVT254,UVT215,D1Log,NLamps)
RZ-163-HP: RED(P1,P2,P3,P4,Eff1,Eff2,Eff3,Eff4,Flow,UVT,D1Log,NLamps)
RZ-300-HDR: RED(P,Status,Flow,UVT,D1Log,NLamps)
RZB-300: RED(P1,P2,Eff1,Eff2,Flow,UVT,D1Log,NLamps)
RZM-200: RED(P1,P2,P3,P4,P5,Eff1,Eff2,Eff3,Eff4,Eff5,Flow,UVT,D1Log,NLamps)
RZM-350: RED(P1,P2,P3,P4,P5,P6,P7,P8,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Eff8,Flow,UVT,D1Log,NLamps)
RZMW-350-7: RED(P1,P2,P3,P4,P5,P6,P7,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Flow,UVT,D1Log,NLamps):
RZMW-350-11: RED(P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,Eff1,Eff2,Eff3,Eff4,Eff5,Eff6,Eff7,Eff8,
    Eff9,Eff10,Eff11,Flow,UVT,D1Log,NLamps):
"""
namespace = {
    'D1Log': 'D1Log',
    'Flow': 'Flow',
    'Eff': 'Status',
    'Status': 'Status',
    'UVT': 'UVT',
    'UVT254': 'UVT',
    'UVT215': 'UVT215',
    'P': 'P',
    'P1': 'P',
    'P2': 'P',
    'P3': 'P',
    'P4': 'P',
    'P5': 'P',
    'P6': 'P',
    'P7': 'P',
    'P8': 'P',
    'P9': 'P',
    'P10': 'P',
    'P11': 'P',
    'Eff1': 'Status',
    'Eff2': 'Status',
    'Eff3': 'Status',
    'Eff4': 'Status',
    'Eff5': 'Status',
    'Eff6': 'Status',
    'Eff7': 'Status',
    'Eff8': 'Status',
    'Eff9': 'Status',
    'Eff10': 'Status',
    'Eff11': 'Status',
    'NLamps': 'NLamps'
}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Read the data from SystemParameters into the Pandas Dataframe
SystemParameters_path = resource_path("SystemParameters.xlsx")
SystemParameters = rX(SystemParameters_path, dtype='str',index_col=3) # System Parameters file

# systems contains the names of the modules, used for the calculation of RED
systems = SystemParameters['CalcModule'].to_dict()
NLamps = SystemParameters['NLamps'].astype('int').to_dict()
reactor_families = sorted(list(set(['-'.join(reactor.split('-')[:2]) for reactor in systems.keys()])))
valid_systems = list(systems.keys()) #Init the full list
validatedFamilies = ['RZ-104','RZ-163','RZ-300']

def LampPower(system):
    """
    Returns the actual system power in Watts
    """
    try:
        modulename = __import__(systems[system])
        return (modulename.LampPower)
    except ImportError:
        print('No module found')
        sys.exit(1)

def Qmin_max(system):
    return (SystemParameters['Qmin [m^3/h]'][system],SystemParameters['Qmax [m^3/h]'][system])

def Pmin_max(system):
    return (SystemParameters['Pmin [%]'][system], SystemParameters['Pmax [%]'][system])

def UVTmin_max(system):
    return (SystemParameters['UVTmin [%-1cm]'][system], SystemParameters['UVTmax [%-1cm]'][system])