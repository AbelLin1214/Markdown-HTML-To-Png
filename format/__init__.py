'''
Author: Abel
Date: 2022-12-26 16:08:48
LastEditTime: 2022-12-27 16:47:31
'''
from loguru import logger
from format.plugins import html_to_png, md_to_png

@logger.catch
async def transfer(type_: str, content: str, **kwargs):
    if type_ == 'markdown':
        return await md_to_png(content)
    elif type_ == 'html':
        return await html_to_png(content, **kwargs)
