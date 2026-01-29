from nicegui import ui

continents = [
    'Asia',
    'Africa',
    'Antarctica',
    'Europe',
    'Oceania',
    'North America',
    'South America',
]
ui.select(options=continents, multiple=True, with_input=True, on_change=lambda e: ui.notify(e.value)).classes('w-40')

ui.run()

