from pathlib import Path
# Works in dev, packaging, systemd, deb install
BASE_DIR = Path(__file__).parent.parent.parent  # src/ns/ui → project root
ASSETS_DIR = BASE_DIR / "assets"
INTROSPECTION_DIR = BASE_DIR / "introspection"