import os
import time
import requests
from flask import Flask, jsonify, make_response

app = Flask(__name__)
TMDB = "27783cb7ebda05c652a7934334d3e002"
current = {}

def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def tmdb_lookup(imdb_id):
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/find/{imdb_id}",
            params={"api_key": TMDB, "external_source": "imdb_id"},
            timeout=5,
        )
        data = r.json()
        results = data.get("movie_results") or data.get("tv_results") or []
        if results:
            item = results[0]
            title = item.get("title") or item.get("name", imdb_id)
            poster = "https://image.tmdb.org/t/p/w500" + item["poster_path"] if item.get("poster_path") else None
            return title, poster
    except Exception:
        pass
    return imdb_id, None

@app.route("/")
def index():
    return add_cors(make_response("OK"))

@app.route("/manifest.json")
def manifest():
    return add_cors(make_response(jsonify({
        "id": "community.stremiodiscordrpc.railway",
        "version": "1.0.0",
        "name": "Discord RPC",
        "description": "Atualiza o Discord Rich Presence.",
        "resources": ["stream"],
        "types": ["movie", "series"],
        "catalogs": [],
        "idPrefixes": ["tt"],
    })))

@app.route("/stream/<type>/<id>.json")
def stream(type, id):
    parts = id.split(":")
    imdb_id = parts[0]
    season = int(parts[1]) if len(parts) > 1 else None
    episode = int(parts[2]) if len(parts) > 2 else None
    title, poster = tmdb_lookup(imdb_id)
    detail = f"S{season:02d}E{episode:02d}" if season and episode else "Assistindo"
    current.update({"title": title, "detail": detail, "poster": poster, "start": int(time.time())})
    print(f"▶  {title} — {detail}", flush=True)
    return add_cors(make_response(jsonify({"streams": []})))

@app.route("/now")
def now():
    return add_cors(make_response(jsonify(current)))

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
