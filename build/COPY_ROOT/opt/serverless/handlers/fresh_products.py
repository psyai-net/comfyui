import random
import os
from handlers.basehandler import BaseHandler
from utils.imageutils import calculate_aspect_ratio

elegant_room_prompt = os.environ.get("FRESH_PRODUCTS_PROMPT","masterpiece,best quality")

class FreshProducts(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/fresh_products.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        image_width = self.get_value("width", 512)
        image_height = self.get_value("height", 512)
        
        image_ratio = calculate_aspect_ratio(image_width, image_height)
        
        workflow = self.prompt["prompt"]
        # workflow["3"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["5"]["inputs"]["width"] = image_width
        workflow["5"]["inputs"]["height"] = image_height
        workflow["5"]["inputs"]["batch_size"] = self.get_value("batch", 2)
        workflow["6"]["inputs"]["text"] = ",".join([self.get_value("include_text",""), elegant_room_prompt])
        workflow["7"]["inputs"]["text"] = self.get_value("exclude_text","")     
        workflow["29"]["inputs"]["value"] = "_".join(["fresh_products", self.get_value("request_id","")])
        workflow["31"]["inputs"]["larger_side"] = image_width if image_width > image_height else image_height
        workflow["31"]["inputs"]["side_ratio"] = image_ratio            
