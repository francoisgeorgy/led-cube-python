import importlib, json

from ledcube.emulator.logger import Logger

adapters = [
    {
        'path': 'ledcube.emulator.adapters.cube_browser_adapter.adapter',
        'class': 'CubeBrowserAdapter',
        'type': 'cube_browser'
    },
    {
        'path': 'ledcube.emulator.adapters.browser_adapter.adapter',
        'class': 'BrowserAdapter',
        'type': 'browser'
    },
    {
        'path': 'ledcube.emulator.adapters.pygame_adapter',
        'class': 'PygameAdapter',
        'type': 'pygame'
    },
    {
        'path': 'ledcube.emulator.adapters.sixel_adapter',
        'class': 'SixelAdapter',
        'type': 'sixel'
    },
    {
        'path': 'ledcube.emulator.adapters.terminal_adapter',
        'class': 'TerminalAdapter',
        'type': 'terminal'
    },
    {
        'path': 'ledcube.emulator.adapters.tkinter_adapter',
        'class': 'TkinterAdapter',
        'type': 'tkinter'
    },
    {
        'path': 'ledcube.emulator.adapters.turtle_adapter',
        'class': 'TurtleAdapter',
        'type': 'turtle'
    }
]

ADAPTER_TYPES = {}

try:
    with open("emulator_config.json") as config_file:
        suppress_adapter_load_errors = json.load(config_file).get("suppress_adapter_load_errors", False)
except:
    suppress_adapter_load_errors = False

for adapter in adapters:
    package_path = adapter.get('path')
    adapter_class = adapter.get('class')
    adapter_name = adapter.get('type')
    try:
        package = importlib.import_module(package_path)
        adapter = getattr(package, adapter_class)

        ADAPTER_TYPES[adapter_name] = adapter
    except Exception as ex:
        if suppress_adapter_load_errors: continue

        Logger.exception(f'''
Failed to load {adapter_class} for "{adapter_name}" display adapter!

If this is not your configured display adapter, the emulator will continue to load.

You can suppress this error in the `emulator_config.json` by adding:

  "suppress_adapter_load_errors": true

'''
        )
