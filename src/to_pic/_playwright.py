'''
Author: Abel
Date: 2023-12-28 10:15:10
LastEditTime: 2023-12-28 10:15:11
'''
'''
Author: Abel
Date: 2023-12-13 15:44:13
LastEditTime: 2023-12-13 16:00:03
'''
import asyncio
from ._stealth import stealth_js
from pathlib import Path
from contextlib import asynccontextmanager
from playwright.async_api import (
    PlaywrightContextManager, Browser, Playwright)

class ContextManager:
    '''Playwright Context Manager
    
    Automatically manage playwright resources.
    '''
    def __init__(
            self,
            headless: bool = True,
            device: str = None
            ):
        self.headless = headless
        self.device = device
        self._playwright: Playwright = None
        self._browser: Browser = None

    @property
    def device_settings(self) -> dict:
        d = self._playwright.devices.get(self.device, {})
        if not d:
            d = self._playwright.devices.get('Desktop Chrome')
        return d

    async def start(self):
        '''Start playwright'''
        self._playwright = await PlaywrightContextManager().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
            )
    
    async def stop(self):
        '''Stop playwright'''
        if self._playwright:
            if self._browser and self._browser.is_connected():
                await self._browser.close()
            await self._playwright.stop()

    async def restart(self):
        '''Restart playwright'''
        await self.stop()
        await self.start()

    def is_available(self) -> bool:
        '''Check if playwright is available'''
        if self._playwright and self._browser:
            return self._browser.is_connected()
        return False
    
    def start_self_checker(self, interval: int=60):
        '''Auto restart playwright if it is not available'''
        async def _auto_restart():
            while True:
                if not self.is_available():
                    await self.restart()
                await asyncio.sleep(interval)
        return asyncio.create_task(_auto_restart())

    @asynccontextmanager
    async def context_page(self, proxy: str=None, storage_state: str=None):
        '''Create a new page'''
        context = None
        try:
            context = await self.new_context(proxy, storage_state)
            page = await context.new_page()
            yield page
        finally:
            if context is not None:
                try:
                    if storage_state:
                        await context.storage_state(path=storage_state)
                    await context.close()
                except: ...
    
    async def new_context(self, proxy: str=None, storage_state: str=None):
        '''create a new page'''
        path = None
        if storage_state:
            _path = Path(storage_state)
            if _path.is_file():
                path = _path 
        
        context = await self._browser.new_context(
            storage_state=path,
            proxy=None if not proxy else {'server': proxy},
            ignore_https_errors=True,
            # 允许下载
            accept_downloads=True,
            **self.device_settings
        )
        await context.add_init_script(stealth_js)
        return context

    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, *args):
        await self.stop()
