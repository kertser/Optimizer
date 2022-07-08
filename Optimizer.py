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
#import csv
import numpy as np
#from matplotlib import pyplot as plt

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

    loadChartPQR()
    RED_UVT_chartMin.visible = True
    RED_UVT_chartMax.visible = True

def export_to_CSV(): # Export the data to csv
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
    targetRED_input.__setattr__('value',pquvt.targetRED)
    redMargin_input.__setattr__('value',pquvt.redMargin)
    D1Log_input.__setattr__('value',pquvt.D1Log)
    RED_UVT_chartMin.visible = False
    RED_UVT_chartMax.visible = False
    loadChartPQR()


def clearAll():
    for _ in opt_config.reactor_families:
        switch[_].value = False
    for _ in list(opt_config.systems.keys()):
        subswitch[_].props('color=gray text-color=green')

def selectAll():
    for _ in opt_config.reactor_families:
        switch[_].value = True
    for _ in list(opt_config.systems.keys()):
        subswitch[_].props('color=primary text-color=white')

def validatedOnly():
    for _ in opt_config.reactor_families:
        switch[_].value = False
    for _ in opt_config.validatedFamilies:
        switch[_].value = True

def add_remove_system(e):
    # Filter-out the systems per family
    if switch[e.sender.type].value == False:
        opt_config.valid_systems = [system for system in opt_config.valid_systems
                                    if system not in list(filter(lambda t: e.sender.type in t, opt_config.valid_systems))]
    else:
        opt_config.valid_systems.extend(list(filter(lambda t: e.sender.type in t, opt_config.systems.keys())))

    for _ in list(opt_config.systems.keys()):
        if _ in opt_config.valid_systems:
            subswitch[_].props('color=primary text-color=white')
        else:
            subswitch[_].props('color=gray text-color=green')

def add_remove_subsystem(z):
    # Add or Remove the subsystem
    selected_subsystem = z.sender.model[0]+'-'+z.sender.model[1]
    if selected_subsystem in opt_config.valid_systems: # Disable sybsystem
        opt_config.valid_systems.remove(selected_subsystem)
        z.sender.props('color=gray text-color=green')
        if not list(filter(lambda t: z.sender.model[0] in t, opt_config.valid_systems)):  # If list is empty
            switch[z.sender.model[0]].value = False  # Switch-off the entire family
    else: # Enable sybsystem
        if switch[z.sender.model[0]].value == False: # If the family is off
            switch[z.sender.model[0]].value = True
            for _ in list(filter(lambda t: z.sender.model[0] in t, opt_config.systems.keys())):
                opt_config.valid_systems.remove(_)
                subswitch[_].props('color=gray text-color=green')
            opt_config.valid_systems.append(selected_subsystem)
            subswitch[selected_subsystem].props('color=primary text-color=white')
        else:
            opt_config.valid_systems.append(selected_subsystem)
            z.sender.props('color=primary text-color=white')

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

