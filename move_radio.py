import re

# ===== 1. إزالة الراديو العائم من index.html و forum.html =====
for filename in ['templates/index.html', 'templates/forum.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة كتلة الراديو العائم بالكامل
    content = re.sub(r'<!-- ===== الراديو العربي ===== -->.*?<!-- ===== نهاية الراديو ===== -->\n?', '', content, flags=re.DOTALL)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ تم إزالة الراديو العائم من {filename}')

# ===== 2. إضافة زر الراديو في القائمة الجانبية + لوحة الراديو =====
radio_sidebar_item = '''<li style="margin-bottom:15px;">
                <a href="#" onclick="toggleRadioPanel(event)" style="color:white; text-decoration:none; font-size:18px; font-weight:bold; display:block; padding:10px;">📻 الراديو</a>
                <div id="radioPanel" style="display:none; background:#111; border-radius:8px; padding:10px; margin-top:8px;">
                    <button class="radio-station-btn" onclick="playRadio('https://backup.qurango.net/radio/tarateel', this)">📖 إذاعة القرآن الكريم</button>
                    <button class="radio-station-btn" onclick="playRadio('https://stream.zeno.fm/0r0xa792kwzuv', this)">🎶 راديو طرب عربي</button>
                    <button class="radio-station-btn" onclick="playRadio('https://stream.zeno.fm/8wv4d0a3kwzuv', this)">🎵 ميكس عربي</button>
                    <button class="radio-station-btn" onclick="playRadio('https://n0d.radiojar.com/8s5u5tpdtwzuv', this)">🎼 راديو الشام</button>
                    <audio id="radioAudio" controls style="width:100%; margin-top:8px; height:35px;"></audio>
                </div>
            </li>'''

for filename in ['templates/index.html', 'templates/forum.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'toggleRadioPanel' not in content:
        # إضافة زر الراديو قبل "الصفحة الرئيسية"
        content = content.replace(
            '<li style="margin-bottom:15px;"><a href="/"',
            radio_sidebar_item + '\n            <li style="margin-bottom:15px;"><a href="/"'
        )
        # في حال كان النمط مختلف
        content = content.replace(
            '<li><a href="/"',
            radio_sidebar_item + '\n            <li><a href="/"'
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ تم إضافة زر الراديو إلى {filename}')

# ===== 3. إضافة CSS + JavaScript للراديو =====
radio_css = '''
/* ===== تنسيقات الراديو في القائمة الجانبية ===== */
.radio-station-btn {
    width: 100%;
    padding: 8px;
    margin-bottom: 5px;
    background: #2e5d4a;
    color: white;
    border: 1px solid #d4af37;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'Tajawal', sans-serif;
    font-size: 12px;
    text-align: right;
    transition: all 0.2s;
}
.radio-station-btn:hover { background: #3d7d64; }
.radio-station-btn.active { background: #d4af37; color: #1a3c34; font-weight: bold; }
'''

radio_js = '''
        function toggleRadioPanel(event) {
            event.preventDefault();
            const panel = document.getElementById('radioPanel');
            panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
        }
        function playRadio(url, btn) {
            const audio = document.getElementById('radioAudio');
            document.querySelectorAll('.radio-station-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            audio.src = url;
            audio.play().catch(e => console.log('خطأ في التشغيل:', e));
        }
'''

for filename in ['templates/index.html', 'templates/forum.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة CSS قبل </style>
    if '.radio-station-btn {' not in content:
        content = content.replace('</style>', radio_css + '\n</style>')
    
    # إضافة JavaScript قبل </script> الأخير
    if 'function toggleRadioPanel' not in content:
        content = content.replace('</script>', radio_js + '</script>')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ تم إضافة CSS/JS الراديو إلى {filename}')
