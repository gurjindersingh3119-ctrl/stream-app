# 🎬 NetMirror (Net77.cc Clone)

A modern, full-featured streaming portal clone of [Net77.cc](https://net77.cc/home) / NetMirror built with **Python Flask**, responsive **modern dark-mode vanilla JS/CSS**, and multi-provider **free video embed APIs** for movies, web series, TV shows, and anime across all languages.

---

## ✨ Features

- **🍿 Aggregated OTT Hubs**:
  - Filter content by streaming network: **Netflix**, **Prime Video**, **Disney+**, **Apple TV+**, **HBO Max**, **Crunchyroll / Anime**, and **Bollywood & Regional**.
- **🌐 All-Language Support**:
  - Filter and stream movies and TV shows in **English**, **Hindi (हिन्दी)**, **Spanish (Español)**, **Korean (한국어)**, **Japanese (日本語)**, **French (Français)**, **German (Deutsch)**, **Telugu (తెలుగు)**, **Tamil (தமிழ்)**, and more.
- **⚡ 8 Free High-Speed Embed Video Servers**:
  - **Server 1: VidLink HD** *(Recommended - Multi-Subtitles, Multi-Audio, Autoplay)*
  - **Server 2: VidSrc Pro** *(1080p, High Speed)*
  - **Server 3: VidSrc XYZ** *(Reliable Global Mirror)*
  - **Server 4: EmbedSU** *(Fast CDN, Quality Selector)*
  - **Server 5: AutoEmbed** *(Fast Global Streaming)*
  - **Server 6: MultiEmbed** *(Multi-Language & Indian Regional Audio support)*
  - **Server 7: SmashyStream** *(Alternate HD Source)*
  - **Server 8: 2Embed** *(Classic Backup Server)*
  - **Server 9: Nxsha Space** *(Fast CDN, 1080p, Subtitles)*
  - **Server 10: YTHD Player** *(1080p / 4K, Multi-Audio & Subtitles)*
- **📺 TV Series Season & Episode Navigator**:
  - Full season tabs and episode grid with thumbnails, episode runtimes, plot overviews, and "Now Playing" highlight.
  - Previous / Next Episode one-click controls.
- **🔥 Interactive Hero Banner**:
  - Auto-sliding featured titles with live backdrop transitions, ratings, tags, and quick playback.
- **🔍 Instant Debounced Search**:
  - Search movies, TV shows, and anime with live thumbnail dropdown suggestions.
- **📑 Filter & Discover Modal**:
  - Filter by media type, genre, release year, language, and sorting.
- **💾 Watchlist & Continue Watching (Local Storage)**:
  - Add titles to "My List".
  - Automatically records watch history with resume badges and progress bars.
- **🎥 Cinema Mode & Fullscreen**:
  - Theater mode, fullscreen video player, and trailer previews via official YouTube integration.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Dependencies: `pip install -r requirements.txt` (Flask, flask-cors, httpx)

### 2. Run the Application
Double-click `run.bat` or run:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 Embed API Endpoints Used

| Server | Movie Format | TV Series Format |
|---|---|---|
| **VidLink** | `https://vidlink.pro/movie/{id}` | `https://vidlink.pro/tv/{id}/{season}/{episode}` |
| **VidSrc CC** | `https://vidsrc.cc/v2/embed/movie/{id}` | `https://vidsrc.cc/v2/embed/tv/{id}/{season}/{episode}` |
| **VidSrc XYZ** | `https://vidsrc.xyz/embed/movie/{id}` | `https://vidsrc.xyz/embed/tv/{id}/{season}/{episode}` |
| **EmbedSU** | `https://embed.su/embed/movie/{id}` | `https://embed.su/embed/tv/{id}/{season}/{episode}` |
| **AutoEmbed** | `https://player.autoembed.cc/embed/movie/{id}` | `https://player.autoembed.cc/embed/tv/{id}/{season}/{episode}` |
| **MultiEmbed** | `https://multiembed.mov/?video_id={id}&tmdb=1` | `https://multiembed.mov/?video_id={id}&tmdb=1&s={season}&e={episode}` |
| **SmashyStream** | `https://embed.smashystream.com/playere.php?tmdb={id}` | `https://embed.smashystream.com/playere.php?tmdb={id}&season={season}&episode={episode}` |
| **2Embed** | `https://www.2embed.cc/embed/{id}` | `https://www.2embed.cc/embedtv/{id}&s={season}&e={episode}` |
| **Nxsha Space** | `https://nxsha.space/embed/movie/{id}` | `https://nxsha.space/embed/tv/{id}/{season}/{episode}` |
| **YTHD Player** | `https://ythd.org/embed/movie/{id}` | `https://ythd.org/embed/tv/{id}/{season}/{episode}` |

---

## 🛠️ Project Structure

```
netmirror/
├── app.py                 # Flask server with TMDB caching and API proxies
├── seed_data.py           # High-availability seed fallback data
├── test_app.py            # Automated test suite
├── requirements.txt       # Python dependencies
├── run.bat                # Windows one-click start script
├── templates/
│   └── index.html         # Netflix/Net77 style SPA layout
└── static/
    ├── css/
    │   └── style.css      # Dark-mode glassmorphic streaming UI styles
    └── js/
        ├── app.js         # Core frontend app logic, sliders, search, routing
        ├── player.js      # Embed video player and season/episode switcher
        └── storage.js     # Watchlist & Continue Watching localStorage manager
```
