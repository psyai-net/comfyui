import random
from handlers.basehandler import BaseHandler



class Text2ImageCascade(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/text2image_cascade.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        workflow = self.prompt["prompt"]
        workflow["47"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["49"]["inputs"]["seed"] = random.randint(0,2**32)
        workflow["43"]["inputs"]["value"] = self.get_value("width", 512)
        workflow["44"]["inputs"]["value"] = self.get_value("height", 512)
        workflow["42"]["inputs"]["value"] = self.get_value("include_text","")
        workflow["46"]["inputs"]["value"] = self.get_value("exclude_text","")
        
        
# Example Request Body:

# {
#     "input": {
#         "handler": "Text2Image_Cascade",
#         "include_text": "An image of a young woman with an olive complexion and short, layered hair with brown to blonde highlights. She is looking down at her smartphone with an expression of concentration. She wears a black button-up shirt, slightly open to reveal a coral pink t-shirt underneath. The background is a blurred cityscape, urban environment. The woman has a natural makeup look and carries a brown leather bag with a strap acrosser body.",
#         "exclude_text": "text, watermark",
#         "width": 512,
#         "height": 512
#     }
# }
           
