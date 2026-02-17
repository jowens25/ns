#!/usr/bin/env python3
import asyncio
from ns2.dbus import *

def main():
    asyncio.run(service())
    

if __name__ == "__main__":
    main()