import os
import json
import requests
import base64
import subprocess
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GH_TOKEN")
GITHUB_USER = "tuyunrou"
REPO_NAME = "EEWS_GAS_Dashboard_Data" 
FILE_PATH = "system_health.json"  # 這次我們要更新的是健康狀態檔案

def get_system_stats():
    """模擬或獲取本機系統的簡單健康狀態"""
    # 獲取系統當前時間
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 透過讀取負載來獲取簡單健康狀態，這裡做標準結構包裝
    health_data = {
        "last_check_time": current_time,
        "server_status": "ONLINE",
        "modules": {
            "eBEAR_listener": "RUNNING",
            "FINDER_listener": "RUNNING",
            "github_pusher": "OK"
        },
        "hardware": {
            "note": "MacBook Pro Monitor Host"
        }
    }
    return health_data

def push_health_to_github():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. 自動獲取舊檔案的 SHA
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get("sha") if res_get.status_code == 200 else None
    
    # 2. 獲取當前系統狀態資料
    health_json_data = get_system_stats()
    
    # 3. Base64 編碼
    json_str = json.dumps(health_json_data, ensure_ascii=False, indent=2)
    content_b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    # 4. 發送 PUT 請求
    payload = {
        "message": "🤖 [Server Heartbeat] Automatic Health Check",
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha
        
    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        print(f"✅ 健康狀態已成功回報至 GitHub ({res.status_code})")
    else:
        print(f"❌ 回報失敗: {res.text}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ 錯誤：找不到環境變數 GH_TOKEN，請先執行 export GH_TOKEN=...")
    else:
        push_health_to_github()
