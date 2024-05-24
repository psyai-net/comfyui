"""
A FastAPI application that provides text to image conversion.
"""

import sys
import uuid
sys.path.append('/opt/serverless')

# pylint: disable=no-name-in-module
# pylint: disable=wrong-import-position

from fastapi import FastAPI, Request
import uvicorn

from handlers.cascade_svd import CascadeSVD
from handlers.text2image_cascade import Text2ImageCascade
from handlers.text2image import Text2Image
from handlers.elegant_room import ElegantRoom
from handlers.fresh_products import FreshProducts
from handlers.festive_celebration import FestiveCelebration
from handlers.library_bookshelf import LibraryBookshelf
from handlers.upscale_image import ImageUpscaler
from schema import ImageGenerationBase, ImageUpscaleBase


app = FastAPI()


@app.get("/")
def read_root():
    """
    Returns a simple Hello World message.
    """
    return {"Hello": "World"}


def check_request_id(request, payload):
    job_id = request.headers.get("X-Fc-Request-Id")
    if job_id:
        payload["request_id"] = job_id
    else:
        payload["request_id"] = str(uuid.uuid4())


@app.post("/text2image", tags=["images"], summary="stable diffusion 1.5 文生图")
def text2image(request: Request, req: ImageGenerationBase):
    """
    Converts text to image based on the input provided.
    """
    payload = req.model_dump()

    check_request_id(request, payload)

    handler = Text2Image(payload)
    return handler.handle()

@app.post("/elegant_room", tags=["images"], summary="用于生成有质感的居家室内环境，适合用于电商，保险和医疗场景下的直播背景。")
def elegant_room(request:Request, req: ImageGenerationBase):
    payload = req.model_dump()
    
    check_request_id(request, payload)
    
    handler = ElegantRoom(payload)
    
    return handler.handle() 


@app.post("/fresh_products", tags=["images"], summary="cascade文生图")
def fresh_products(request: Request, req: ImageGenerationBase):
    payload = req.model_dump()

    check_request_id(request, payload)

    handler = FreshProducts(payload)
    return handler.handle()


@app.post("/festive_celebration", tags=["images"], summary="cascade文生图")
def festive_celebration(request: Request, req: ImageGenerationBase):
    payload = req.model_dump()
    
    check_request_id(request, payload)
    
    handler = FestiveCelebration(payload)
    return handler.handle()


@app.post("/library_bookshelf", tags=["images"], summary="cascade文生图")
def library_bookshelf(request: Request, req: ImageGenerationBase):
    payload = req.model_dump()
    
    check_request_id(request, payload)
    
    handler = LibraryBookshelf(payload)
    return handler.handle()


@app.post("/text2image_cascade_simple", tags=["images"], summary="简单的cascade文生图")
def text2image_cascade_simple(request: Request, req: ImageGenerationBase):
    payload = req.model_dump()

    check_request_id(request, payload)

    handler = Text2ImageCascade(payload)
    return handler.handle()


@app.post("/cascade_svd_simple", tags=["videos"], summary="cascade + svd 文生视频")
def cascade_svd_simple(request: Request, req: ImageGenerationBase):
    payload = req.model_dump()

    check_request_id(request, payload)

    handler = CascadeSVD(payload)
    return handler.handle()


@app.post("/image_upscale", tags=["images"], summary="图片超分")
def image_upscale(request: Request, req: ImageUpscaleBase):
    payload = req.model_dump()
      
    check_request_id(request, payload)
    
    handler = ImageUpscaler(payload)
    return handler.handle()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
