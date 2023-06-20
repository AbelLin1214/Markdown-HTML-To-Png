'''
Author: Abel
Date: 2022-12-26 17:18:18
LastEditTime: 2023-06-20 17:18:23
'''
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import Response
from format import transfer
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/statics', StaticFiles(directory='./statics'), name='statics')
N = 0

def png_response(img_bytes: bytes):
    return Response(
        img_bytes,
        media_type='application/png',
        # headers={'Content-Disposition': 'attachment;filename=result.png'}
        headers={'Content-Type': 'image/png'}
    )

class Item(BaseModel):
    type: str
    content: str
    selector: str = None

@app.post('/api/to_png')
async def to_png(item: Item):
    global N
    N += 1
    logger.info(f'[No.{N}] Received a format req, type: {item.type}')
    img_bytes = await transfer(item.type, item.content, selector=item.selector)
    if not img_bytes:
        return {'code': -1, 'msg': '请求错误：不支持当前格式'}
    return png_response(img_bytes)
