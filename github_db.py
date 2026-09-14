import base64
import json
import os
import requests

# إعدادات GitHub (تُقرأ من متغيرات البيئة أو ملف .env)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "Eyadanoos11")
GITHUB_REPO = os.getenv("GITHUB_REPO", "sabahiya")
GITHUB_API = "https://api.github.com"

def get_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def read_json_from_github(filename):
    """قراءة ملف JSON من GitHub"""
    try:
        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content), data.get("sha")
        return None, None
    except Exception as e:
        print(f"خطأ في قراءة {filename}: {e}")
        return None, None

def write_json_to_github(filename, data, commit_message="update"):
    """كتابة ملف JSON إلى GitHub"""
    try:
        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"
        
        _, sha = read_json_from_github(filename)
        
        content_str = json.dumps(data, ensure_ascii=False, indent=2)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": commit_message,
            "content": content_b64
        }
        if sha:
            payload["sha"] = sha
        
        response = requests.put(url, headers=get_headers(), json=payload, timeout=15)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"فشل الكتابة في {filename}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"خطأ في الكتابة إلى {filename}: {e}")
        return False
