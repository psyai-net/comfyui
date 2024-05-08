import sys
sys.path.append('/opt/serverless')

# pylint: disable=wrong-import-position
import uuid
from pydoc import locate
import runpod


def get_handler(payload):
    try:
        c_name = payload["handler"]
        m_name = c_name.lower()
        handler_class = locate(f"handlers.{m_name}.{c_name}")
        handler = handler_class(payload)
    except Exception as e:
        print(e)
        raise
        
    return handler
  

# Handler to be specified in input.handler
def worker(event):
    result = {}
    try:
        payload = event["input"]
        if is_test_job(event):
            payload["request_id"] = str(uuid.uuid4())
        else:
            payload["request_id"] = event["id"]
        handler = get_handler(payload)
        result = handler.handle()
    except KeyError as e:
        result = {}
        result["error"] = str(e)
    
    return result

def is_test_job(event):
    test_values = [
        "local_test",
        "test_job"
    ]
    return event["id"] in test_values

runpod.serverless.start({
    "handler": worker
})