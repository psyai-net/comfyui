from handlers.basehandler import BaseHandler


class ImageUpscaler(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/upscale_image.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
              
            
    def apply_modifiers(self):
        workflow = self.prompt["prompt"]
        workflow["43"]["inputs"]["image"] = self.get_value("image","")
        workflow["40"]["inputs"]["value"] = self.get_value("request_id", "")
