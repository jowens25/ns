from importlib.resources import files

# These return Traversable objects that work like Path objects
ASSETS_DIR = files('ns').joinpath('ui').joinpath('assets')
INTROSPECTION_DIR = files('ns').joinpath('lib').joinpath('introspection')
