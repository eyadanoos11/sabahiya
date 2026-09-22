import json
import urllib.request

TMDB_API_KEY = '151a3932cc4c9aefce50797a0ed698ad'
poster_url = "https://via.placeholder.com/500x750/1a3c34/d4af37?text=Hatchet"

try:
    url = "https://api.themoviedb.org/3/search/movie?api_key=" + TMDB_API_KEY + "&query=Hatchet&year=2006"
    with urllib.request.urlopen(url, timeout=15) as response:
        data = json.loads(response.read().decode())
        if data.get('results'):
            path = data['results'][0].get('poster_path')
            if path:
                poster_url = 'https://image.tmdb.org/t/p/w500' + path
                print('Poster: ' + poster_url)
except Exception as e:
    print('Error: ' + str(e))

with open('static/movies.json', 'r', encoding='utf-8') as f:
    movies = json.load(f)

movies = [m for m in movies if m['title'] != 'Hatchet']
movies.append({
    'title': 'Hatchet',
    'year': '2006',
    'poster': poster_url,
    'description': 'مجموعة من السياح يجدون أنفسهم محاصرين في مستنقعات نيو أورلينز، يطاردهم رجل مشوه خارق للطبيعة.',
    'category': 'رعب / كوميدي',
    'duration': '1 ساعة 23 دقيقة',
    'watch_url': 'https://odysee.com/Hatchet:9',
    'embed_url': 'https://odysee.com/$/embed/Hatchet:9'
})

with open('static/movies.json', 'w', encoding='utf-8') as f:
    json.dump(movies, f, ensure_ascii=False, indent=2)

print('')
print('Total movies: ' + str(len(movies)))
for m in movies:
    print('- ' + m['title'])
