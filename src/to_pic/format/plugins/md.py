'''
Author: Abel
Date: 2022-12-26 16:11:13
LastEditTime: 2023-12-28 10:18:18
'''
import mistune
from loguru import logger
from playwright._impl._api_types import Error as P_ERR
from playwright.async_api import Page
from mistune.plugins import _plugins
from .html import html_to_png

template = open('statics/template.html', 'r', encoding='utf-8').read()

async def md_to_png(page: Page, md_text: str):
    markdown = mistune.create_markdown(
        escape=False, plugins=list(_plugins.keys()))
    html = markdown(md_text)
    # transform以左上角为基准点，放大两倍。是为了提升截图分辨率
    html = template.replace('！！！ReadyForReplace！！！', html)
    scale = 2
    old_scale = f'scale(1, 1)'
    # 因页面过大最多尝试缩放 3 次
    for _ in range(3):
        try:            
            html = html.replace(old_scale, f'scale({scale}, {scale})')
            return await html_to_png(page, html, '//body/article')
        except P_ERR as e:
            if 'Page.captureScreenshot' in str(e):
                old_scale = f'scale({scale}, {scale})'
                scale /= 2
                logger.warning(f'page too large! trying to scale to {scale * 100:.2f}%')
            else:
                raise e
