import asyncio
from dataclasses import dataclass, fields
import os
from pprint import pprint
import time
from typing import Any, Optional, Type, TypeVar
from dbus import dbus


from dbus_next import BusType
from dbus_next.signature import Variant, SignatureTree, SignatureType
from dbus_next.aio import MessageBus


def GetNetworkManager(bus: MessageBus):
    file_name = 'org.freedesktop.NetworkManager.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager', introspection)
    return obj.get_interface('org.freedesktop.NetworkManager')

def GetDevice(bus: MessageBus, path : str):
    file_name = 'org.freedesktop.NetworkManager.Device.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Device')


def GetActiveConnection(bus: MessageBus, path : str):
    file_name = 'org.freedesktop.NetworkManager.Connection.Active.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Connection.Active')


def GetIp4Config(bus: MessageBus, path : str):
    file_name = 'org.freedesktop.NetworkManager.IP4Config.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.IP4Config')

def GetIp6Config(bus: MessageBus, path : str):
    file_name = 'org.freedesktop.NetworkManager.IP6Config.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.IP6Config')


def GetSettingsManager(bus: MessageBus):
    file_name = 'org.freedesktop.NetworkManager.Settings.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', "/org/freedesktop/NetworkManager/Settings", introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Settings')

def GetConnection(bus: MessageBus, path : str):
    file_name = 'org.freedesktop.NetworkManager.Settings.Connection.xml'
    with open("introspection/"+file_name, "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Settings.Connection')

#def UnpackSettings(settings: dict):


introspections = None
bus = None

async def GetProperties(proxy):
    data = (await proxy.get_all())[0]
    for f in fields(proxy):
        if f.name in data:
            prop_data = data[f.name]
            if isinstance(prop_data, tuple) and len(prop_data) == 2:
               setattr(proxy, f.name, prop_data[1])
            else:
                setattr(proxy, f.name, prop_data)



async def getAllProperties(cls :dataclass, router, path: str = ''):
    prox = Proxy(Properties(cls(path)), router)
    all_properties = (await prox.get_all())[0]
    if all_properties:
        return cls.from_dict(all_properties)




def from_dict(obj, instance, data: dict[str, tuple[str, Any]]):
    """Convert from dict of {'Prop': ('s', value)} or similar into structured props."""
    for f in fields(obj):
        if f.name in data:
            prop_data = data[f.name]
            if isinstance(prop_data, tuple) and len(prop_data) == 2:
                #filtered[f.name] = prop_data[1]
                setattr(instance, f.name, prop_data[1])
            else:
                print("from dict ERROR")
                #filtered[f.name] = prop_data
                setattr(instance, f.name, prop_data)
    #return cls(**filtered)



def load_introspection():
    introspections = {}

    for file_name in os.listdir("introspection"):
        if file_name.endswith(".xml"):
            print(file_name)
            with open("introspection/"+file_name, "r") as f:
                introspections[file_name] = f.read()

    return introspections

def get_network_manager():
    global introspections, bus
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager', introspections['org.freedesktop.NetworkManager.xml'])
    nm = obj.get_interface('org.freedesktop.NetworkManager')
    return nm

def get_network_device(path):
    global introspections, bus
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspections['org.freedesktop.NetworkManager.Device.xml'])
    return obj.get_interface('org.freedesktop.NetworkManager.Device')

def get_active_connection(path):
    global introspections, bus
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspections['org.freedesktop.NetworkManager.Connection.Active.xml'])
    return obj.get_interface('org.freedesktop.NetworkManager.Connection.Active')


def get_settings_manager():
    global introspections, bus
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager/Settings', introspections['org.freedesktop.NetworkManager.Settings.xml'])
    nm = obj.get_interface('org.freedesktop.NetworkManager.Settings')
    return nm

#def nm_settings_to_dict(settings: dict):
#    new_dict = {}
#    for key, value in settings.items():
#        new_dict[key] = value
#        for k, v in value.items():
#            if isinstance(v.value, list):
#                if k == "address-data":
#                    addresses = []
#                    for addr in v.value:
#                        addresses.append(f"{addr.get("address").value}/{addr.get("prefix").value}")
#                    new_dict[key][k] = addresses
#                else:
#                    new_dict[key][k] = v.value
#
#    return new_dict
#
#def dict_to_nm_settings(settings: dict):
#    new_dict = {}
#    for key, value in settings.items():
#        new_dict[key] = value
#        for k, v in value.items():
#            if isinstance(v.value, list):
#                if k == "address-data":
#                    addresses = []
#                    for addr in v.value:
#                        addresses.append(f"{addr.get("address").value}/{addr.get("prefix").value}")
#                    new_dict[key][k] = addresses
#                else:
#                    new_dict[key][k] = v.value
#
#    return new_dict

