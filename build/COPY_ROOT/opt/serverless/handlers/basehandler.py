import json
import datetime
import time
import os
import base64
import shutil
import threading
import requests
from utils.s3utils import S3utils
from utils.network import Network
from utils.filesystem import Filesystem


class BaseHandler:
    ENDPOINT_PROMPT = "http://127.0.0.1:18188/prompt"
    ENDPOINT_QUEUE = "http://127.0.0.1:18188/queue"
    ENDPOINT_HISTORY = "http://127.0.0.1:18188/history"
    INPUT_DIR = f"{os.environ.get('WORKSPACE')}/ComfyUI/input/"
    OUTPUT_DIR = f"{os.environ.get('WORKSPACE')}/ComfyUI/output/"

    request_id = None
    comfyui_job_id = None

    def __init__(self, payload, workflow_json=None):
        self.job_time_received = datetime.datetime.now()
        self.payload = payload
        self.workflow_json = workflow_json
        self.s3utils = S3utils(self.get_s3_settings())
        self.request_id = str(self.get_value(
            "request_id",
            None
        )
        )
        self.set_prompt()
        self.result = {
            "images": [],
            "timings": {}
        }
        self.job_time_queued = None
        self.job_time_processed = None
        self.job_time_completed = None

    def set_prompt(self):
        if self.workflow_json:
            with open(self.workflow_json, 'r', encoding='utf-8') as f:
                self.prompt = {"prompt": json.load(f)}
        else:
            self.prompt = {"prompt": self.payload["workflow_json"]}

    def get_value(self, key, default=None):
        if key not in self.payload and default is None:
            raise IndexError(f"{key} required but not set")
        if key not in self.payload:
            return default
        if Network.is_url(self.payload[key]) and not (key.startswith("aws_") or key.startswith("webhook_")):
            return self.get_url_content(self.payload[key])
        
        return self.payload[key]

    def get_input_dir(self):
        return f"{self.INPUT_DIR}"

    def get_output_dir(self):
        return f"{self.OUTPUT_DIR}"

    def replace_urls(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self.replace_urls(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                data[i] = self.replace_urls(item)
        elif isinstance(data, str) and Network.is_url(data):
            data = self.get_url_content(data)
        return data

    def get_url_content(self, url):
        existing_file = Filesystem.find_input_file(
            self.get_input_dir(),
            Network.get_url_hash(url)
        )
        if existing_file:
            return os.path.basename(existing_file)

        return os.path.basename(Network.download_file(
            url,
            self.get_input_dir(),
            self.request_id
        ))

    def is_server_ready(self):
        try:
            req = requests.head(self.ENDPOINT_PROMPT, timeout=5)
            return True if req.status_code == 200 else False
        except requests.RequestException:
            return False

    def queue_job(self, timeout=30):
        try:
            self.job_time_queued = datetime.datetime.now()
            while ((datetime.datetime.now() - self.job_time_queued).seconds < timeout) and not self.is_server_ready():
                print("waiting for local server...")
                time.sleep(0.5)

            if not self.is_server_ready():
                self.invoke_webhook(
                    success=False, error=f"Server not ready after timeout ({timeout}s)")
                raise requests.RequestException(
                    f"Server not ready after timeout ({timeout}s)")

            print("Posting job to local server...")
            data = json.dumps(self.prompt).encode('utf-8')

            response = requests.post(self.ENDPOINT_PROMPT, data=data, timeout=10).json()

            if "prompt_id" in response:
                return response["prompt_id"]
            if "node_errors" in response:
                self.invoke_webhook(
                    success=False, error=response["node_errors"])
                raise requests.RequestException(response["node_errors"])
            if "error" in response:
                self.invoke_webhook(success=False, error=response["error"])
                raise requests.RequestException(response["error"])
        except requests.RequestException:
            self.invoke_webhook(success=False, error="Unknown error")
            raise
        except Exception as e:
            self.invoke_webhook(success=False, error="Unknown error")
            raise requests.RequestException("Failed to queue prompt") from e

    def get_job_status(self):
        try:
            history = requests.get(self.ENDPOINT_HISTORY, timeout=10).json()
            if self.comfyui_job_id in history:
                self.job_time_processed = datetime.datetime.now()
                return "complete"
            queue = requests.get(self.ENDPOINT_QUEUE, timeout=10).json()
            for job in queue["queue_running"]:
                if self.comfyui_job_id in job:
                    return "running"
            for job in queue["queue_pending"]:
                if self.comfyui_job_id in job:
                    return "pending"
        except requests.RequestException as e:
            self.invoke_webhook(success=False, error="Failed to queue job")
            raise requests.RequestException("Failed to queue job") from e

    def image_to_base64(self, path):
        with open(path, "rb") as f:
            b64 = (base64.b64encode(f.read()))
            b64_str = b64.decode('utf-8')
        return "data:image/png;charset=utf-8;base64, " + b64_str
    
    def remove_files(self, files_to_remove):
        for file_path in files_to_remove:
            os.remove(file_path)

    def get_result(self, job_id):
        result = requests.get(self.ENDPOINT_HISTORY, timeout=10).json()[
            job_id]

        # prompt = result["prompt"]
        outputs = result["outputs"]        

        custom_output_dir = f"{self.OUTPUT_DIR}{self.request_id}"
        os.makedirs(custom_output_dir, exist_ok=True)
        
        files_to_remove = []
        
        for item in outputs:
            for kind in ["images", "gifs"]:
                if kind in outputs[item]:
                    for image in outputs[item][kind]:
                        if image['type'] == "output":  
                            original_path = f"{self.OUTPUT_DIR}{image['subfolder']}/{image['filename']}"
                            new_path = f"{custom_output_dir}/{image['filename']}"
                            # Handle duplicated request where output file in not re-generated
                            if os.path.islink(original_path):
                                shutil.copyfile(os.path.realpath(original_path), new_path)
                            else:
                                os.rename(original_path, new_path)
                                os.symlink(new_path, original_path)
                            key = f"{self.request_id}/{image['filename']}"
                            self.result["images"].append({
                                # "local_path": new_path,
                                #"base64": self.image_to_base64(path),
                                # make this work first, then threads
                                "url": self.s3utils.file_upload(new_path, key)
                            })
                            
                            files_to_remove.append(original_path)
                            files_to_remove.append(new_path)
        
        self.job_time_completed = datetime.datetime.now()
        self.result["timings"] = {
            "job_time_received": self.job_time_received.ctime(),
            "job_time_queued": self.job_time_queued.ctime(),
            "job_time_processed": self.job_time_processed.ctime(),
            "job_time_completed": self.job_time_completed.ctime(),
            "job_time_total": (self.job_time_completed - self.job_time_received).seconds
        }
        
        threading.Thread(target=self.remove_files, args=(files_to_remove,)).start()

        return self.result
        

    def get_s3_settings(self):
        settings = {}
        settings["aws_access_key_id"] = self.get_value(
            "aws_access_key_id", os.environ.get("AWS_ACCESS_KEY_ID"))
        settings["aws_secret_access_key"] = self.get_value(
            "aws_secret_access_key", os.environ.get("AWS_SECRET_ACCESS_KEY"))
        settings["aws_endpoint_url"] = self.get_value(
            "aws_endpoint_url", os.environ.get("AWS_ENDPOINT_URL"))
        settings["aws_bucket_name"] = self.get_value(
            "aws_bucket_name", os.environ.get("AWS_BUCKET_NAME"))
        settings["connect_timeout"] = 5
        settings["connect_attempts"] = 1
        return settings

    # Webhook cannot be mandatory. Quick fix
    def invoke_webhook(self, success=False, result=None, error=""):
        if result is None:
            result = {}
        try:
            webhook_url = self.get_value(
                "webhook_url", os.environ.get("WEBHOOK_URL"))
        except ValueError as e:
            print(f"ValueError occurred: {e}")
            return None
        except KeyError as e:
            print(f"KeyError occurred: {e}")
            return None
        webhook_extra_params = self.get_value("webhook_extra_params", {})

        if Network.is_url(webhook_url):
            data = {}
            data["job_id"] = self.comfyui_job_id
            data["request_id"] = self.request_id
            data["success"] = success
            if result:
                data["result"] = result
            if error:
                data["error"] = error
            if webhook_extra_params:
                data["extra_params"] = webhook_extra_params
            Network.invoke_webhook(webhook_url, data)
        else:
            print("webhook_url is NOT valid!")

    def handle(self):
        self.comfyui_job_id = self.queue_job(30)

        status = None
        while status != "complete":
            status = self.get_job_status()
            if status != "complete":
                print(f"Waiting for {status} job to complete")
                time.sleep(0.5)

        result = self.get_result(self.comfyui_job_id)
        # temporary disable webhook
        # self.invoke_webhook(success=True, result=result)
        return result
