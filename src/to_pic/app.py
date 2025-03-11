'''
Author: Abel
Date: 2022-12-26 17:18:18
LastEditTime: 2025-03-11 10:32:17
'''
import os
from pathlib import Path
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import Response
from .format import transfer
from typing import Literal
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ._playwright import ContextManager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_app: FastAPI):
    '''应用生命周期管理器'''
    temp_dir = Path('./temp')
    if not temp_dir.exists():
        temp_dir.mkdir()

    global CM
    CM = ContextManager(
        headless=os.getenv('HEADLESS', 'True') == 'True'
    )
    await CM.start()
    yield

app = FastAPI(lifespan=lifespan)
app.mount('/statics', StaticFiles(directory='./statics'), name='statics')
N = 0

def png_response(img_bytes: bytes, image_type: str):
    return Response(
        img_bytes,
        media_type=f'image/{image_type}'
    )

class Item(BaseModel):
    type_: Literal['markdown', 'html'] = Field(..., alias='type', examples=['html'], description='类型')
    content: str = Field(None, examples=['<h1>hello world</h1>'], description='内容, 同时指定url时只会使用url')
    selector: str = Field(None, examples=['//h1'], description='元素选择器, 仅当type为html时有效')
    proxy: str = Field(None, examples=['http://localhost:8888'], description='代理地址, 格式为http://ip:port')
    url: str = Field(None, examples=['https://www.baidu.com'], description='页面地址')
    timeout: int = Field(30, examples=[30], description='页面等待超时时间，单位秒，仅当url不为空时有效')
    image_type: Literal['png', 'jpeg'] = Field('png', examples=['png'], description='图片格式')
    quality: int = Field(100, examples=[100], description='图片质量，仅对jpeg有效')

@app.get('/temp/{file_name}', include_in_schema=False)
async def to_temp_dir(file_name: str):
    return FileResponse(f'./temp/{file_name}')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./statics/favicon.ico')

@app.post('/api/to_png')
async def to_png(item: Item):
    global N
    N += 1
    logger.info(f'[No.{N}] Received a format req, type: {item.type_}')
    if not item.content and not item.url:
        return {'code': -1, 'msg': '请求错误: url和content不能同时为空'}
    
    async with CM.context_page(proxy=item.proxy) as page:
        page.set_default_timeout(item.timeout * 1000)
        img_bytes = await transfer(
            page,
            **item.model_dump(exclude=['proxy', 'timeout'])
            )
        if not img_bytes:
            return {'code': -1, 'msg': '请求错误：不支持当前格式或等待超时'}
        
    return png_response(img_bytes, item.image_type)

@app.get("/health")
async def health():
    return {"success": True}
