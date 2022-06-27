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

# This is a temporary procedure and will be replaced
def update():
    table.options.rowData[0].age += 1

class PQUVT:
    def __init__(self):
        self.minP = 40
        self.maxP = 100
        self.minQ = 10
        self.maxQ = 2000

#%% --- Main Frame ---

pquvt = PQUVT()

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


with ui.row():
    with ui.column():
        with ui.row().classes('flex items-stretch'):
            with ui.card().classes('max-w-full'):
                ui.label('Variables:').classes('text-h7 underline')
                with ui.row().classes('max-w-full space-x-2'): #Power
                    P_check = ui.checkbox()
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minPower = ui.slider(min=pquvt.minP, max=pquvt.maxP, value=pquvt.minP,on_change=lambda: power('min')).bind_value_to(pquvt,'minP').props('label')
                        with ui.row() as row:
                            ui.label('Minimum Power:')
                            ui.label().bind_text_from(minPower, 'value')
                            ui.label('[%]')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxPower = ui.slider(min=pquvt.minP, max=pquvt.maxP, value=pquvt.maxP,on_change=lambda: power('max')).bind_value_to(pquvt,'maxP').props('label')
                        with ui.row() as row:
                            ui.label('Maximum Power:')
                            ui.label().bind_text_from(maxPower, 'value')
                            ui.label('[%]')

                with ui.row().classes('max-w-full space-x-2'): # Flow
                    Q_check = ui.checkbox()
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minFlow = ui.slider(min=pquvt.minQ, max=pquvt.maxQ, value=pquvt.minQ,on_change=lambda: flow('min')).bind_value_to(pquvt,'minQ').props('label')
                        with ui.row() as row:
                            ui.label('Minimum Flow: [m^3/h]')
                            ui.label().bind_text_from(minFlow, 'value')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxFlow = ui.slider(min=pquvt.minQ, max=pquvt.maxQ, value=pquvt.maxQ,on_change=lambda: flow('max')).bind_value_to(pquvt,'maxQ').props('label')
                        with ui.row() as row:
                            ui.label('Maximum Flow: [m^3/h]')
                            ui.label().bind_text_from(maxFlow, 'value')

                with ui.row().classes('max-w-full space-x-2'): # UVT
                    Q_check = ui.checkbox()
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        minUVT = ui.slider(min=0, max=100, value=0).props('label')
                        with ui.row() as row:
                            ui.label('Minimum UVT: [%-1cm]')
                            ui.label().bind_text_from(minUVT, 'value')
                    with ui.column().classes('max-w-full -space-y-5 w-52'):
                        maxUVT = ui.slider(min=0, max=100, value=40).props('label')
                        with ui.row() as row:
                            ui.label('Maximum UVT: [%-1cm]')
                            ui.label().bind_text_from(maxUVT, 'value')
            # chart.options.series[0].data[:] = random(2)
            with ui.card().classes('max-h-fit'):
                ui.label('Charts:').classes('text-h7 underline')
                chart = ui.chart({
                    'title': False,
                    'chart': {'type': 'bar'},
                    'xAxis': {'categories': ['A', 'B']},
                    'series': [
                        {'name': 'Alpha', 'data': [0.1, 0.2]},
                        {'name': 'Beta', 'data': [0.3, 0.4]},
                    ],
                }).classes('h-64')

        with ui.card().classes('bg-yellow-300 w-full h-48'):
            table = ui.table({
                    'columnDefs': [
                        {'headerName': 'Name', 'field': 'name'},
                        {'headerName': 'Age', 'field': 'age'},
                    ],
                    'rowData': [
                        {'name': 'Alice', 'age': 18},
                        {'name': 'Bob', 'age': 21},
                        {'name': 'Carol', 'age': 42},
                    ],
                })
        ui.button('Optimize', on_click=update)
    # Constrains
    with ui.card().classes('w-64'):
        ui.label('Constrains:').classes('text-h7 underline')
        with ui.expansion('Specific reactors', icon='settings').classes('w-full'):
            with ui.column():
                for system in opt_config.systems.keys():
                    ui.checkbox(system, value=True)


if __name__ == "__main__":
    ui.run(title = 'Optimizer', host='127.0.0.1', reload=False, favicon='configuration.ico',show=False)

