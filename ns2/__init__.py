__version__ = "0.2.8"

def service():
    from .service import start_ui
    start_ui()