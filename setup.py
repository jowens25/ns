#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="ns",
    version="0.2.2",
    description="Novus power products configuration tool",
    author="jaowens14",
    author_email="jaowens14@protonmail.com",
    license="MIT",
    python_requires=">=3.11, <3.13",
    packages=find_packages("src"),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'ns=ns.ui.main:main',  # Adjust 'main' to your actual function
        ],
    },

    package_data={
        'ns': [
            'assets/**/*',
            'introspection/**/*',
        ],
    },

    install_requires=[
        "aiofiles", "aiohappyeyeballs", "aiohttp", "aiosignal", "annotated-doc",
        "annotated-types", "anyio", "attrs", "beautifulsoup4", "bidict", "bs4",
        "certifi", "charset-normalizer", "click", "dbus-next", "docutils",
        "fastapi", "frozenlist", "h11", "httpcore", "httptools", "httpx", "idna",
        "ifaddr", "itsdangerous", "jinja2", "markdown2", "markupsafe", "multidict",
        "narwhals", "nicegui", "numpy", "orjson", "packaging", "pam", "pandas",
        "plotly", "propcache", "pydantic", "pydantic-core", "pygments",
        "python-dateutil", "python-dotenv", "python-engineio", "python-multipart",
        "python-pam", "python-socketio", "pyinstaller", "pyyaml", "requests",
        "simple-websocket", "six", "soupsieve", "typing-inspection",
        "typing-extensions", "urllib3", "uvicorn", "uvloop", "watchfiles",
        "websockets", "wheel2deb", "wsproto", "yarl", 
    ],
)