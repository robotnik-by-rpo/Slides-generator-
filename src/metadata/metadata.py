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
        print("Данные успешно отправлены на LRS сервер")
    else:
        print("Ошибка:",response.status_code)
        print("Ответ сервера:", response.text)

def send_next_cloud(path_files: dict)->None:
    """
    Public function for sending to next cloude

    Args:
        path_files: dict for storing paths for saving files to next cloud
    """
    nc = nextcloud_client.Client('https://your-nextcloud.com')
    nc.login(os.environ.get('LOGIN_NEXTCLOUD'),os.environ.get('PASSWORD_NEXTCLOUD'))
    
    path_next_cloud = os.environ.get('FOLDER_NEXTCLOUD')
    nc.put_file(path_next_cloud,path_files["plan"])
    if path_files.get("pdf", False): 
        nc.put_file(path_next_cloud, path_files["pdf"])
    if path_files.get("pptx", False):
        nc.put_file(path_next_cloud, path_files["pptx"])
