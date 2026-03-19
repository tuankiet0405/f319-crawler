"""Flask web application for F319 Crawler."""

import logging
import os

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


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/crawl", methods=["POST"])
def crawl():
    """Handle crawl request."""
    user_input = request.form.get("user_ids", "").strip()
    full_content_limit = int(request.form.get("full_content_limit", 10))
    max_posts = int(request.form.get("max_posts", 0))

    # Validate input
    try:
        users = validate_user_input(user_input)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    results = []
    all_posts = []
    files_created = []

    for i, (username, userid) in enumerate(users, 1):
        logger.info(f"Crawling user {i}/{len(users)}: {username}.{userid}")

        try:
            posts = crawl_user(
                username=username,
                userid=userid,
                full_content_limit=full_content_limit,
                max_posts=max_posts,
            )

            if posts:
                # Export individual CSV
                filename = generate_filename(username, userid)
                filepath = export_to_csv(posts, filename)
                files_created.append(filename)
                all_posts.extend(posts)

                results.append({
                    "username": username,
                    "userid": userid,
                    "post_count": len(posts),
                    "filename": filename,
                    "full_content_count": sum(1 for p in posts if p.get("content_type") == "full"),
                })
            else:
                results.append({
                    "username": username,
                    "userid": userid,
                    "post_count": 0,
                    "filename": None,
                    "full_content_count": 0,
                })
        except Exception as e:
            logger.error(f"Error crawling {username}: {e}")
            results.append({
                "username": username,
                "userid": userid,
                "post_count": 0,
                "filename": None,
                "error": str(e),
            })

    # Combined CSV for multi-user
    if len(users) > 1 and all_posts:
        combined_filename = generate_combined_filename()
        export_to_csv(all_posts, combined_filename)
        files_created.append(combined_filename)

    return jsonify({
        "success": True,
        "results": results,
        "total_posts": len(all_posts),
        "files": files_created,
    })


@app.route("/download/<filename>")
def download(filename):
    """Download a generated CSV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="text/csv",
    )


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host=HOST, port=PORT, debug=DEBUG)
