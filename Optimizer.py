"""
More info for deployment and examples:
https://nicegui.io/
You can call ui.run() with optional arguments:

host (default: '0.0.0.0')
port (default: 8080)
title (default: 'NiceGUI')
favicon (default: 'favicon.ico')
dark: whether to use Quasar's dark mode (default: False, use None for "auto" mode)
reload: automatically reload the ui on file changes (default: True)
show: automatically open the ui in a browser tab (default: True)
on_connect: default function or coroutine which is called for each new client connection; the optional request argument provides session infos
uvicorn_logging_level: logging level for uvicorn server (default: 'warning')
uvicorn_reload_dirs: string with comma-separated list for directories to be monitored (default is current working directory only)
uvicorn_reload_includes: string with comma-separated list of glob-patterns which trigger reload on modification (default: '.py')
uvicorn_reload_excludes: string with comma-separated list of glob-patterns which should be ignored for reload (default: '.*, .py[cod], .sw.*, ~*')
main_page_classes: configure Quasar classes of main page (default: 'q-ma-md column items-start')
binding_refresh_interval: time between binding updates (default: 0.1 seconds, bigger is more cpu friendly)
interactive: used internally when run in interactive Python shell (default: False)
The environment variables HOST and PORT can also be used to configure NiceGUI.

"""

import PQR_optimizer
import opt_config
from nicegui import ui
import asyncio
import csv
import numpy as np
from matplotlib import pyplot as plt

class PQUVT:
    def __init__(self):
        # Initial Values can be changed later
        self.minP = 40
        self.maxP = 100
        self.minQ = 10
        self.maxQ = 2000
        self.minUVT = 25
        self.maxUVT = 99
        self.targetRED = 40
        self.redMargin = 5 # RED +/- margin of RED
        self.D1Log = 18 # mJ/cm^2

pquvt = PQUVT()

# This is a temporary procedure and will be replaced
async def optimize():
    table.options.rowData = []
    opbutton.visible = False # Hide the "Optimize" button
    ui.colors(primary='#555') # Make all gray
    ui.notify('Optimiation in progress...\nPlease wait for the calculation results to be finished', close_button='OK')

    #for system in opt_config.systems.keys():
    for system in opt_config.valid_systems:

        try:
            # Iterations (by means of complexity)
            iters = 5
            max_iters = 8
            REDOpt = 0 #Initial value
            #redMargin = 5

            while not ((pquvt.targetRED - pquvt.redMargin) <= REDOpt <= (pquvt.targetRED + pquvt.redMargin)) and (iters < max_iters):

                xOpt, REDOpt, PQROpt = PQR_optimizer.optimize(System=system,minP=pquvt.minP,maxP=pquvt.maxP,
                                                              minFlow=pquvt.minQ,maxFlow=pquvt.maxQ,
                                                              minUVT=pquvt.minUVT,maxUVT=pquvt.maxUVT,
                                                              iters = iters,targetRED=pquvt.targetRED,
                                                              redMargin=pquvt.redMargin,D1Log=pquvt.D1Log)
                iters += 1
                if iters == max_iters:
                    raise Exception("not converging good enough")

            table.options.rowData.append({
                'system': system, 'pqr': round(PQROpt, 1), 'targetRED': round(REDOpt, 1),
                'pMin': max(int(opt_config.Pmin_max(system)[0]),pquvt.minP), 'pMax': min(int(opt_config.Pmin_max(system)[1]),pquvt.maxP),
                'qMin': max(int(opt_config.Qmin_max(system)[0]),pquvt.minQ), 'qMax': min(int(opt_config.Qmin_max(system)[1]),pquvt.maxQ),
                'uvtMin': max(int(opt_config.UVTmin_max(system)[0]),pquvt.minUVT), 'uvtMax': min(int(opt_config.UVTmin_max(system)[1]),pquvt.maxUVT)
            })
            await table.view.update()
            await asyncio.sleep(1)
        except: # no solution for the selected range
            await asyncio.sleep(0)
    table.options.rowData = sorted(table.options.rowData, key=lambda d: d['pqr'])
    ui.colors() # Reset colors
    ui.notify('Finished the optimization...',close_button='OK',position='center')
    opbutton.visible = True # Restore button visibility

