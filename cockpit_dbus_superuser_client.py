import asyncio
from dbus_next.aio import MessageBus
from dbus_next import BusType

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    introspection = await bus.introspect(
        'cockpit.Superuser',
        '/superuser'
    )

    obj = bus.get_proxy_object(
        'cockpit.Superuser',
        '/superuser',
        introspection
    )

    superuser = obj.get_interface('cockpit.Superuser')
    
    
    async def handle_prompt(message, prompt, default, echo, error):
        print("PROMPT:", prompt)
        pw = input("> ")
        await superuser.call_answer(pw)

    # Listen for prompts
    superuser.on_prompt(handle_prompt)

    print("Current:", await superuser.get_current())

    await superuser.call_start('sudo')



asyncio.run(main())
