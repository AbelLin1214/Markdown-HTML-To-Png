'''
Author: Abel
Date: 2022-12-26 16:08:48
LastEditTime: 2023-12-28 10:23:22
'''
from loguru import logger
from playwright.async_api import Page
from .plugins import html_to_png, md_to_png

@logger.catch
async def transfer(page: Page, type_: str, content: str=None, **kwargs):
    if type_ == 'markdown':
        return await md_to_png(page, content)
    elif type_ == 'html':
        return await html_to_png(page, content, **kwargs)