def export_to_CSV(): # Export the data to csv
    # TODO: Rewrite to export in descent format: headers than data per line
    tableData = table.options.to_dict()['rowData']
    columnDefs = [line['headerName'] for line in table.options.to_dict()['columnDefs']]
    with open('best_reactors.csv', 'w') as f:
        [f.write("%s," % (_).replace("²", "^2").replace("³", "^3")) for _ in columnDefs]
        f.write("\n")
        for tableLine in tableData:
            for line in tableLine.values():
                f.write("%s," % (line))
            f.write("\n")
        f.close()

def reset(): # Reset everything
    pquvt = PQUVT()
    selectAll()
    table.options.rowData = []
    minPower.__setattr__('value', pquvt.minP)
    maxPower.__setattr__('value', pquvt.maxP)
    minFlow.__setattr__('value', pquvt.minQ)
    maxFlow.__setattr__('value', pquvt.maxQ)
    minUVT.__setattr__('value', pquvt.minUVT)
    maxUVT.__setattr__('value', pquvt.maxUVT)

def clearAll():
    for _ in opt_config.reactor_families:
        switch[_].value = False

def selectAll():
    for _ in opt_config.reactor_families:
        switch[_].value = True

def validatedOnly():
    for _ in opt_config.reactor_families:
        switch[_].value = False
    for _ in opt_config.validatedFamilies:
        switch[_].value = True

def add_remove_system(value):
    # Filter-out the systems per family
    opt_config.valid_systems = list(opt_config.systems.keys()) #Init the full list
    for reactor_type in opt_config.reactor_families: #for all type in full families
        if switch[reactor_type].value == False: # If the reactor type is "off"
            for reactor in reactor_type:
                opt_config.valid_systems = list(filter(lambda t: reactor_type not in t, opt_config.valid_systems))

def power(minmax):
    # Resolve the minimum-maximum for Power
    if minmax == 'min':
        if minPower.value > maxPower.value:
            maxPower.__setattr__('value', minPower.value)
    if minmax == 'max':
        if maxPower.value < minPower.value:
            minPower.__setattr__('value', maxPower.value)

def flow(minmax):
    # Resolve the minimum-maximum for Flow
    if minmax == 'min':
        if minFlow.value > maxFlow.value:
            maxFlow.__setattr__('value', minFlow.value)
    if minmax == 'max':
        if maxFlow.value < minFlow.value:
            minFlow.__setattr__('value', maxFlow.value)

def uvt(minmax):
    # Resolve the minimum-maximum for UVT254
    if minmax == 'min':
        if minUVT.value > maxUVT.value:
            maxUVT.__setattr__('value', minUVT.value)
    if minmax == 'max':
        if maxUVT.value < minUVT.value:
            minUVT.__setattr__('value', maxUVT.value)

def loadChart():
    # Initialize the empty data
    chart.options['series']['name' == 'High UVT']['data'] = []
    chart.options['series']['name' == 'Low UVT']['data'] = []
    chart.options['xAxis']['categories'] = []

    tableData = table.options.to_dict()['rowData']

    for tableLine in tableData:
        #print(tableLine['system']) #as system name
        #print(tableLine['pqr']) #as PQR
        #print(tableLine)
        #print(tableLine['uvtMin'])
        #print(tableLine['uvtMax'])
        minUVT = tableLine['uvtMin']
        maxUVT = tableLine['uvtMax']
        system = tableLine['system']

        if minUVT < int(opt_config.UVTmin_max(system)[0]):
            minUVT = int(opt_config.UVTmin_max(system)[0])
        if maxUVT > int(opt_config.UVTmin_max(system)[1]):
            maxUVT = int(opt_config.UVTmin_max(system)[1])

        chart.options['xAxis']['categories'].append(system)
        #print(PQR_optimizer.specificPQR(system=system,P=100,Status=100,UVT254=maxUVT,targetRED=40))
        chart.options['series']['name'=='High UVT']['data'].append(PQR_optimizer.specificPQR(system=system,
                                                                                             P=100,
                                                                                             Status=100,
                                                                                             UVT254=maxUVT,
                                                                                             targetRED=40))
        chart.options['series']['name' == 'Low UVT']['data'].append(PQR_optimizer.specificPQR(system=system,
                                                                                              P=100,
                                                                                              Status=100,
                                                                                              UVT254=minUVT,
                                                                                              targetRED=40))

    """
    chart = ui.chart({
                    'title': {'text': 'Optimized PQR per UVT range'},
                    'subtitle': {'text': '5-top results'},
                    'chart': {'type': 'column','height':270,'zoomType': 'y'},
                    'xAxis': {'categories': ['RZ-163-11', 'RZ-104-12']},
                    'yAxis': {'title': {'text': 'P/Q [W/(m³/h)]'}},
                    'legend': {'layout':'vertical','align':'right','verticalAlign':'top','floating': True},
                    'exporting':{'enabled':False},
                    'credits': {'enabled': False},
                    'series': [
                        {'name': 'Low UVT', 'data': [0.1, 0.2 ,1, 2.3, 3.5]},
                        {'name': 'High UVT', 'data': [0.3, 0.4, 3.2, 1.1, 0.1]},

                    ],
                }).classes('h-64')
    """

    """
    system = 'RZ-104-11'
    UVTs = np.linspace(40,99)
    REDs = [PQR_optimizer.RED(module=opt_config.systems[system],P=100,Flow=100,
                              UVT=uvt,UVT215=90,Status=100,D1Log=18,NLamps=opt_config.NLamps[system])
            for uvt in UVTs]

    chart.options['chart']['type']='scatter'
    chart.options['series'] = {'name':'RED vs. UVT for '+system,'data':[_ for _ in zip(UVTs,REDs)]}
    """

