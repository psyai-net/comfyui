import random
from handlers.basehandler import BaseHandler


class CascadeSVD(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/cascade_svd.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        workflow = self.prompt["prompt"]
        workflow["56"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["57"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["58"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["54"]["inputs"]["value"] = self.get_value("width", 512)
        workflow["55"]["inputs"]["value"] = self.get_value("height", 512)
        workflow["52"]["inputs"]["value"] = self.get_value("include_text","")
        workflow["53"]["inputs"]["value"] = self.get_value("exclude_text","")        
        

## Example Request Body:

# {
#     "input": {
#         "handler": "CascadeSVD",
#         "include_text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
#         "exclude_text": "text, watermark",
#         "width": 512,
#         "height": 512,
#     }
# }
           