def loadChartRED(minmax):

    tableData = table.options.to_dict()['rowData']

    chart.options['chart']['type'] = 'scatter'
    chart.options['legend'] = {'borderWidth': 1, 'backgroundColor': 'white', 'x': 70, 'y': 60, 'shadow': True,
                               'layout': 'vertical', 'align': 'left', 'verticalAlign': 'top', 'floating': True}
    chart.options['xAxis'] = {'title': {'text': 'UVT [%-1cm]'}}
    chart.options['yAxis'] = {'title': {'text': 'RED [mJ/cm²]'}}
    chart.options['title'] = {'text': 'RED vs. UVT'}
    if minmax == 'min':
        chart.options['subtitle'] = {'text': 'Top 5 UV-Systems at Minimum Flow'}
    elif minmax =='max':
        chart.options['subtitle'] = {'text': 'Top 5 UV-Systems at Maximum Flow'}
    chart.options['series'] = []  # Initialize Empty

    # Add all the systems into the list
    """
    systems = []
    for _ in opt_config.validatedFamilies:
        systems.append(list(filter(lambda t: _ in t, opt_config.systems.keys()))[0])  # Just the first types
    """
    systems = [tableLine['system'] for tableLine in tableData][:5]

    UVTs = np.round(np.linspace(70, 98), 1)
    minFlow = max([[x for x in tableData[:5] if x['system'] == system][0]['qMin'] for system in systems])
    maxFlow = min([[x for x in tableData[:5] if x['system'] == system][0]['qMax'] for system in systems])

    for system in systems:
        #minFlow = [x for x in tableData[:5] if x['system'] == system][0]['qMin']
        #maxFlow = [x for x in tableData[:5] if x['system'] == system][0]['qMax']
        if minmax == 'min':
            qFlow = minFlow
        elif minmax =='max':
            qFlow = maxFlow

        REDs = [PQR_optimizer.RED(module=opt_config.systems[system], P=100, Flow=qFlow,
                                  UVT=uvt, UVT215=uvt, Status=100, D1Log=18, NLamps=opt_config.NLamps[system])
                for uvt in UVTs]

        chart.options['series'].append({'name': system+' at '+str(qFlow)+'[m³/h]', 'data': [list(_) for _ in zip(UVTs, REDs)]})

def loadChartPQR():
    chart.options['series'] = []  # Initialize Empty

    tableData = table.options.to_dict()['rowData']
    PQRs = [tableLine['pqr'] for tableLine in tableData]

    chart.options['series'].append({'name': 'Optimized PQR', 'data': PQRs})

    chart.options['chart'] = {'type': 'column', 'height': 270, 'zoomType': 'y'}
    chart.options['title'] = {'text': 'Optimized PQR'}
    chart.options['legend'] = {'borderWidth': 1, 'backgroundColor': 'white', 'x': 0, 'y': 0, 'shadow': True,
                               'layout': 'vertical', 'align': 'right', 'verticalAlign': 'top', 'floating': True}
    chart.options['subtitle'] = {'text': 'Calculated Values inside the selected range'}
    chart.options['xAxis'] = {'title': {'text': 'UV-Systems'},
                              'categories': [tableLine['system'] for tableLine in tableData]}
    chart.options['yAxis'] = {'title': {'text': 'P/Q [W/(m³/h)]'}}

    # print(PQR_optimizer.specificPQR(system=system,P=100,Status=100,UVT254=maxUVT,targetRED=40))


#%% --- Main Frame ---
ui.colors()
# Help Dialog:
with ui.dialog() as help_dialog, ui.card():
    ui.markdown('### PQR Optimization Tool for UV-Systems\n'
                'Pleasee apply to [Atlantium Technologies](https://atlantium.com/) website for more information.')
    ui.html('<p>This tool is intended to provide a global parametic optimization in terms of <strong>PQR</strong>:<br>'
            '<strong>P</strong>ower-to-<strong>F</strong>low <strong>R</strong>atio, '
            'which is similar to the  <strong>Cost-Per-Treated-Volume</strong> for the Atlantum UV-Reactors Family</p>')
    ui.html('<p><u>Steps to work with the tool:</u></p>'
            '<p><strong>1:</strong> Choose the parametric range in terms of minimum/maximum for Power[%], Flow Rate[m³/h] and UVT254[%-1cm].<br>'
            '<strong>2:</strong> Choose the target UV-Dose, D1-Log inactivation dose and algorythmic accuracy tolerance.<br>'
            '<strong>3:</strong> Select the relevant UV-reactors by family and/or by  specific branch. One may filter out the validated systems only.<br>'
            '<strong>4:</strong> Push the "Optimize by PQR" button to start global search process.<br>'
            '<strong>5:</strong> The algorithm performes a "simplicial homology global optimization" search for an optimal solution inside the selected range, so that '
            'the cost-per-treated volume for the selected reactor, in terms of PQR value, will provide the specified UV-Dose within the set tolerance. '
            'Note that every UV-reactor type has a specific operating parametric range, so that the algorythm will search inside these limits only.<br>'
            'Some of the reactors will not have a solution for the selected target dose and/or accuracy tolerance<br>'
            '<strong>6:</strong> As soon as the algorithm finishes the optimization, it will populte the ranged table with the most '
            'relevant UV-reactor types at the top of the table. You may find the relevant bar chart of this range at the top-right of the calculator window.<br>'
            '<strong>7:</strong> One may take a look at the additional charts/graphs for the 5 best performing UV-systems and export the table in CSV format.</p>')

    ui.button('Close and back to the PQR tool', on_click=help_dialog.close)

