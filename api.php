<?php
/**
 * NetMirror API Backend for Hostinger Shared Hosting (PHP 7.4 - 8.3+)
 * Handles TMDB API requests with file-based TTL caching and embed server endpoints.
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

define('TMDB_API_KEY', '1cf50e6248dc270629e802686245c2c8');
define('TMDB_BASE_URL', 'https://api.themoviedb.org/3');
define('CACHE_DIR', __DIR__ . '/cache');

if (!is_dir(CACHE_DIR)) {
    @mkdir(CACHE_DIR, 0755, true);
}

// 10 Free Embed Video Providers
$EMBED_SERVERS = [
    [
        "id" => "vidlink",
        "name" => "VidLink HD (Fast, Multi-Audio & Subs)",
        "badge" => "Recommended",
        "quality" => "1080p / 4K",
        "features" => ["Multi-Subtitles", "Multi-Audio", "Autoplay", "No Lag"],
        "movie_url" => "https://vidlink.pro/movie/{id}?primaryColor=e50914&secondaryColor=1f1f23&iconColor=e50914&title=true&poster=true&autoplay=false",
        "tv_url" => "https://vidlink.pro/tv/{id}/{season}/{episode}?primaryColor=e50914&secondaryColor=1f1f23&iconColor=e50914&title=true&poster=true&autoplay=false"
    ],
    [
        "id" => "vidsrc_cc",
        "name" => "VidSrc Pro (Server 2)",
        "badge" => "HD+",
        "quality" => "1080p",
        "features" => ["High Speed", "Multi-Subtitles"],
        "movie_url" => "https://vidsrc.cc/v2/embed/movie/{id}?autoPlay=false",
        "tv_url" => "https://vidsrc.cc/v2/embed/tv/{id}/{season}/{episode}?autoPlay=false"
    ],
    [
        "id" => "vidsrc_xyz",
        "name" => "VidSrc XYZ (Server 3)",
        "badge" => "Stable",
        "quality" => "1080p",
        "features" => ["Reliable", "Multi-Subtitles"],
        "movie_url" => "https://vidsrc.xyz/embed/movie/{id}",
        "tv_url" => "https://vidsrc.xyz/embed/tv/{id}/{season}/{episode}"
    ],
    [
        "id" => "embedsu",
        "name" => "EmbedSU (Server 4)",
        "badge" => "Fast",
        "quality" => "1080p",
        "features" => ["Fast CDN", "Multiple Qualities"],
        "movie_url" => "https://embed.su/embed/movie/{id}",
        "tv_url" => "https://embed.su/embed/tv/{id}/{season}/{episode}"
    ],
    [
        "id" => "autoembed",
        "name" => "AutoEmbed (Server 5)",
        "badge" => "VIP",
        "quality" => "1080p",
        "features" => ["Global CDN", "Subtitles"],
        "movie_url" => "https://player.autoembed.cc/embed/movie/{id}",
        "tv_url" => "https://player.autoembed.cc/embed/tv/{id}/{season}/{episode}"
    ],
    [
        "id" => "multiembed",
        "name" => "MultiEmbed (Server 6 - Multi-Lang / Regional)",
        "badge" => "Multi-Audio",
        "quality" => "720p / 1080p",
        "features" => ["Hindi/Regional Audio", "Spanish/French Tracks"],
        "movie_url" => "https://multiembed.mov/?video_id={id}&tmdb=1",
        "tv_url" => "https://multiembed.mov/?video_id={id}&tmdb=1&s={season}&e={episode}"
    ],
    [
        "id" => "smashystream",
        "name" => "SmashyStream (Server 7)",
        "badge" => "Backup",
        "quality" => "1080p",
        "features" => ["Alternate Sources"],
        "movie_url" => "https://embed.smashystream.com/playere.php?tmdb={id}",
        "tv_url" => "https://embed.smashystream.com/playere.php?tmdb={id}&season={season}&episode={episode}"
    ],
    [
        "id" => "twoembed",
        "name" => "2Embed (Server 8)",
        "badge" => "Backup",
        "quality" => "HD",
        "features" => ["Classic Mirror"],
        "movie_url" => "https://www.2embed.cc/embed/{id}",
        "tv_url" => "https://www.2embed.cc/embedtv/{id}&s={season}&e={episode}"
    ],
    [
        "id" => "nxsha",
        "name" => "Nxsha Space (Server 9 - Fast HD)",
        "badge" => "HD Space",
        "quality" => "1080p",
        "features" => ["Fast CDN", "No Lag", "Subtitles"],
        "movie_url" => "https://nxsha.space/embed/movie/{id}",
        "tv_url" => "https://nxsha.space/embed/tv/{id}/{season}/{episode}"
    ],
    [
        "id" => "ythd",
        "name" => "YTHD Player (Server 10 - Cinema HD)",
        "badge" => "Cinema",
        "quality" => "1080p / 4K",
        "features" => ["High Speed", "Multi-Audio", "Subtitles"],
        "movie_url" => "https://ythd.org/embed/movie/{id}",
        "tv_url" => "https://ythd.org/embed/tv/{id}/{season}/{episode}"
    ]
];

$SUPPORTED_LANGUAGES = [
    ["code" => "all", "name" => "All Languages", "native" => "Global", "flag" => "🌐"],
    ["code" => "en", "name" => "English", "native" => "English", "flag" => "🇺🇸"],
    ["code" => "hi", "name" => "Hindi", "native" => "हिन्दी", "flag" => "🇮🇳"],
    ["code" => "es", "name" => "Spanish", "native" => "Español", "flag" => "🇪🇸"],
    ["code" => "ko", "name" => "Korean (K-Drama)", "native" => "한국어", "flag" => "🇰🇷"],
    ["code" => "ja", "name" => "Japanese (Anime)", "native" => "日本語", "flag" => "🇯🇵"],
    ["code" => "fr", "name" => "French", "native" => "Français", "flag" => "🇫🇷"],
    ["code" => "de", "name" => "German", "native" => "Deutsch", "flag" => "🇩🇪"],
    ["code" => "it", "name" => "Italian", "native" => "Italiano", "flag" => "🇮🇹"],
    ["code" => "pt", "name" => "Portuguese", "native" => "Português", "flag" => "🇧🇷"],
    ["code" => "te", "name" => "Telugu", "native" => "తెలుగు", "flag" => "🇮🇳"],
    ["code" => "ta", "name" => "Tamil", "native" => "தமிழ்", "flag" => "🇮🇳"],
    ["code" => "ml", "name" => "Malayalam", "native" => "മലയാളം", "flag" => "🇮🇳"],
    ["code" => "zh", "name" => "Chinese", "native" => "中文", "flag" => "🇨🇳"],
    ["code" => "ru", "name" => "Russian", "native" => "Русский", "flag" => "🇷🇺"],
    ["code" => "tr", "name" => "Turkish", "native" => "Türkçe", "flag" => "🇹🇷"],
    ["code" => "ar", "name" => "Arabic", "native" => "العربية", "flag" => "🇸🇦"]
];

$OTT_PLATFORMS = [
    ["id" => "all", "name" => "All Hubs", "icon" => "fa-film", "color" => "#E50914"],
    ["id" => "netflix", "name" => "Netflix", "network_id" => "213", "icon" => "fa-n", "color" => "#E50914", "badge" => "Originals"],
    ["id" => "prime", "name" => "Prime Video", "network_id" => "1024", "icon" => "fa-amazon", "color" => "#00A8E1", "badge" => "Prime"],
    ["id" => "disney", "name" => "Disney+", "network_id" => "2739", "icon" => "fa-wand-magic-sparkles", "color" => "#113CCF", "badge" => "Disney+"],
    ["id" => "apple", "name" => "Apple TV+", "network_id" => "2552", "icon" => "fa-apple", "color" => "#A2AAAD", "badge" => "Apple Original"],
    ["id" => "hbo", "name" => "HBO Max", "network_id" => "3186", "icon" => "fa-crown", "color" => "#9900F0", "badge" => "Max"],
    ["id" => "crunchyroll", "name" => "Crunchyroll / Anime", "network_id" => "1112", "genre_id" => "16", "icon" => "fa-dragon", "color" => "#F47521", "badge" => "Anime"],
    ["id" => "bollywood", "name" => "Bollywood & South", "lang" => "hi", "icon" => "fa-clapperboard", "color" => "#FF9933", "badge" => "Desi Hits"]
];

function fetch_tmdb($endpoint, $params = [], $ttl = 900) {
    $params['api_key'] = TMDB_API_KEY;
    ksort($params);
    $cache_key = md5($endpoint . '?' . http_build_query($params));
    $cache_file = CACHE_DIR . '/' . $cache_key . '.json';

    if (file_exists($cache_file) && (time() - filemtime($cache_file)) < $ttl) {
        return json_decode(file_get_contents($cache_file), true);
    }

    $url = TMDB_BASE_URL . '/' . ltrim($endpoint, '/') . '?' . http_build_query($params);
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept: application/json'
        ]
    ]);
    $response = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($status === 200 && $response) {
        @file_put_contents($cache_file, $response);
        return json_decode($response, true);
    }

    // Return cached if available even if expired, or return empty results
    if (file_exists($cache_file)) {
        return json_decode(file_get_contents($cache_file), true);
    }

    return ["results" => [], "page" => 1, "total_pages" => 1];
}

// Router
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$endpoint = preg_replace('#^/api/?#', '', $uri);

switch (true) {
    case ($endpoint === 'config'):
        echo json_encode([
            "status" => "success",
            "embed_servers" => $EMBED_SERVERS,
            "languages" => $SUPPORTED_LANGUAGES,
            "ott_platforms" => $OTT_PLATFORMS
        ]);
        break;

    case ($endpoint === 'trending'):
        $media_type = $_GET['media_type'] ?? 'all';
        $time_window = $_GET['time_window'] ?? 'day';
        $page = $_GET['page'] ?? '1';
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("trending/{$media_type}/{$time_window}", ['page' => $page, 'language' => $lang]));
        break;

    case ($endpoint === 'movies/popular'):
        $page = $_GET['page'] ?? '1';
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("movie/popular", ['page' => $page, 'language' => $lang]));
        break;

    case ($endpoint === 'tv/popular'):
        $page = $_GET['page'] ?? '1';
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("tv/popular", ['page' => $page, 'language' => $lang]));
        break;

    case ($endpoint === 'movies/top_rated'):
        $page = $_GET['page'] ?? '1';
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("movie/top_rated", ['page' => $page, 'language' => $lang]));
        break;

    case ($endpoint === 'tv/top_rated'):
        $page = $_GET['page'] ?? '1';
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("tv/top_rated", ['page' => $page, 'language' => $lang]));
        break;

    case ($endpoint === 'discover'):
        $type = $_GET['media_type'] ?? 'movie';
        $params = [
            'page' => $_GET['page'] ?? '1',
            'sort_by' => $_GET['sort_by'] ?? 'popularity.desc',
            'language' => $_GET['language'] ?? 'en-US',
            'include_adult' => 'false'
        ];
        if (!empty($_GET['with_genres'])) $params['with_genres'] = $_GET['with_genres'];
        if (!empty($_GET['with_original_language']) && $_GET['with_original_language'] !== 'all') {
            $params['with_original_language'] = $_GET['with_original_language'];
        }
        if (!empty($_GET['with_networks'])) {
            if ($type === 'tv') $params['with_networks'] = $_GET['with_networks'];
            else $params['with_companies'] = $_GET['with_networks'];
        }
        if (!empty($_GET['year'])) {
            if ($type === 'movie') $params['primary_release_year'] = $_GET['year'];
            else $params['first_air_date_year'] = $_GET['year'];
        }
        echo json_encode(fetch_tmdb("discover/{$type}", $params));
        break;

    case ($endpoint === 'search'):
        $q = trim($_GET['q'] ?? '');
        $page = $_GET['page'] ?? '1';
        $type = $_GET['type'] ?? 'multi';
        $lang = $_GET['language'] ?? 'en-US';
        if (empty($q)) {
            echo json_encode(["results" => [], "total_pages" => 0]);
            break;
        }
        $ep = ($type === 'movie') ? 'search/movie' : (($type === 'tv') ? 'search/tv' : 'search/multi');
        echo json_encode(fetch_tmdb($ep, ['query' => $q, 'page' => $page, 'language' => $lang]));
        break;

    case (preg_match('#^movie/(\d+)$#', $endpoint, $m)):
        $id = $m[1];
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("movie/{$id}", [
            'append_to_response' => 'videos,credits,recommendations,similar',
            'language' => $lang
        ], 86400));
        break;

    case (preg_match('#^tv/(\d+)$#', $endpoint, $m)):
        $id = $m[1];
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("tv/{$id}", [
            'append_to_response' => 'videos,credits,recommendations,similar',
            'language' => $lang
        ], 86400));
        break;

    case (preg_match('#^tv/(\d+)/season/(\d+)$#', $endpoint, $m)):
        $id = $m[1];
        $season = $m[2];
        $lang = $_GET['language'] ?? 'en-US';
        echo json_encode(fetch_tmdb("tv/{$id}/season/{$season}", ['language' => $lang], 86400));
        break;

    case ($endpoint === 'genres'):
        $movie = fetch_tmdb("genre/movie/list", [], 86400)['genres'] ?? [];
        $tv = fetch_tmdb("genre/tv/list", [], 86400)['genres'] ?? [];
        $merged = [];
        foreach (array_merge($movie, $tv) as $g) {
            $merged[$g['id']] = $g['name'];
        }
        $all = [];
        foreach ($merged as $k => $v) {
            $all[] = ["id" => $k, "name" => $v];
        }
        echo json_encode(["movie_genres" => $movie, "tv_genres" => $tv, "all_genres" => $all]);
        break;

    case ($endpoint === 'embed-urls'):
        $type = $_GET['type'] ?? 'movie';
        $id = $_GET['id'] ?? '';
        $season = $_GET['season'] ?? '1';
        $episode = $_GET['episode'] ?? '1';

        $res = [];
        foreach ($EMBED_SERVERS as $s) {
            if ($type === 'movie') {
                $url = str_replace('{id}', $id, $s['movie_url']);
            } else {
                $url = str_replace(['{id}', '{season}', '{episode}'], [$id, $season, $episode], $s['tv_url']);
            }
            $res[] = array_merge($s, ['url' => $url]);
        }
        echo json_encode([
            "media_type" => $type,
            "id" => $id,
            "season" => ($type === 'tv') ? $season : null,
            "episode" => ($type === 'tv') ? $episode : null,
            "servers" => $res
        ]);
        break;

    default:
        http_response_code(404);
        echo json_encode(["error" => "Endpoint not found: " . $endpoint]);
        break;
}
