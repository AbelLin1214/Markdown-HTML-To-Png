'''
Author: Abel
Date: 2022-12-26 17:18:18
LastEditTime: 2023-12-27 10:35:32
'''
from pathlib import Path
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import Response
from .format import transfer
from typing import Literal
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
app.mount('/statics', StaticFiles(directory='./statics'), name='statics')
N = 0

temp_dir = Path('./temp')
if not temp_dir.exists():
    temp_dir.mkdir()

def png_response(img_bytes: bytes):
    return Response(
        img_bytes,
        media_type='application/png',
        headers={'Content-Type': 'image/png'}
    )

class Item(BaseModel):
    type_: Literal['markdown', 'html'] = Field(..., alias='type', examples=['html'])
    content: str = Field(None, examples=['<h1>hello world</h1>'])
    selector: str = Field(None, examples=['//h1'])
    proxy: str = Field(None, examples=['http://localhost:8888'])
    url: str = Field(None, examples=['https://www.baidu.com'])

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
    if item.content is None and item.url is None:
        return {'code': -1, 'msg': '请求错误: url和content不能同时为空'}
    img_bytes = await transfer(
        **item.model_dump()
        )
    if not img_bytes:
        return {'code': -1, 'msg': '请求错误：不支持当前格式'}
    return png_response(img_bytes)