# Main Window:
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

            with ui.card():
                chart = ui.chart({
                    'title': {'text': 'Run PQR Optimization to make the chart available'},
                    'chart': {'height': 270, 'zoomType': 'y'},
                    'exporting':{'enabled':False},
                    'credits': {'enabled': False}
                }).classes('h-64')
                with ui.row():
                    PQR_chart = ui.button('PQR chart', on_click = loadChartPQR).props('size=sm')
                    RED_UVT_chartMin = ui.button('RED vs UVT chart at Qmin', on_click = lambda: loadChartRED('min')).props('size=sm')
                    RED_UVT_chartMax = ui.button('RED vs UVT chart at Qmax', on_click = lambda: loadChartRED('max')).props('size=sm')
                    RED_UVT_chartMin.visible = False
                    RED_UVT_chartMax.visible = False

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
                    opbutton = ui.button('Optimize by PQR', on_click=optimize)
                    reset = ui.button('Reset All', on_click=reset)
                with ui.row().classes('relative right-0'):
                    export = ui.button('Export to csv', on_click=export_to_CSV)
                    help = ui.button(on_click=help_dialog.open).props('icon=help')
    # Switches
    switch = {}
    subswitch = {}
    with ui.card().classes('w-62 -space-y-2'):
        ui.image('https://atlantium.com/wp-content/uploads/2020/03/Atlantium_Logo_Final_white3.png').style('width:200px')
        ui.label('Specific Reactor Types:').classes('text-h8 underline')
        validatedOnly = ui.button('Select Validated Systems Only', on_click=validatedOnly).props(
            'rounded align=around icon=directions size=sm')
        with ui.column().classes('-space-y-6'):
            for reactor_type in opt_config.reactor_families:
                with ui.row().classes('w-full justify-between'):
                    # Main switch
                    switch[reactor_type]=ui.switch(reactor_type, value=True, on_change=lambda e: add_remove_system(e))
                    setattr(switch[reactor_type], 'type', reactor_type)
                    # Subsystem switches
                    with ui.row().classes('pt-3 -space-x-3'):
                        for sub_type in opt_config.reactor_subtypes(reactor_type):
                            subswitch[reactor_type+'-'+sub_type] = ui.button(
                                sub_type, on_click=lambda z: add_remove_subsystem(z)
                            ).props('push rounded dense size=xs')
                            setattr(subswitch[reactor_type+'-'+sub_type], 'model', (reactor_type,sub_type))

            ui.html('<br>')
            with ui.row().classes('w-full justify-between'):
                clearAll = ui.button('Clear', on_click=clearAll).props('size=sm icon=camera align=around')
                enableAll = ui.button('Select All', on_click=selectAll).props('size=sm icon=my_location align=around')
        ui.image('https://atlantium.com/wp-content/uploads/2022/06/HOD-UV-A_Technology_Overview-540x272.jpg').style('height:84px')
ui.html('<p>Atlantium Technologies, Mike Kertser, 2022, <strong>v1.02</strong></p>')

if __name__ == "__main__":
    #ui.run(title='Optimizer', favicon='favicon.ico', host='127.0.0.1', reload=False, show=True)
    ui.run(title='Optimizer', reload=True, show=True)