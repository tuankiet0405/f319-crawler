"""Flask web application for F319 Crawler — background job architecture."""

import logging
import os
import threading
import time
import uuid

from flask import Flask, render_template, request, jsonify, send_file

from config import HOST, PORT, DEBUG, OUTPUT_DIR, LOG_FILE
from crawler.scraper import validate_user_input, crawl_user
from crawler.exporter import export_to_csv, generate_filename, generate_combined_filename

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── In-memory job store ───
# {job_id: {"status": "running|done|error", "progress": [...], "results": None, "started": float}}
jobs = {}
JOBS_TTL = 600  # auto-cleanup jobs older than 10 minutes


def _cleanup_old_jobs():
    """Remove finished jobs older than JOBS_TTL."""
    now = time.time()
    expired = [jid for jid, j in jobs.items()
               if j["status"] != "running" and now - j.get("started", now) > JOBS_TTL]
    for jid in expired:
        del jobs[jid]


def _run_crawl(job_id, users, full_content_limit, max_posts):
    """Background worker: crawl users and update job state."""
    job = jobs[job_id]

    try:
        results = []
        all_posts = []
        files_created = []

        for i, (username, userid) in enumerate(users, 1):
            job["progress"].append(f"Crawling user {i}/{len(users)}: {username}.{userid}")
            logger.info(f"[Job {job_id[:8]}] Crawling user {i}/{len(users)}: {username}.{userid}")

            try:
                posts = crawl_user(
                    username=username,
                    userid=userid,
                    full_content_limit=full_content_limit,
                    max_posts=max_posts,
                    progress_callback=lambda msg: job["progress"].append(msg),
                )

                if posts:
                    filename = generate_filename(username, userid)
                    export_to_csv(posts, filename)
                    files_created.append(filename)
                    all_posts.extend(posts)

                    results.append({
                        "username": username,
                        "userid": userid,
                        "post_count": len(posts),
                        "filename": filename,
                        "full_content_count": sum(1 for p in posts if p.get("content_type") == "full"),
                        "posts": posts,  # Include for client-side CSV download
                    })
                else:
                    results.append({
                        "username": username,
                        "userid": userid,
                        "post_count": 0,
                        "filename": None,
                        "full_content_count": 0,
                        "posts": [],
                    })
            except Exception as e:
                logger.error(f"[Job {job_id[:8]}] Error crawling {username}: {e}")
                results.append({
                    "username": username,
                    "userid": userid,
                    "post_count": 0,
                    "filename": None,
                    "error": str(e),
                })

        # Combined CSV
        if len(users) > 1 and all_posts:
            combined_filename = generate_combined_filename()
            export_to_csv(all_posts, combined_filename)
            files_created.append(combined_filename)

        job["results"] = {
            "success": True,
            "results": results,
            "total_posts": len(all_posts),
            "files": files_created,
        }
        job["status"] = "done"
        job["progress"].append(f"✅ Hoàn tất — {len(all_posts)} bài viết")
        logger.info(f"[Job {job_id[:8]}] Done — {len(all_posts)} posts")

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["progress"].append(f"❌ Lỗi: {e}")
        logger.error(f"[Job {job_id[:8]}] Fatal error: {e}")


# ─── Routes ───

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/crawl", methods=["POST"])
def crawl():
    """Start a crawl job (returns immediately with job_id)."""
    user_input = request.form.get("user_ids", "").strip()
    full_content_limit = int(request.form.get("full_content_limit", 10))
    max_posts = int(request.form.get("max_posts", 0))

    # Validate input synchronously
    try:
        users = validate_user_input(user_input)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Cleanup old jobs
    _cleanup_old_jobs()

    # Create job
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {
        "status": "running",
        "progress": [f"Bắt đầu crawl {len(users)} user(s)..."],
        "results": None,
        "started": time.time(),
    }

    # Start background thread
    thread = threading.Thread(
        target=_run_crawl,
        args=(job_id, users, full_content_limit, max_posts),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def job_status(job_id):
    """Poll job status and progress."""
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    job = jobs[job_id]
    response = {
        "status": job["status"],
        "progress": job["progress"],
    }

    if job["status"] == "done":
        response["results"] = job["results"]
    elif job["status"] == "error":
        response["error"] = job.get("error", "Unknown error")

    return jsonify(response)


@app.route("/download/<filename>")
def download(filename):
    """Download a generated CSV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    response = send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="text/csv; charset=utf-8",
    )
    # Explicit header to ensure browser uses proper filename
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host=HOST, port=PORT, debug=DEBUG)
