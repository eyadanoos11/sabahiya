import json
import requests

TMDB_API_KEY = '151a3932cc4c9aefce50797a0ed698ad'
url = 'https://api.themoviedb.org/3/search/movie'
params = {'api_key': TMDB_API_KEY, 'query': 'Hatchet', 'year': '2006', 'language': 'ar'}

poster_url = ''
try:
    response = requests.get(url, params=params, timeout=15)
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            movie = data['results'][0]
            poster_path = movie.get('poster_path')
            if poster_path:
                poster_url = 'https://image.tmdb.org/t/p/w500' + poster_path
                print('✅ تم العثور على البوستر: ' + poster_url)
except Exception as e:
    print('خطأ في الاتصال: ' + str(e))

if not poster_url:
    poster_url = 'https://via.placeholder.com/500x750/1a3c34/d4af37?text=Hatchet'
    print('⚠️ استخدام صورة افتراضية')

with open('static/movies.json', 'r', encoding='utf-8') as f:
    movies = json.load(f)

if not any(m['title'] == 'Hatchet' for m in movies):
    new_movie = {
        'title': 'Hatchet',
        'year': '2006',
        'poster': poster_url,
        'description': 'مجموعة من السياح في رحلة سفاري في مستنقعات نيو أورلينز يجدون أنفسهم محاصرين في البرية، ليطاردهم رجل مشوه خارق للطبيعة.',
        'category': 'رعب / كوميدي',
        'duration': '1 ساعة 23 دقيقة',
        'watch_url': 'https://odysee.com/Hatchet:9',
        'embed_url': 'https://odysee.com/$/embed/Hatchet:9'
    }
    movies.append(new_movie)
    with open('static/movies.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    print('✅ تم إضافة فيلم Hatchet بنجاح!')
else:
    print('⚠️ الفيلم موجود بالفعل')
