import random
import os
from handlers.basehandler import BaseHandler
from utils.imageutils import calculate_aspect_ratio

elegant_room_prompt = os.environ.get("LIBRARY_BOOKSHELF_PROMPT","photo-realistic，no human, best quality, Canon RF 85mm f/1.2L，Nikon AF-S 105mm f/1.4E ED， Eye-level Angle")

class LibraryBookshelf(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/library_bookshelf.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        image_width = self.get_value("width", 512)
        image_height = self.get_value("height", 512)
        
        image_ratio = calculate_aspect_ratio(image_width, image_height)
        
        workflow = self.prompt["prompt"]
        workflow["3"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["5"]["inputs"]["width"] = image_width
        workflow["5"]["inputs"]["height"] = image_height
        workflow["5"]["inputs"]["batch_size"] = self.get_value("batch", 2)
        workflow["6"]["inputs"]["text"] = ",".join([self.get_value("include_text",""), elegant_room_prompt])
        workflow["7"]["inputs"]["text"] = self.get_value("exclude_text","")     
        workflow["29"]["inputs"]["value"] = "_".join(["library_bookshelf", self.get_value("request_id","")])
        workflow["30"]["inputs"]["larger_side"] = image_width if image_width > image_height else image_height
        workflow["32"]["inputs"]["value"] = image_ratio            
