'''
Author: Abel
Date: 2022-12-26 17:18:18
LastEditTime: 2023-12-27 10:03:33
'''
from pathlib import Path
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import Response
from .format import transfer
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
    type_: str = Field(..., alias='type')
    content: str = None
    selector: str = None
    proxy: str = None
    url: str = None

@app.get('/temp/{file_name}')
async def to_temp_dir(file_name: str):
    return FileResponse(f'./temp/{file_name}')

@app.get('/favicon.ico')
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
        **item.dict()
        )
    if not img_bytes:
        return {'code': -1, 'msg': '请求错误：不支持当前格式'}
    return png_response(img_bytes)
