import uvicorn
import json
import os
import time
import hashlib
from datetime import datetime, timezone, timedelta
import random
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# توقيت سوريا (UTC+3)
SYRIA_TZ = timezone(timedelta(hours=3))

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="mysecretkey123")

os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

USERS_FILE = "users.json"

from dotenv import load_dotenv
load_dotenv()
from github_db import read_json_from_github, write_json_to_github

def load_users():
    data, _ = read_json_from_github("users.json")
    if data is None:
        # إذا كان الملف غير موجود، أنشئ حساب الأدمن الافتراضي
        default = {
            "00963995600240": {
                "name": "eyad",
                "country": "سوريا",
                "password": hashlib.sha256("eyadnasem".encode()).hexdigest(),
                "is_admin": True,
                "is_banned": False,
                "forum_banned": False
            }
        }
        write_json_to_github("users.json", default, "إنشاء ملف المستخدمين الأولي")
        return default
    return data

def save_users(data):
    write_json_to_github("users.json", data, "تحديث المستخدمين")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_marble_types():
    types = []
    base_dir = "static/final_results"
    if os.path.exists(base_dir):
        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            if os.path.isdir(folder_path):
                files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if files:
                    name = folder.replace("_", " ")
                    types.append({
                        "name": name,
                        "img": f"/static/final_results/{folder}/{files[0]}",
                        "images": [f"/static/final_results/{folder}/{f}" for f in files[:2]]
                    })
    return types[:5]

def get_two_random_results(marble_type):
    folder = marble_type.replace(" ", "_")
    folder_path = f"static/final_results/{folder}"
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if len(files) >= 2:
            selected = random.sample(files, 2)
        elif len(files) == 1:
            selected = [files[0], files[0]]
        else:
            return []
        return [f"/static/final_results/{folder}/{f}" for f in selected]
    return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    marble_list = get_marble_types()
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user, "marble_list": marble_list, "final_results": marble_list})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={})

