import re

# ===== 1. تعديل main.py: إضافة دالة جلب الإذاعات ومسار API =====
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# إضافة دالة جلب الإذاعات السورية من radio-browser.info
if 'def get_syrian_radios' not in content:
    func = '''
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

'''
    content = content.replace('uvicorn.run(app', func + 'uvicorn.run(app', 1)
    print('✅ تم إضافة دالة get_syrian_radios ومسار /api/syrian_radios')

# تعديل مسار /radio لتمرير الإذاعات
old_radio = '''@app.get("/radio", response_class=HTMLResponse)
async def radio_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    return templates.TemplateResponse(request=request, name="radio.html", context={"user": user})'''

new_radio = '''@app.get("/radio", response_class=HTMLResponse)
async def radio_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    syrian_radios = get_syrian_radios()
    return templates.TemplateResponse(request=request, name="radio.html", context={"user": user, "syrian_radios": syrian_radios})'''

content = content.replace(old_radio, new_radio)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('✅ تم تحديث main.py بنجاح!')

# ===== 2. تعديل radio.html: عرض الإذاعات السورية ديناميكياً =====
with open('templates/radio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# استبدال قسم الإذاعات السورية الثابت بقسم ديناميكي
old_section = '''<h2 class="section-title">🇸🇾 الإذاعات السورية</h2>
        <div class="stations-grid">
            <div class="station-card" onclick="playStation('https://radiodamascus.ortas.live/RDimshq/RDimshqAudioLive/playlist.m3u8', 'إذاعة دمشق', this)">
                <div class="station-icon">📻</div>
                <div class="station-name">إذاعة دمشق</div>
                <div class="station-desc">95.0 FM</div>
            </div>
            <div class="station-card" onclick="playStation('http://radioshamfm.grtvstream.com:2199/tunein/shamfm.pls', 'شام FM', this)">
                <div class="station-icon">🎼</div>
                <div class="station-name">شام FM</div>
                <div class="station-desc">92.3 دمشق</div>
            </div>
            <div class="station-card" onclick="playStation('http://82.137.248.20:1935/RSyriana/RSyrianaLive/playlist.m3u8', 'راديو سوريا (سوريانا)', this)">
                <div class="station-icon">🇸🇾</div>
                <div class="station-name">راديو سوريا (سوريانا)</div>
                <div class="station-desc">بث مباشر</div>
            </div>
            <div class="station-card" onclick="playStation('http://82.137.248.20:1935/RShabab/RShababLive/playlist.m3u8', 'صوت الشباب', this)">
                <div class="station-icon">🎤</div>
                <div class="station-name">صوت الشباب</div>
                <div class="station-desc">RTV Syria</div>
            </div>
            <div class="station-card" onclick="playStation('http://82.137.248.20:1935/RKarma/RKarmaLive/playlist.m3u8', 'راديو الكرامة', this)">
                <div class="station-icon">🎵</div>
                <div class="station-name">راديو الكرامة</div>
                <div class="station-desc">بث مباشر</div>
            </div>
            <div class="station-card" onclick="playStation('http://82.137.248.20:1935/RZenobia/RZenobiaLive/playlist.m3u8', 'راديو زينوبيا', this)">
                <div class="station-icon">🏛️</div>
                <div class="station-name">راديو زينوبيا</div>
                <div class="station-desc">بث مباشر</div>
            </div>
        </div>'''

new_section = '''<h2 class="section-title">🇸🇾 الإذاعات السورية</h2>
        <div class="stations-grid" id="syrianRadiosGrid">
            <p style="text-align:center; color:#d4af37; grid-column: 1/-1;">⏳ جاري تحميل الإذاعات...</p>
        </div>'''

html = html.replace(old_section, new_section)

# إضافة JavaScript لجلب الإذاعات
old_script = '''function toggleMenu() {'''
new_script = '''async function loadSyrianRadios() {
            const grid = document.getElementById('syrianRadiosGrid');
            try {
                // محاولة جلب الإذاعات من API
                const response = await fetch('/api/syrian_radios');
                const radios = await response.json();
                
                if (!radios || radios.length === 0) {
                    grid.innerHTML = '<p style="text-align:center; color:#ff9800; grid-column: 1/-1;">⚠️ لا توجد إذاعات متاحة حالياً. حاول تحديث الصفحة.</p>';
                    return;
                }
                
                grid.innerHTML = '';
                radios.forEach(radio => {
                    const card = document.createElement('div');
                    card.className = 'station-card';
                    card.onclick = () => playStation(radio.url, radio.name, card);
                    const icon = radio.favicon ? '<img src="' + radio.favicon + '" style="width:40px;height:40px;border-radius:8px;" onerror="this.style.display=\\'none\\';this.parentNode.innerHTML=\\'📻\\'">' : '📻';
                    card.innerHTML = '<div class="station-icon">' + icon + '</div><div class="station-name">' + radio.name + '</div><div class="station-desc">' + (radio.tags ? radio.tags.substring(0, 30) : 'بث مباشر') + '</div>';
                    grid.appendChild(card);
                });
            } catch (e) {
                console.error('خطأ في تحميل الإذاعات:', e);
                grid.innerHTML = '<p style="text-align:center; color:#ff9800; grid-column: 1/-1;">⚠️ تعذر تحميل الإذاعات. تحقق من اتصالك بالإنترنت.</p>';
            }
        }
        
        window.addEventListener('load', loadSyrianRadios);

        function toggleMenu() {'''

html = html.replace(old_script, new_script)

with open('templates/radio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('✅ تم تحديث radio.html بنجاح!')
