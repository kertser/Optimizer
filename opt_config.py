from pandas import read_excel as rX
import sys,os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SystemParameters_path = resource_path("SystemParameters.xlsx")
SystemParameters = rX(SystemParameters_path, dtype='str',index_col=0) # System Parameters file

# systems contains the names of the modules, used for the calculation of RED
systems = SystemParameters['CalcModule'].to_dict()

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