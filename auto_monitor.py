import os
import json
import requests
from datetime import datetime

# ==================== 🛠️ 1. 安全與路徑設定區 ====================
GITHUB_USER = "tuyunrou"  # 你的 GitHub 帳號
REPO_NAME = "EEWS_GAS_Dashboard_Data"  # 你實際的儲存庫名稱
BRANCH = "main"

# 💡 安全提示：實務上建議設定為環境變數（如 os.getenv("GH_TOKEN")）
GITHUB_TOKEN = os.environ.get("GH_TOKEN")

# ==================== 📥 2. 內部核心資料整合邏輯 ====================
def build_standard_json(raw_event_id, consensus_mag, depth, lat, lon, max_int):
    """
    將內部系統產出的地震參數，封裝成符合專題規格書第 5 頁的標準化 JSON 格式
    """
    current_time_iso = datetime.now().isoformat() + "+08:00"
    
    standard_data = {
        "event_id": raw_event_id,
        "origin_time": current_time_iso,
        "update_time": current_time_iso,
        "status": "active",
        "consensus": {
            "magnitude": float(consensus_mag),
            "lat": float(lat),
            "lon": float(lon),
            "depth_km": float(depth),
            "max_intensity": int(max_int)
        },
        "solutions": [
            {
                "algorithm": "eBEAR",
                "magnitude": round(float(consensus_mag) + 0.1, 1),
                "lat": float(lat) + 0.01,
                "lon": float(lon) + 0.01,
                "depth_km": float(depth) + 0.5,
                "max_intensity": int(max_int),
                "confidence": 0.88,
                "status": "ok"
            },
            {
                "algorithm": "FINDER",
                "magnitude": round(float(consensus_mag) - 0.1, 1),
                "lat": float(lat) - 0.02,
                "lon": float(lon) - 0.01,
                "depth_km": float(depth) - 0.8,
                "max_intensity": int(max_int),
                "confidence": 0.82,
                "status": "ok"
            }
        ],
        "public_note": f"🔴 預警推播測試成功！最新模擬震央位於花蓮近海（規模 {consensus_mag}）。"
    }
    return standard_data

# ==================== 🚀 3. GitHub API 單向發布核心 ====================
def push_to_github(file_path, json_data):
    """
    透過 GitHub REST API 自動取得舊檔案的 SHA 碼並安全更新，達到資料單向外推
    """
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Step A: 檢查檔案在 GitHub 是否已存在，若存在則取得 sha 碼
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
        
    # Step B: 轉換並進行 Base64 編碼
    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
    import base64
    content_b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": f"🤖 內網自動發布系統: 更新地震動態資料 {file_path}",
        "content": content_b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
        
    # Step C: 發送 PUT 請求更新 GitHub
    put_response = requests.put(url, headers=headers, json=payload)
    if put_response.status_code in [200, 201]:
        print(f"✅ [發布成功] 資料已單向推送至 GitHub: {file_path}")
    else:
        print(f"❌ [發布失敗] 狀態碼: {put_response.status_code}, 錯誤訊息: {put_response.text}")

# ==================== 🏁 4. 模擬執行 ====================
if __name__ == "__main__":
    print("🔄 啟動內網地震預警自動化整合發布模組...")
    
    # 模擬內網演算法拋出了最新一筆即時地震測報參數
    mock_event_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_TW"
    mock_mag = 5.8
    mock_depth = 12.5
    mock_lat = 24.15   # 花蓮近海緯度
    mock_lon = 121.65  # 花蓮近海經度
    mock_max_intensity = 5
    
    print(f"📦 偵測到內網新模擬事件: {mock_event_id} (規模: {mock_mag})")
    
    # 進行資料包裝
    final_json = build_standard_json(mock_event_id, mock_mag, mock_depth, mock_lat, mock_lon, mock_max_intensity)
    
    # 推送到 GitHub
    push_to_github("latest.json", final_json)
    print("🏁 內網排程作業結束。")
