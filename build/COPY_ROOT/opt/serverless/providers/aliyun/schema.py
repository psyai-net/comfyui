from pydantic import BaseModel, Field

    
class ImageGenerationBase(BaseModel):
    include_text: str = Field(description="positive text")
    exclude_text: str = Field(description="negative text")
    width: int = Field(default=512, description="image width")
    height: int = Field(default=512, description="image height")
    batch: int = Field(default=1, description="batch num")


class ImageUpscaleBase(BaseModel):
    image : str = Field(description="image url")