'''
Author: Abel
Date: 2022-12-26 16:27:54
LastEditTime: 2023-06-20 17:12:34
'''
import platform
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def html_to_png(html: str, selector: str=None):
    async with async_playwright() as p:
        b = await p.chromium.launch(
            headless=True
            )
        c = await b.new_context(no_viewport=True)
        p = await c.new_page()
        with TempUrl(content=html) as url:
            await p.goto(url)
            await p.wait_for_load_state('networkidle')  # sometimes need to load js via network
            # await p.keyboard.press('Control+End')  # 滚至页面底部
            selector = selector or '//body'
            ele = await p.wait_for_selector(selector, state='visible')
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
