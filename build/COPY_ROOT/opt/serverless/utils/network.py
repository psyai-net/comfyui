import os
import hashlib
from urllib.parse import urlparse
import requests

from .filesystem import Filesystem

class Network:
    def __init__(self):
        pass

    @staticmethod
    def is_url(value):
        try:
            return bool(urlparse(value)[0])
        except(AttributeError, TypeError):        
            return False
    
    @staticmethod
    def get_url_hash(url):
        return hashlib.md5((f'{url}').encode()).hexdigest()
    
     
    @staticmethod
    def download_file(url, target_dir, request_id):
        try:
            print(f"download_file request id: {request_id}")
            file_name_hash = Network.get_url_hash(url)
            os.makedirs(target_dir, exist_ok=True)
            response = requests.get(url, timeout=5)
            if response.status_code > 399:
                raise requests.RequestException(f"Unable to download {url}")
          
            filepath_hash = f"{target_dir}/{file_name_hash}"
            # ignore above
            with open(filepath_hash, mode="wb") as file:
                file.write(response.content)
           
            file_extension = Filesystem.get_file_extension(filepath_hash)     
            filepath = f"{filepath_hash}{file_extension}"
            os.replace(filepath_hash, filepath)
            
        except requests.RequestException as req_err:
            print(f"Error downloading file: {req_err}")
            return None
        except IOError as io_err:
            print(f"Error writing file: {io_err}")
            return None
    
    @staticmethod
    def invoke_webhook(url, data):
        try:
            response = requests.post(url, json=data, timeout=30)
            print(f"Invoke webhook {url} with data {data} - status {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request: {e}")
            return None
