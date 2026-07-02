import json
from typing import Generator, Optional
from pathlib import Path
import os
import nextcloud_client
import requests
from requests.auth import HTTPBasicAuth

def save_json_metadata(data: dict, path: Path) -> None:
    """
    Public function for saving metadata to json file

    Args:
        data: data for json
        path: directory for saving json file in local system
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def send_lrs(url: str, xAPI: dict)->None:
    """
    Public function for sending to lrs platform \"ralph\"
    
    Args:
        url: url for sending json 
        xAPI: it's json request 
    """
    auth = HTTPBasicAuth(os.environ.get('LOGIN_LRS'),os.environ.get('PASSWORD_LRS'))
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=xAPI, headers=headers, auth=auth)
    if response.status_code == 200:
        print("Data successufl sent to LRS server")
    else:
        print("Error:",response.status_code)
        print("Response server:", response.text)

def send_next_cloud(local_files: dict, remote_folder: str)->dict:
    """
    Public function for sending to next cloude

    Args:
        path_files: dict for storing paths for saving files to next cloud

    Return:
        uploaded_urls: urls to files for downloads
    """

    base_url = os.environ.get('API_NEXTCLOUD').rstrip('/')
    external_url = os.environ.get('NEXTCLOUD_EXTERNAL_URL', 'http://localhost:8080').rstrip('/')
    username = os.environ.get('LOGIN_NEXTCLOUD')
    password = os.environ.get('PASSWORD_NEXTCLOUD')
    auth = HTTPBasicAuth(username, password)
    
    webdav_base = f"{base_url}/remote.php/dav/files/{username}"
    external_webdav_base = f"{external_url}/remote.php/dav/files/{username}"
    remote_folder_clean = remote_folder.lstrip('/')
    
    def directory_exists(path):
        check_url = f"{webdav_base}/{path}"
        response = requests.request('PROPFIND', check_url, auth=auth, headers={'Depth': '1'})
        return response.status_code in [200, 207]
    
    if not directory_exists(remote_folder_clean):
        parts = remote_folder_clean.split('/')
        current_path = ""
        for part in parts:
            if not part:
                continue
            current_path += f"/{part}" if current_path else part
            if not directory_exists(current_path):
                mkdir_url = f"{webdav_base}/{current_path}"
                response = requests.request('MKCOL', mkdir_url, auth=auth)
                if response.status_code not in [200, 201, 204, 405]:
                    print(f"Could not create {current_path}: {response.status_code}")
    else:
        print(f"Directory {remote_folder_clean} already exists")
    
    uploaded_urls = {}
    for key, local_path in local_files.items():
        if local_path and Path(local_path).exists():
            remote_path = f"{remote_folder_clean}/{Path(local_path).name}"
            upload_url = f"{webdav_base}/{remote_path}"
            external_url_full = f"{external_webdav_base}/{remote_path}"
            
            with open(local_path, 'rb') as f:
                response = requests.put(upload_url, data=f, auth=auth)
                if response.status_code in [200, 201, 204]:
                    uploaded_urls[key] = external_url_full
                    print(f"Uploaded {key} -> {external_url_full}")
                else:
                    print(f"Failed to upload {key}: {response.status_code} - {response.text}")
                    uploaded_urls[key] = ""
        else:
            print(f"File {local_path} does not exist")
            uploaded_urls[key] = ""
    
    return uploaded_urls