async def help_me():
    global introspections, bus


    print(__name__)

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()



    nm = GetNetworkManager(bus)

    sm = GetSettingsManager(bus)

    connections = await sm.call_list_connections()

    pprint(connections)

    devices = await nm.call_get_devices()


    for device_path in devices:

        device = GetDevice(bus, device_path)

        interface = await device.get_interface()


        if interface == 'enp3s0':

            ip4_config_path = await device.get_ip4_config()

            ip4_config = GetIp4Config(bus, ip4_config_path)

            address_data = await ip4_config.get_address_data()
            gateway = await ip4_config.get_gateway()
            print(gateway)
            pprint(address_data)

            active_connection_path = await device.get_active_connection()
            #print(active_connection_path)
            if len(active_connection_path) > 1:
                activeConnection = GetActiveConnection(bus, active_connection_path)

                connection_path = await activeConnection.get_connection()

                #print(connection_path)

                connection = GetConnection(bus, connection_path)

                current_settings = await connection.call_get_settings()

                pprint(current_settings)
                
                if False:
                    current_settings['ipv4']['method'] = Variant('s', 'auto')
                    current_settings['ipv4']['address-data'] = Variant('aa{sv}', [
                        {
                            'address': Variant('s', '10.1.10.106'),
                            'prefix': Variant('u', 24)
                        }
                    ])
                    current_settings['ipv4']['gateway'] = Variant('s', '10.1.10.1')


                    # Remove if exists, do nothing if it doesn't
                    current_settings['ipv4'].pop('addresses', None)
                    current_settings['ipv4'].pop('routes', None)  # Also remove deprecated routes

                    await connection.call_update2(current_settings, 0x1, {})

                    await device.call_reapply(current_settings, 0, 0)

                    pprint(current_settings)


    
    
    
    
    
    #conn = await open_dbus_connection(bus="SYSTEM")
    
    #router = DBusRouter(conn)
    
    # the introspection xml would normally be included in your project, but
    # this is convenient for development
#    introspection = await bus.introspect('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager/Devices/2')
#
#    #print(introspection.tostring())
#    
#    with open("test.xml", 'a') as f:
#        f.write(introspection.tostring())
#
#    with open("./introspection/org.freedesktop.NetworkManager.Device.xml", "r") as f:
#        device_intro = f.read()
#
#    with open("./introspection/org.freedesktop.NetworkManager.xml", 'r') as f:
#        nm_intro = f.read()

   # introspections = load_introspection()
#
   # #obj = bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager', nm_intro)
   # #nm = obj.get_interface('org.freedesktop.NetworkManager')
   # #properties = obj.get_interface('org.freedesktop.DBus.Properties')
#
   # nm = get_network_manager()
#
   # sm = get_settings_manager()
#
   # #connections = await sm.call_list_connections()
   # #print(connections)
#
   # print(await nm.get_all())
#
   # device_paths = await nm.call_get_devices()
   # print(device_paths)
#
##
   # for device in device_paths:
   #     dev = get_network_device(device)
#
#
   #     print( await dev.get_udi())
#
#
  #


    # call methods on the interface (this causes the media player to play)
#    await player.call_play()
#
#    volume = await player.get_volume()
#    print(f'current volume: {volume}, setting to 0.5')
#
    #print(introspection)
#
    #introspection.to_xml()
#
    #with open("NetworkManager.xml", 'x') as f:
    #    f.write(introspection.tostring())
    
    
    
    #nm = Proxy(NetworkManager(), router)
    #device_paths = await nm.GetDevices()
    #
    #for path in device_paths[0]:
#
#
#
    #    deviceProxy = Proxy(Device(path), router) # holds methods
    #    properties = await deviceProxy.get_all() # gets all props





        #print(await deviceProxy.GetAppliedConnection(flags=0))
        #devicePropsProxy = Proxy(Properties(Device(path)), router) # holds properties

        #print(await devicePropsProxy.get_all()) # gets all props

        #await deviceProxy.SomeMethod() # calls some method

        


        #print(await dev.get("Interface"))
#
        #deviceProperties = (await dev.get_all())[0]
#
        #devProps = DeviceProperties.from_dict(deviceProperties)
#
        #print(devProps.ActiveConnection)

#
#        if device.Interface == 'wlp1s0':
#
#            print(device.AvailableConnections)
#
#            print(device.Ip4Config)
#
#
#            config_prox = Proxy(Properties(IP4Config(device.Ip4Config)), router)
#
#            all_config_data = (await config_prox.get_all())[0]
#
#            cfg = IP4ConfigProperties.from_dict(all_config_data)
#
#            print(cfg.AddressData)
#
        
        #print(res2)
        
    #await conn.close()

asyncio.run(help_me())
