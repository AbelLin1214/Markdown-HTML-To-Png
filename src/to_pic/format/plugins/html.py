'''
Author: Abel
Date: 2022-12-26 16:27:54
LastEditTime: 2023-12-28 12:09:30
'''
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import Page, Request
from typing import Literal

class RequestListener:
    '''请求监听器'''
    def __init__(self):
        self._last_request_time = time.time()
    
    async def listen(self, request: Request):
        '''监听请求'''
        self._last_request_time = time.time()

    def network_idle(self, timeout: float=0.5):
        '''判断网络是否空闲'''
        return time.time() - self._last_request_time > timeout
    
    async def wait_for_network_idle(self, page: Page, timeout: float):
        '''等待网络空闲'''
        while not self.network_idle(timeout):
            await page.wait_for_timeout(0.1)

async def html_to_png(
        page: Page,
        html: str=None,
        selector: str=None,
        url: str=None,
        image_type: Literal['png', 'jpeg']='png',
        quality: int=100
        ):
    '''将html转换为png'''
    quality = None if image_type == 'png' else quality
    if url:
        listener = RequestListener()
        page.on('request', listener.listen)
        await page.goto(url)
        # wait_for_load_state如果已经达成了networkidle
        # 再次调用会因为没有新的请求而阻塞
        # 而部分页面在达成load状态后就不会再发起新的请求
        # 所以不能直接使用page.wait_for_loadstate('networkidle')
        await listener.wait_for_network_idle(page, 1)
        if selector:
            ele = await page.wait_for_selector(selector, state='visible')
            img_bytes = await ele.screenshot(
                type=image_type,
                path=f'temp/temp.{image_type}',
                scale='css', quality=quality
            )
        else:
            img_bytes = await page.screenshot(
                type=image_type,
                path=f'temp/temp.{image_type}',
                full_page=True, quality=quality
            )
        return img_bytes

    with TempUrl(content=html) as url:
        await page.goto(url)
        await page.wait_for_load_state('networkidle')  # sometimes need to load js via network
        # await page.keyboard.press('Control+End')  # 滚至页面底部
        selector = selector or '//body'
        ele = await page.wait_for_selector(selector, state='visible')
        img_bytes = await ele.screenshot(path='temp/temp.png', scale='css')
        return img_bytes

class TempUrl:
    '''临时文件处理器'''
    def __init__(self, content: str):
        self.content = content
        self.dir = 'temp'
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
