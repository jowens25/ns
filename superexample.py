import asyncio
import logging
from typing import Optional, Callable, Dict
from nicegui import ui, app
from dbus_next.aio import MessageBus, ProxyObject
from dbus_next.constants import BusType
from dbus_next import Variant

logger = logging.getLogger(__name__)


class SuperuserClient:
    """Client for interacting with the D-Bus Superuser service."""
    
    def __init__(self):
        self.bus: Optional[MessageBus] = None
        self.proxy: Optional[ProxyObject] = None
        self.interface = None
        self._status_callback: Optional[Callable] = None
        self._prompt_callback: Optional[Callable] = None
        self._current = 'none'
        
    async def connect(self):
        """Connect to the D-Bus service."""
        try:
            # Connect to system bus
            self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            
            # Get proxy object for the service
            introspection = await self.bus.introspect('com.novus.ns', '/com/novus/ns')
            self.proxy = self.bus.get_proxy_object('com.novus.ns', '/com/novus/ns', introspection)
            
            # Get the interface
            self.interface = self.proxy.get_interface('com.novus.ns.super')
            
            # Subscribe to signals
            self.interface.on_prompt(self._on_prompt)
            
            # Subscribe to property changes
            props_interface = self.proxy.get_interface('org.freedesktop.DBus.Properties')
            props_interface.on_properties_changed(self._on_properties_changed)
            
            # Get initial state
            self._current = await self.interface.get_current()
            
            logger.info("Connected to superuser D-Bus service")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to D-Bus service: {e}")
            return False
    
    def _on_prompt(self, message: str, prompt: str, default: str, echo: bool, error: str):
        """Handle Prompt signal from D-Bus."""
        logger.debug(f"Received prompt: {prompt}")
        if self._prompt_callback:
            self._prompt_callback(prompt, echo, error)
    
    def _on_properties_changed(self, interface_name: str, changed: Dict, invalidated: list):
        """Handle property changes."""
        if 'Current' in changed:
            self._current = changed['Current'].value
            logger.debug(f"Current state changed to: {self._current}")
            if self._status_callback:
                # Determine state for callback
                if self._current == 'none':
                    self._status_callback('stopped', 'none')
                elif self._current == 'init':
                    self._status_callback('init', '')
                else:
                    self._status_callback('active', self._current)
    
    def set_status_callback(self, callback: Callable):
        """Register callback for status updates."""
        self._status_callback = callback
        
    def set_prompt_callback(self, callback: Callable):
        """Register callback for authentication prompts."""
        self._prompt_callback = callback
    
    async def start(self, bridge: str = 'any') -> bool:
        """Request superuser access."""
        if not self.interface:
            logger.error("Not connected to D-Bus service")
            return False
            
        try:
            await self.interface.call_start(bridge)
            return True
        except Exception as e:
            logger.error(f"Failed to start superuser: {e}")
            if self._status_callback:
                self._status_callback('failed', str(e))
            return False
    
    async def answer(self, password: str):
        """Submit password response to pending prompt."""
        if self.interface:
            try:
                await self.interface.call_answer(password)
            except Exception as e:
                logger.error(f"Failed to submit answer: {e}")
    
    async def stop(self):
        """Stop superuser session."""
        if self.interface:
            try:
                await self.interface.call_stop()
            except Exception as e:
                logger.error(f"Failed to stop superuser: {e}")
    
    @property
    def current_state(self) -> str:
        """Get current superuser state."""
        return self._current
    
    @property
    def is_active(self) -> bool:
        """Check if superuser is currently active."""
        return self._current not in ['none', 'init']


# Global client instance
superuser_client = SuperuserClient()


