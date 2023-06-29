'''
Author: Abel
Date: 2022-12-26 16:27:54
LastEditTime: 2023-06-29 09:28:16
'''
import time
from pathlib import Path
from playwright.async_api import async_playwright

class NewPage:
    '''新建页面处理器'''
    __playwright = None
    __browser = None
    
    @classmethod
    async def get_playwright(cls):
        '''获取playwright实例'''
        if cls.__playwright is None:
            cls.__playwright = await async_playwright().start()
        return cls.__playwright
    
    @classmethod
    async def get_browser(cls):
        '''获取浏览器实例'''
        if cls.__browser is None:
            cls.__browser = await cls.__playwright.chromium.launch(
                headless=True
                )
        return cls.__browser
    
    @classmethod
    async def start(cls):
        '''启动playwright和浏览器'''
        await cls.get_playwright()
        await cls.get_browser()
    
    @classmethod
    async def close(cls):
        '''关闭playwright和浏览器'''
        if cls.__browser is not None:
            await cls.__browser.close()
        if cls.__playwright is not None:
            await cls.__playwright.stop()
    
    async def __aenter__(self):
        '''新建页面'''
        await self.start()
        self.__context = await self.__browser.new_context(no_viewport=True)
        self.__page = await self.__context.new_page()
        return self.__page

    async def __aexit__(self, exc_type, exc, tb):
        '''关闭页面和上下文'''
        await self.__context.close()

async def html_to_png(html: str, selector: str=None):
    '''将html转换为png'''
    async with NewPage() as page:
        with TempUrl(content=html) as url:
            await page.goto(url)
            await page.wait_for_load_state('networkidle')  # sometimes need to load js via network
            # await page.keyboard.press('Control+End')  # 滚至页面底部
            selector = selector or '//body'
            ele = await page.wait_for_selector(selector, state='visible')
            img_bytes = await ele.screenshot(path='statics/temp/temp.png', scale='css')
            return img_bytes

class TempUrl:
    '''临时文件处理器'''
    def __init__(self, content: str):
        self.content = content
        self.dir = 'statics/temp'
        self.hostname = 'http://localhost:19527'
        self.file = None
    
    def __enter__(self):
        '''将内容写入一个随机生成的html，返回URL'''
        d = Path(self.dir)
        name = f'{time.time() * 1000000:.0f}.html'  # 微秒防重
        self.file = d.joinpath(name)
        self.file.write_text(self.content, 'utf-8')
        self.file.touch()
        return f'{self.hostname}/{self.file}'

    def __exit__(self, *args):
        '''将这个文件删除'''
        if self.file:
            self.file.unlink(True)
