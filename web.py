from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os, re
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "videos.json"

def load_videos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_videos(videos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

def get_embed_url(url):
    """Konvertiert YouTube/Vimeo URLs in Embed-Links."""
    # YouTube
    yt = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if yt:
        return f"https://www.youtube.com/embed/{yt.group(1)}"
    # Vimeo
    vm = re.search(r"vimeo\.com/(\d+)", url)
    if vm:
        return f"https://player.vimeo.com/video/{vm.group(1)}"
    return None

@app.route("/")
def index():
    videos = load_videos()
    videos = sorted(videos, key=lambda v: v["date"], reverse=True)
    return render_template("index.html", videos=videos)

@app.route("/add", methods=["POST"])
def add_video():
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    comment = request.form.get("comment", "").strip()

    if not name or not url:
        return redirect(url_for("index"))

    embed = get_embed_url(url)
    videos = load_videos()
    videos.append({
        "id": int(datetime.now().timestamp() * 1000),
        "name": name,
        "url": url,
        "embed": embed,
        "comment": comment,
        "date": datetime.now().isoformat(),
        "likes": 0
    })
    save_videos(videos)
    return redirect(url_for("index"))

@app.route("/like/<int:video_id>", methods=["POST"])
def like(video_id):
    videos = load_videos()
    for v in videos:
        if v["id"] == video_id:
            v["likes"] = v.get("likes", 0) + 1
            break
    save_videos(videos)
    return jsonify({"ok": True})

@app.route("/delete/<int:video_id>", methods=["POST"])
def delete(video_id):
    videos = load_videos()
    videos = [v for v in videos if v["id"] != video_id]
    save_videos(videos)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