# NiceGUI UI Components
class SuperuserDialog:
    """Dialog for superuser authentication."""
    
    def __init__(self):
        self.dialog = None
        self.password_input = None
        self.status_label = None
        
    def show(self, prompt: str = "Password:", echo: bool = False, error: str = ""):
        """Show authentication dialog."""
        with ui.dialog() as self.dialog, ui.card().classes('w-96'):
            ui.label('Administrator Access Required').classes('text-xl font-bold mb-4')
            
            if error:
                ui.label(error).classes('text-red-500 mb-2')
            
            ui.label(prompt).classes('mb-2')
            
            self.password_input = ui.input(
                placeholder='Enter password',
                password=not echo,
                on_change=lambda: self.status_label.set_text('')
            ).classes('w-full').props('autofocus')
            
            self.password_input.on('keydown.enter', self.submit)
            
            self.status_label = ui.label('').classes('text-sm text-gray-500 mt-2')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=self.cancel).props('flat')
                ui.button('Authenticate', on_click=self.submit).props('color=primary')
        
        self.dialog.open()
    
    async def submit(self):
        """Submit password."""
        password = self.password_input.value
        if password:
            self.status_label.set_text('Authenticating...')
            await superuser_client.answer(password)
        else:
            self.status_label.set_text('Please enter a password')
    
    async def cancel(self):
        """Cancel authentication."""
        await superuser_client.answer('')  # Empty string = cancel
        if self.dialog:
            self.dialog.close()
    
    def close(self):
        """Close dialog."""
        if self.dialog:
            self.dialog.close()


# Example NiceGUI Application
@ui.page('/')
async def main_page():
    status_badge = ui.badge('Not Active', color='gray').classes('mb-4')
    action_btn = ui.button('Request Admin Access', on_click=lambda: None)
    log_area = ui.textarea(label='Log', value='').classes('w-full h-40').props('readonly')
    
    dialog = SuperuserDialog()
    
    def log(message: str):
        """Add message to log."""
        current = log_area.value
        log_area.value = f"{current}\n{message}" if current else message
    
    def update_status(state: str, details: str):
        """Update UI status."""
        if state == 'active':
            status_badge.set_text(f'Active ({details})')
            status_badge.props('color=green')
            action_btn.set_text('Stop Admin Access')
            action_btn.set_enabled(True)
            dialog.close()
            log(f"Superuser access granted: {details}")
        elif state == 'init':
            status_badge.set_text('Authenticating...')
            status_badge.props('color=orange')
            action_btn.set_enabled(False)
        elif state == 'stopped':
            status_badge.set_text('Not Active')
            status_badge.props('color=gray')
            action_btn.set_text('Request Admin Access')
            action_btn.set_enabled(True)
            log("Superuser access stopped")
        elif state == 'failed':
            status_badge.set_text('Failed')
            status_badge.props('color=red')
            action_btn.set_enabled(True)
            log(f"Authentication failed: {details}")
            dialog.close()
    
    def show_prompt(prompt: str, echo: bool, error: str):
        """Show authentication prompt."""
        log(f"Authentication requested: {prompt}")
        dialog.show(prompt, echo, error)
    
    async def toggle_superuser():
        """Toggle superuser access."""
        if superuser_client.is_active:
            await superuser_client.stop()
        else:
            log("Requesting administrator access...")
            update_status('init', '')
            await superuser_client.start()
    
    # Register callbacks
    superuser_client.set_status_callback(update_status)
    superuser_client.set_prompt_callback(show_prompt)
    
    # Update button handler
    action_btn.on_click(toggle_superuser)
    
    # Initialize status
    log("Application started")
    if superuser_client.is_active:
        update_status('active', superuser_client.current_state)


# Application startup
@app.on_startup
async def startup():
    """Connect to D-Bus service on startup."""
    success = await superuser_client.connect()
    if success:
        logger.info("Connected to superuser D-Bus service")
    else:
        logger.error("Failed to connect to superuser D-Bus service")


@app.on_shutdown
async def shutdown():
    """Cleanup on shutdown."""
    if superuser_client.bus:
        superuser_client.bus.disconnect()


if __name__ in {"__main__", "__mp_main__"}:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    ui.run(
        title='Superuser Demo',
        port=8080,
        reload=False
    )