#%% --- Main Frame ---

ui.colors()
with ui.row():
    with ui.column():
        with ui.row().classes('flex items-stretch'):
            with ui.card().classes('max-w-full mr-2'):
                ui.label('Control Variables:').classes('text-h7 underline')
                with ui.row().classes('max-w-full space-x-2'): #Power
                    P_check = ui.checkbox('Power:',value=True).classes('max-w-full w-20')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minPower = ui.slider(min=pquvt.minP, max=pquvt.maxP, value=pquvt.minP,on_change=lambda: power('min')).bind_value_to(pquvt,'minP').props('label')
                        with ui.row() as row:
                            ui.label('Minimum Power:')
                            ui.label().bind_text_from(minPower, 'value').classes('font-black')
                            ui.label('[%]')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxPower = ui.slider(min=pquvt.minP, max=pquvt.maxP, value=pquvt.maxP,on_change=lambda: power('max')).bind_value_to(pquvt,'maxP').props('label')
                        with ui.row() as row:
                            ui.label('Maximum Power:')
                            ui.label().bind_text_from(maxPower, 'value').classes('font-black')
                            ui.label('[%]')

                with ui.row().classes('max-w-full space-x-2'): # Flow
                    Q_check = ui.checkbox('Flow:',value=True).classes('max-w-full w-20')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minFlow = ui.slider(min=pquvt.minQ, max=pquvt.maxQ, value=pquvt.minQ,on_change=lambda: flow('min')).bind_value_to(pquvt,'minQ').props('label')
                        with ui.row() as row:
                            ui.label('Minimum Flow:')
                            ui.label().bind_text_from(minFlow, 'value').classes('font-black')
                            ui.label('[m³/h]')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxFlow = ui.slider(min=pquvt.minQ, max=pquvt.maxQ, value=pquvt.maxQ,on_change=lambda: flow('max')).bind_value_to(pquvt,'maxQ').props('label')
                        with ui.row() as row:
                            ui.label('Maximum Flow:')
                            ui.label().bind_text_from(maxFlow, 'value').classes('font-black')
                            ui.label('[m³/h]')

                with ui.row().classes('max-w-full space-x-2'): # UVT
                    UVT_check = ui.checkbox('UVT:',value=True).classes('max-w-full w-20')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minUVT = ui.slider(min=pquvt.minUVT, max=pquvt.maxUVT, value=pquvt.minUVT,on_change=lambda: uvt('min')).bind_value_to(pquvt,'minUVT').props('label')
                        with ui.row() as row:
                            ui.label('Minimum UVT:')
                            ui.label().bind_text_from(minUVT, 'value').classes('font-black')
                            ui.label('[%-1cm]')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxUVT = ui.slider(min=pquvt.minUVT, max=pquvt.maxUVT, value=pquvt.maxUVT,on_change=lambda: uvt('max')).bind_value_to(pquvt,'maxUVT').props('label')
                        with ui.row() as row:
                            ui.label('Maximum UVT:')
                            ui.label().bind_text_from(maxUVT, 'value').classes('font-black')
                            ui.label('[%-1cm]')
                with ui.row().classes('w-full justify-evenly'):
                    targetRED_input = ui.number(label = 'Target RED [mJ/cm²]',value=pquvt.targetRED,
                                                format='%.1f',placeholder='Target Dose?').bind_value_to(pquvt,'targetRED').classes('space-x-5 w-32')
                    redMargin_input = ui.number(label = 'RED margin [±mJ/cm²]',value=pquvt.redMargin,
                                                format='%.1f',placeholder='Dose Margin?').bind_value_to(pquvt,'redMargin').classes('space-x-5 w-32')
                    D1Log_input = ui.number(label='1-Log Dose [±mJ/cm²]', value=pquvt.D1Log,
                                                format='%.1f', placeholder='D-1Log?').bind_value_to(pquvt,'D1Log').classes('space-x-5 w-32')

            with ui.card().classes(''):

                chart = ui.chart({
                    'title': {'text': 'Optimized PQR per UVT range'},
                    'subtitle': {'text': '5-top results'},
                    'chart': {'type': 'column','height':270,'zoomType': 'y'},
                    'xAxis': {'categories': ['RZ-163-11', 'RZ-104-12']},
                    'yAxis': {'title': {'text': 'P/Q [W/(m³/h)]'}},
                    'legend': {'layout':'vertical','align':'right','verticalAlign':'top','floating': True},
                    'exporting':{'enabled':False},
                    'credits': {'enabled': False},
                    'series': [
                        {'name': 'Low UVT', 'data': [0.1, 0.2 ,1, 2.3, 3.5]},
                        {'name': 'High UVT', 'data': [0.3, 0.4, 3.2, 1.1, 0.1]},

                    ],
                }).classes('h-64')
                with ui.row():
                    ui.button('push me!',on_click = loadChart).props('size=sm')
                    ui.button('push me too!!!').props('size=sm')

        with ui.card().classes('bg-yellow-300 w-full h-64'):
            table = ui.table({
                'columnDefs': [
                        {'headerName': 'System Type', 'field': 'system'},
                        {'headerName': 'PQR [W/(m³/h)]', 'field': 'pqr'},
                        {'headerName': 'Effective RED [mJ/cm²]', 'field': 'targetRED'},
                        {'headerName': 'Pmin [%]', 'field': 'pMin'},
                        {'headerName': 'Pmax [%]', 'field': 'pMax'},
                        {'headerName': 'Qmin [m³/h]', 'field': 'qMin'},
                        {'headerName': 'Qmax [m³/h]', 'field': 'qMax'},
                        {'headerName': 'UVT254min [%-1cm]', 'field': 'uvtMin'},
                        {'headerName': 'UVT254max [%-1cm]', 'field': 'uvtMax'},
                    ],
                    'rowData': [],
                })

        with ui.card().classes('bg-yellow-300 w-full'):
            with ui.row().classes('w-full justify-between'):
                with ui.row().classes('relative left-0'):
                    opbutton = ui.button('Optimize', on_click=optimize)
                    reset = ui.button('Reset All', on_click=reset)
                export = ui.button('Export to csv', on_click=export_to_CSV)
    # Switches
    switch = {}
    with ui.card().classes('w-62'):
        ui.image('https://atlantium.com/wp-content/uploads/2020/03/Atlantium_Logo_Final_white3.png').style('width:200px')
        ui.label('Specific Reactor Types:').classes('text-h7 underline')
        with ui.column().classes('-space-y-5'):
            for reactor_type in opt_config.reactor_families:
                with ui.row().classes('w-full justify-between'):
                    switch[reactor_type]=ui.switch(reactor_type, value=True, on_change=lambda e: add_remove_system(e.value))
                    with ui.row().classes('pt-3 -space-x-3'):
                        for sub_type in opt_config.reactor_subtypes(reactor_type):
                            ui.button(sub_type).props('rounded dense size=xs')

            ui.html('<br>')
            with ui.row().classes('w-full justify-between'):
                clearAll = ui.button('Clear', on_click=clearAll)
                enableAll = ui.button('Select All', on_click=selectAll)
            ui.html('<br>')
            validatedOnly = ui.button('Validated Systems Only', on_click=validatedOnly)
        ui.image('https://atlantium.com/wp-content/uploads/2022/06/HOD-UV-A_Technology_Overview-540x272.jpg').style('height:82px')

if __name__ == "__main__":
    ui.run(title = 'Optimizer', host='127.0.0.1', reload=False, favicon='configuration.ico',show=False)