import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import httpx
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Default TMDB API Key (can be overridden via environment variable TMDB_API_KEY)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "1cf50e6248dc270629e802686245c2c8")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# In-memory simple TTL cache
_cache = {}

def get_from_cache(key):
    if key in _cache:
        data, exp = _cache[key]
        if time.time() < exp:
            return data
        else:
            del _cache[key]
    return None

def set_in_cache(key, data, ttl=900): # 15 minutes default
    _cache[key] = (data, time.time() + ttl)

# HTTPX Client with proper headers & timeouts
client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    },
    timeout=12.0
)

import seed_data

def get_fallback_data(endpoint, params):
    if "trending" in endpoint:
        return {"results": seed_data.SEED_TRENDING, "page": 1, "total_pages": 1}
    elif "hi" in params.get("with_original_language", ""):
        return {"results": seed_data.SEED_BOLLYWOOD, "page": 1, "total_pages": 1}
    elif "16" in params.get("with_genres", "") or "ja" in params.get("with_original_language", ""):
        return {"results": seed_data.SEED_ANIME, "page": 1, "total_pages": 1}
    elif "season" in endpoint:
        # Fallback episodes for any season
        return {
            "season_number": 1,
            "episodes": [
                {
                    "episode_number": i,
                    "name": f"Episode {i}",
                    "overview": f"Episode {i} of this season. Stream directly on any available server.",
                    "runtime": 45,
                    "still_path": None
                } for i in range(1, 11)
            ]
        }
    elif endpoint.startswith("/tv/"):
        return {
            "id": 1399,
            "name": "Featured Series",
            "overview": "Popular television series streaming in high definition with multi-audio and subtitles.",
            "vote_average": 8.5,
            "genres": [{"id": 18, "name": "Drama"}, {"id": 10765, "name": "Sci-Fi & Fantasy"}],
            "seasons": [{"season_number": 1, "name": "Season 1", "episode_count": 10}],
            "credits": {"cast": []},
            "recommendations": {"results": seed_data.SEED_TRENDING}
        }
    elif endpoint.startswith("/movie/"):
        return {
            "id": 969681,
            "title": "Featured Movie",
            "overview": "Blockbuster movie streaming in 4K Ultra HD.",
            "vote_average": 8.2,
            "runtime": 124,
            "genres": [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}],
            "credits": {"cast": []},
            "recommendations": {"results": seed_data.SEED_TRENDING}
        }
    elif "genre" in endpoint:
        return {"genres": [
            {"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 16, "name": "Animation"},
            {"id": 35, "name": "Comedy"}, {"id": 80, "name": "Crime"}, {"id": 18, "name": "Drama"},
            {"id": 14, "name": "Fantasy"}, {"id": 27, "name": "Horror"}, {"id": 9648, "name": "Mystery"},
            {"id": 10749, "name": "Romance"}, {"id": 878, "name": "Sci-Fi"}, {"id": 53, "name": "Thriller"}
        ]}
    elif "movie" in endpoint:
        return {"results": [x for x in seed_data.SEED_TRENDING if x.get("media_type") == "movie"] + seed_data.SEED_BOLLYWOOD, "page": 1}
    elif "tv" in endpoint:
        return {"results": [x for x in seed_data.SEED_TRENDING if x.get("media_type") == "tv"] + seed_data.SEED_ANIME, "page": 1}
    return {"results": seed_data.SEED_TRENDING, "page": 1}

def tmdb_request(endpoint, params=None, ttl=900):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    
    # Generate cache key
    sorted_params = sorted(params.items())
    cache_key = f"{endpoint}?{sorted_params}"
    
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached

    url = f"{TMDB_BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            set_in_cache(cache_key, data, ttl=ttl)
            return data
        else:
            fallback = get_fallback_data(endpoint, params)
            set_in_cache(cache_key, fallback, ttl=300)
            return fallback
    except Exception as e:
        fallback = get_fallback_data(endpoint, params)
        set_in_cache(cache_key, fallback, ttl=300)
        return fallback

# Supported Embed Video Providers
EMBED_SERVERS = [
    {
        "id": "vidlink",
        "name": "VidLink HD (Fast, Multi-Audio & Subs)",
        "badge": "Recommended",
        "quality": "1080p / 4K",
        "features": ["Multi-Subtitles", "Multi-Audio", "Autoplay", "No Lag"],
        "movie_url": "https://vidlink.pro/movie/{id}?primaryColor=e50914&secondaryColor=1f1f23&iconColor=e50914&title=true&poster=true&autoplay=false",
        "tv_url": "https://vidlink.pro/tv/{id}/{season}/{episode}?primaryColor=e50914&secondaryColor=1f1f23&iconColor=e50914&title=true&poster=true&autoplay=false"
    },
    {
        "id": "vidsrc_cc",
        "name": "VidSrc Pro (Server 2)",
        "badge": "HD+",
        "quality": "1080p",
        "features": ["High Speed", "Multi-Subtitles"],
        "movie_url": "https://vidsrc.cc/v2/embed/movie/{id}?autoPlay=false",
        "tv_url": "https://vidsrc.cc/v2/embed/tv/{id}/{season}/{episode}?autoPlay=false"
    },
    {
        "id": "vidsrc_xyz",
        "name": "VidSrc XYZ (Server 3)",
        "badge": "Stable",
        "quality": "1080p",
        "features": ["Reliable", "Multi-Subtitles"],
        "movie_url": "https://vidsrc.xyz/embed/movie/{id}",
        "tv_url": "https://vidsrc.xyz/embed/tv/{id}/{season}/{episode}"
    },
    {
        "id": "embedsu",
        "name": "EmbedSU (Server 4)",
        "badge": "Fast",
        "quality": "1080p",
        "features": ["Fast CDN", "Multiple Qualities"],
        "movie_url": "https://embed.su/embed/movie/{id}",
        "tv_url": "https://embed.su/embed/tv/{id}/{season}/{episode}"
    },
    {
        "id": "autoembed",
        "name": "AutoEmbed (Server 5)",
        "badge": "VIP",
        "quality": "1080p",
        "features": ["Global CDN", "Subtitles"],
        "movie_url": "https://player.autoembed.cc/embed/movie/{id}",
        "tv_url": "https://player.autoembed.cc/embed/tv/{id}/{season}/{episode}"
    },
    {
        "id": "multiembed",
        "name": "MultiEmbed (Server 6 - Multi-Lang / Regional)",
        "badge": "Multi-Audio",
        "quality": "720p / 1080p",
        "features": ["Hindi/Regional Audio", "Spanish/French Tracks"],
        "movie_url": "https://multiembed.mov/?video_id={id}&tmdb=1",
        "tv_url": "https://multiembed.mov/?video_id={id}&tmdb=1&s={season}&e={episode}"
    },
    {
        "id": "smashystream",
        "name": "SmashyStream (Server 7)",
        "badge": "Backup",
        "quality": "1080p",
        "features": ["Alternate Sources"],
        "movie_url": "https://embed.smashystream.com/playere.php?tmdb={id}",
        "tv_url": "https://embed.smashystream.com/playere.php?tmdb={id}&season={season}&episode={episode}"
    },
    {
        "id": "twoembed",
        "name": "2Embed (Server 8)",
        "badge": "Backup",
        "quality": "HD",
        "features": ["Classic Mirror"],
        "movie_url": "https://www.2embed.cc/embed/{id}",
        "tv_url": "https://www.2embed.cc/embedtv/{id}&s={season}&e={episode}"
    },
    {
        "id": "nxsha",
        "name": "Nxsha Space (Server 9 - Fast HD)",
        "badge": "HD Space",
        "quality": "1080p",
        "features": ["Fast CDN", "No Lag", "Subtitles"],
        "movie_url": "https://nxsha.space/embed/movie/{id}",
        "tv_url": "https://nxsha.space/embed/tv/{id}/{season}/{episode}"
    },
    {
        "id": "ythd",
        "name": "YTHD Player (Server 10 - Cinema HD)",
        "badge": "Cinema",
        "quality": "1080p / 4K",
        "features": ["High Speed", "Multi-Audio", "Subtitles"],
        "movie_url": "https://ythd.org/embed/movie/{id}",
        "tv_url": "https://ythd.org/embed/tv/{id}/{season}/{episode}"
    }
]

# Supported Languages for Content Filtering
SUPPORTED_LANGUAGES = [
    {"code": "all", "name": "All Languages", "native": "Global", "flag": "🌐"},
    {"code": "en", "name": "English", "native": "English", "flag": "🇺🇸"},
    {"code": "hi", "name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    {"code": "es", "name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    {"code": "ko", "name": "Korean (K-Drama)", "native": "한국어", "flag": "🇰🇷"},
    {"code": "ja", "name": "Japanese (Anime)", "native": "日本語", "flag": "🇯🇵"},
    {"code": "fr", "name": "French", "native": "Français", "flag": "🇫🇷"},
    {"code": "de", "name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    {"code": "it", "name": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    {"code": "pt", "name": "Portuguese", "native": "Português", "flag": "🇧🇷"},
    {"code": "te", "name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    {"code": "ta", "name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    {"code": "ml", "name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳"},
    {"code": "zh", "name": "Chinese", "native": "中文", "flag": "🇨🇳"},
    {"code": "ru", "name": "Russian", "native": "Русский", "flag": "🇷🇺"},
    {"code": "tr", "name": "Turkish", "native": "Türkçe", "flag": "🇹🇷"},
    {"code": "ar", "name": "Arabic", "native": "العربية", "flag": "🇸🇦"}
]

# OTT Platform Hubs (like NetMirror / net77)
OTT_PLATFORMS = [
    {"id": "all", "name": "All Hubs", "icon": "fa-film", "color": "#E50914"},
    {"id": "netflix", "name": "Netflix", "network_id": "213", "icon": "fa-n", "color": "#E50914", "badge": "Originals"},
    {"id": "prime", "name": "Prime Video", "network_id": "1024", "icon": "fa-amazon", "color": "#00A8E1", "badge": "Prime"},
    {"id": "disney", "name": "Disney+", "network_id": "2739", "icon": "fa-wand-magic-sparkles", "color": "#113CCF", "badge": "Disney+"},
    {"id": "apple", "name": "Apple TV+", "network_id": "2552", "icon": "fa-apple", "color": "#A2AAAD", "badge": "Apple Original"},
    {"id": "hbo", "name": "HBO Max", "network_id": "3186", "icon": "fa-crown", "color": "#9900F0", "badge": "Max"},
    {"id": "crunchyroll", "name": "Crunchyroll / Anime", "network_id": "1112", "genre_id": "16", "icon": "fa-dragon", "color": "#F47521", "badge": "Anime"},
    {"id": "bollywood", "name": "Bollywood & South", "lang": "hi", "icon": "fa-clapperboard", "color": "#FF9933", "badge": "Desi Hits"}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config")
def get_config():
    return jsonify({
        "status": "success",
        "embed_servers": EMBED_SERVERS,
        "languages": SUPPORTED_LANGUAGES,
        "ott_platforms": OTT_PLATFORMS
    })

@app.route("/api/trending")
def get_trending():
    media_type = request.args.get("media_type", "all") # all, movie, tv
    time_window = request.args.get("time_window", "day") # day, week
    page = request.args.get("page", "1")
    language = request.args.get("language", "en-US")
    
    endpoint = f"/trending/{media_type}/{time_window}"
    data = tmdb_request(endpoint, {"page": page, "language": language}, ttl=600)
    return jsonify(data)

@app.route("/api/movies/popular")
def get_popular_movies():
    page = request.args.get("page", "1")
    language = request.args.get("language", "en-US")
    data = tmdb_request("/movie/popular", {"page": page, "language": language})
    return jsonify(data)

@app.route("/api/tv/popular")
def get_popular_tv():
    page = request.args.get("page", "1")
    language = request.args.get("language", "en-US")
    data = tmdb_request("/tv/popular", {"page": page, "language": language})
    return jsonify(data)

@app.route("/api/movies/top_rated")
def get_top_rated_movies():
    page = request.args.get("page", "1")
    language = request.args.get("language", "en-US")
    data = tmdb_request("/movie/top_rated", {"page": page, "language": language})
    return jsonify(data)

@app.route("/api/tv/top_rated")
def get_top_rated_tv():
    page = request.args.get("page", "1")
    language = request.args.get("language", "en-US")
    data = tmdb_request("/tv/top_rated", {"page": page, "language": language})
    return jsonify(data)

@app.route("/api/discover")
def discover():
    media_type = request.args.get("media_type", "movie") # movie, tv
    page = request.args.get("page", "1")
    sort_by = request.args.get("sort_by", "popularity.desc")
    with_genres = request.args.get("with_genres", "")
    with_language = request.args.get("with_original_language", "")
    with_networks = request.args.get("with_networks", "")
    year = request.args.get("year", "")
    ui_lang = request.args.get("language", "en-US")

    params = {
        "page": page,
        "sort_by": sort_by,
        "language": ui_lang,
        "include_adult": "false"
    }

    if with_genres:
        params["with_genres"] = with_genres
    if with_language and with_language != "all":
        params["with_original_language"] = with_language
    if with_networks and media_type == "tv":
        params["with_networks"] = with_networks
    elif with_networks and media_type == "movie":
        # For movies from specific production companies/networks
        params["with_companies"] = with_networks

    if year:
        if media_type == "movie":
            params["primary_release_year"] = year
        else:
            params["first_air_date_year"] = year

    endpoint = f"/discover/{media_type}"
    data = tmdb_request(endpoint, params)
    return jsonify(data)

@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", "1")
    media_type = request.args.get("type", "multi") # multi, movie, tv
    language = request.args.get("language", "en-US")

    if not query:
        return jsonify({"results": [], "total_pages": 0, "total_results": 0})

    if media_type == "movie":
        endpoint = "/search/movie"
    elif media_type == "tv":
        endpoint = "/search/tv"
    else:
        endpoint = "/search/multi"

    data = tmdb_request(endpoint, {
        "query": query,
        "page": page,
        "language": language,
        "include_adult": "false"
    })
    return jsonify(data)

@app.route("/api/movie/<int:movie_id>")
def get_movie_details(movie_id):
    ui_lang = request.args.get("language", "en-US")
    data = tmdb_request(f"/movie/{movie_id}", {
        "append_to_response": "videos,credits,recommendations,similar",
        "language": ui_lang
    }, ttl=86400)
    return jsonify(data)

@app.route("/api/tv/<int:tv_id>")
def get_tv_details(tv_id):
    ui_lang = request.args.get("language", "en-US")
    data = tmdb_request(f"/tv/{tv_id}", {
        "append_to_response": "videos,credits,recommendations,similar",
        "language": ui_lang
    }, ttl=86400)
    return jsonify(data)

@app.route("/api/tv/<int:tv_id>/season/<int:season_num>")
def get_season_details(tv_id, season_num):
    ui_lang = request.args.get("language", "en-US")
    data = tmdb_request(f"/tv/{tv_id}/season/{season_num}", {
        "language": ui_lang
    }, ttl=86400)
    return jsonify(data)

@app.route("/api/genres")
def get_genres():
    movie_genres = tmdb_request("/genre/movie/list", ttl=86400).get("genres", [])
    tv_genres = tmdb_request("/genre/tv/list", ttl=86400).get("genres", [])
    
    # Merge unique genres
    genres_dict = {g["id"]: g["name"] for g in movie_genres}
    for g in tv_genres:
        genres_dict[g["id"]] = g["name"]
    
    merged = [{"id": k, "name": v} for k, v in sorted(genres_dict.items(), key=lambda x: x[1])]
    return jsonify({
        "movie_genres": movie_genres,
        "tv_genres": tv_genres,
        "all_genres": merged
    })

@app.route("/api/embed-urls")
def get_embed_urls():
    media_type = request.args.get("type", "movie") # movie or tv
    item_id = request.args.get("id")
    season = request.args.get("season", "1")
    episode = request.args.get("episode", "1")

    if not item_id:
        return jsonify({"error": "Missing item id"}), 400

    results = []
    for srv in EMBED_SERVERS:
        if media_type == "movie":
            url = srv["movie_url"].format(id=item_id)
        else:
            url = srv["tv_url"].format(id=item_id, season=season, episode=episode)
        
        results.append({
            "id": srv["id"],
            "name": srv["name"],
            "badge": srv["badge"],
            "quality": srv["quality"],
            "features": srv["features"],
            "url": url
        })

    return jsonify({
        "media_type": media_type,
        "id": item_id,
        "season": season if media_type == "tv" else None,
        "episode": episode if media_type == "tv" else None,
        "servers": results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[NetMirror] Server running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
