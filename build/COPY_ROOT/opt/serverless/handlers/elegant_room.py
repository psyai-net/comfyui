import random
import os
from handlers.basehandler import BaseHandler

elegant_room_prompt = os.environ.get("ELEGANT_ROOM_PROMPT","photo-realistic， Canon RF 85mm f/1.2L，Nikon AF-S 105mm f/1.4E ED， Eye-level Angle")

class ElegantRoom(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/elegant_room.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        workflow = self.prompt["prompt"]
        workflow["3"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["5"]["inputs"]["width"] = self.get_value("width", 512)
        workflow["5"]["inputs"]["height"] = self.get_value("height", 512)
        workflow["5"]["inputs"]["batch_size"] = self.get_value("batch", 2)
        workflow["6"]["inputs"]["text"] = ",".join([self.get_value("include_text",""), elegant_room_prompt])
        workflow["7"]["inputs"]["text"] = self.get_value("exclude_text","")     
        workflow["29"]["inputs"]["text"] = "_".join(["elegant_room", self.get_value("request_id","")])