@app.post("/register")
async def register_post(request: Request, name: str = Form(...), phone: str = Form(...), country: str = Form(...), password: str = Form(...)):
    users = load_users()
    if phone in users:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "هذا الرقم مسجل بالفعل"})
    users[phone] = {"name": name, "country": country, "password": hash_password(password)}
    save_users(users)
    request.session["user"] = phone
    return RedirectResponse("/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})

@app.post("/login")
async def login_post(request: Request, phone: str = Form(...), password: str = Form(...)):
    users = load_users()
    if phone not in users:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "الرقم غير مسجل"})
    if users[phone]["password"] != hash_password(password):
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "كلمة المرور غير صحيحة"})
    request.session["user"] = phone
    return RedirectResponse("/", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.post("/generate_ai")
async def generate_ai(request: Request, marble_type: str = Form(...), file: UploadFile = File(None)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    try:
        users = load_users()
        user = users.get(request.session["user"], {})
        marble_list = get_marble_types()
        
        # حفظ الصورة المرفوعة
        if file is not None:
            filepath = f"static/uploads/{request.session['user'].replace('@','_').replace('.','_')}_custom.jpg"
            with open(filepath, "wb") as f:
                f.write(await file.read())

        # الانتظار 5 ثوانٍ (محاكاة المعالجة)
        time.sleep(5)

        # اختيار صورتين عشوائيتين
        selected_images = get_two_random_results(marble_type)
        if not selected_images:
            selected_images = ["https://via.placeholder.com/800x400?text=لا+توجد+صور", "https://via.placeholder.com/800x400?text=لا+توجد+صور"]

        return templates.TemplateResponse(request=request, name="index.html", context={
            "user": user,
            "marble_list": marble_list,
            "final_results": marble_list,
            "result_images": selected_images,
            "result_type": marble_type
        })
    except Exception as e:
        users = load_users()
        user = users.get(request.session["user"], {})
        marble_list = get_marble_types()
        return templates.TemplateResponse(request=request, name="index.html", context={"user": user, "marble_list": marble_list, "final_results": marble_list, "error": f"حدث خطأ: {str(e)}"})

def load_posts():
    data, _ = read_json_from_github("posts.json")
    if data is None:
        return []
    # ضمان وجود الحقول الجديدة
    for post in data:
        if "likes" not in post:
            post["likes"] = []
        if "comments" not in post:
            post["comments"] = []
        if "time" not in post:
            post["time"] = ""
    return data

def save_posts(posts):
    if len(posts) > 1000:
        posts = posts[-1000:]
    write_json_to_github("posts.json", posts, "تحديث المنشورات")

@app.get("/forum", response_class=HTMLResponse)
async def forum(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    posts = load_posts()
    users = load_users()
    user = users.get(request.session["user"], {})
    user_phone = request.session["user"]
    # تجهيز كل منشور مع معلومات إضافية للعرض
    posts_with_data = []
    for i, post in enumerate(posts[::-1]):
        original_index = len(posts) - 1 - i
        post_data = dict(post)
        post_data["original_index"] = original_index
        post_data["liked_by_user"] = user_phone in post.get("likes", [])
        post_data["likes_count"] = len(post.get("likes", []))
        post_data["comments_count"] = len(post.get("comments", []))
        posts_with_data.append(post_data)
    return templates.TemplateResponse(request=request, name="forum.html", context={"posts": posts_with_data, "user": user, "user_phone": user_phone})

@app.post("/forum")
async def post_message(request: Request, content: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    username = user.get("name", "مستخدم")
    posts = load_posts()
    posts.append({"username": username, "content": content})
    if len(posts) > 1000:
        posts = posts[-1000:]
    save_posts(posts)
    return RedirectResponse("/forum", status_code=303)


@app.get("/exchange_rate", response_class=HTMLResponse)
async def exchange_rate(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="exchange_rate.html", context={})

@app.get("/api/usd_rate")
async def get_usd_rate():
    try:
        import urllib.request
        import re
        import time
        url = "https://sp-today.com/en/currency/us-dollar"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        # البحث عن جميع الأرقام بالصيغة 3 أرقام + فاصلة عشرية + رقمين (مثال: 131.20)
        prices = re.findall(r'\b([1-9][0-9]{2}[.,][0-9]{2})\b', html)
        
        # تحويل النصوص إلى أرقام وتصفيتها في نطاق معقول للدولار في سوريا
        valid_prices = []
        for p in prices:
            try:
                val = float(p.replace(',', '.'))
                if 100 <= val <= 200:
                    valid_prices.append(val)
            except:
                pass
        
        if len(valid_prices) >= 2:
            buy_price = f"{valid_prices[0]:.2f}"
            sell_price = f"{valid_prices[1]:.2f}"
        else:
            # قيم احتياطية محدثة
            buy_price = "131.20"
            sell_price = "131.70"
        
        return {
            "buy": buy_price,
            "sell": sell_price,
            "last_updated": datetime.now(SYRIA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"buy": "131.20", "sell": "131.70", "last_updated": "قيمة افتراضية"}


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    current_user = users.get(request.session["user"], {})
    if not current_user.get("is_admin"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request=request, name="admin.html", context={"users": users, "current_user": current_user})

@app.post("/admin/ban_forum/{phone}")
async def ban_forum(request: Request, phone: str):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    current_user = users.get(request.session["user"], {})
    if not current_user.get("is_admin"):
        return RedirectResponse("/", status_code=303)
    if phone in users and not users[phone].get("is_admin"):
        users[phone]["forum_banned"] = True
        save_users(users)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/unban_forum/{phone}")
async def unban_forum(request: Request, phone: str):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    current_user = users.get(request.session["user"], {})
    if not current_user.get("is_admin"):
        return RedirectResponse("/", status_code=303)
    if phone in users:
        users[phone]["forum_banned"] = False
        save_users(users)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/ban_user/{phone}")
async def ban_user(request: Request, phone: str):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    current_user = users.get(request.session["user"], {})
    if not current_user.get("is_admin"):
        return RedirectResponse("/", status_code=303)
    if phone in users and not users[phone].get("is_admin"):
        users[phone]["is_banned"] = True
        save_users(users)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/unban_user/{phone}")
async def unban_user(request: Request, phone: str):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    current_user = users.get(request.session["user"], {})
    if not current_user.get("is_admin"):
        return RedirectResponse("/", status_code=303)
    if phone in users:
        users[phone]["is_banned"] = False
        save_users(users)
    return RedirectResponse("/admin", status_code=303)

import os
port = int(os.environ.get("PORT", 8000))

@app.get("/radio", response_class=HTMLResponse)
async def radio_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    syrian_radios = get_syrian_radios()
    return templates.TemplateResponse(request=request, name="radio.html", context={"user": user, "syrian_radios": syrian_radios})


import requests as req_lib

SYRIAN_RADIOS_CACHE = "syrian_radios.json"

def get_syrian_radios():
    """جلب الإذاعات السورية من radio-browser.info API مع تخزين مؤقت"""
    servers = [
        "https://de1.api.radio-browser.info",
        "https://nl1.api.radio-browser.info",
        "https://at1.api.radio-browser.info",
        "https://api.radio-browser.info"
    ]
    for server in servers:
        try:
            url = f"{server}/json/stations/bycountrycodeexact/SY"
            response = req_lib.get(url, timeout=15, headers={"User-Agent": "SabahiyaRadio/1.0"})
            if response.status_code == 200:
                stations = response.json()
                valid = []
                for s in stations:
                    if s.get("url_resolved") and s.get("name"):
                        valid.append({
                            "name": s["name"],
                            "url": s["url_resolved"],
                            "favicon": s.get("favicon", ""),
                            "tags": s.get("tags", "")
                        })
                # حفظ نسخة مؤقتة
                with open(SYRIAN_RADIOS_CACHE, "w", encoding="utf-8") as f:
                    import json as json_mod
                    json_mod.dump(valid, f, ensure_ascii=False, indent=2)
                return valid
        except Exception as e:
            print(f"فشل الاتصال بـ {server}: {e}")
            continue
    
    # إذا فشل كل شيء، قراءة من النسخة المخزنة
    import os as os_mod
    if os_mod.path.exists(SYRIAN_RADIOS_CACHE):
        with open(SYRIAN_RADIOS_CACHE, "r", encoding="utf-8") as f:
            import json as json_mod
            return json_mod.load(f)
    return []

@app.get("/api/syrian_radios")
async def api_syrian_radios():
    """API لجلب الإذاعات السورية"""
    return get_syrian_radios()



import requests as req_lib

TMDB_API_KEY = "151a3932cc4c9aefce50797a0ed698ad"  # <-- ضع مفتاحك هنا
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
POSTER_CACHE = {}

def get_movie_poster(title, year=None):
    """جلب رابط البوستر الرسمي للفيلم من TMDb API"""
    cache_key = f"{title}_{year}"
    if cache_key in POSTER_CACHE:
        return POSTER_CACHE[cache_key]
    
    try:
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": title, "language": "ar"}
        if year:
            params["year"] = year
        
        response = req_lib.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                movie = data["results"][0]
                poster_path = movie.get("poster_path")
                if poster_path:
                    poster_url = TMDB_IMAGE_BASE + poster_path
                    POSTER_CACHE[cache_key] = poster_url
                    return poster_url
    except Exception as e:
        print(f"خطأ في جلب البوستر: {e}")
    
    POSTER_CACHE[cache_key] = None
    return None


@app.get("/api/movie_poster")
async def api_movie_poster(title: str, year: str = ""):
    poster = get_movie_poster(title, year)
    return {"poster": poster}



uvicorn.run(app, host="0.0.0.0", port=port)
