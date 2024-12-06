import os
import re
import yaml
import markdown
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, jsonify, abort
import sqlite3

from post.topic_post import TopicPost
from post.arxiv_post import ArxivPost

app = Flask(__name__)

# Constants
POSTS_FOLDER = "post/posts/"
CACHE_DURATION = 40

# Cache and Index
posts_cache = []
posts_index = {}
last_loaded = 0

# Anthropic API Key
API_KEY = "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"

def run_arxiv_post():
    # Execute the ArxivPost task.
    generator = ArxivPost(api_key=API_KEY)
    generator.run()

def run_topic_post():
    # Execute the TopicPost task.
    generator = TopicPost(api_key=API_KEY)
    generator.run()

# Schedule ArxivPost every 24 hours and TopicPost every 12 hours.
scheduler = BackgroundScheduler()
scheduler.add_job(run_arxiv_post, 'interval', hours=24)
scheduler.add_job(run_topic_post, 'interval', hours=12)
scheduler.start()

def slugify(title):
    # Convert a title to a URL-friendly slug.
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s-]', '', title)
    return re.sub(r'\s+', '-', title).strip('-')

def extract_front_matter(content):
    # Extract YAML front matter and markdown content from a post.
    front_matter_pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    if match:
        front_matter = yaml.safe_load(match.group(1))
        markdown_content = match.group(2)
        return front_matter, markdown_content
    return {}, content

def load_posts():
    # Load posts from the POSTS_FOLDER, updating the cache if necessary.
    global posts_cache, posts_index, last_loaded
    if time.time() - last_loaded > CACHE_DURATION:
        posts = []
        index = {}
        for filename in os.listdir(POSTS_FOLDER):
            if filename.endswith(".md"):
                filepath = os.path.join(POSTS_FOLDER, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    front_matter, _ = extract_front_matter(content)
                    if "title" in front_matter and "description" in front_matter:
                        slug = slugify(front_matter["title"])
                        post = {
                            "title": front_matter["title"],
                            "content": front_matter["description"],
                            "slug": slug,
                            "filename": filename
                        }
                        posts.append(post)
                        index[slug] = post
                except Exception:
                    continue
        posts_cache = posts
        posts_index = index
        last_loaded = time.time()
    return posts_cache

@app.route("/api/posts")
def get_posts():
    # API endpoint to get a paginated list of posts.
    page = int(request.args.get("page", 1))
    posts_per_page = 10
    start = (page - 1) * posts_per_page
    end = start + posts_per_page
    paginated_posts = load_posts()[start:end]
    return jsonify(paginated_posts)

@app.route("/")
def home():
    # Render the home page.
    return render_template("modals/home.html")

@app.route("/archive")
def archive():
    # Render the archive page.
    return render_template("modals/archive.html")

@app.route("/archive/<slug>")
def show_post(slug):
    # Render a specific post by its slug.
    load_posts()
    post = posts_index.get(slug)
    if not post:
        abort(404)
    filepath = os.path.join(POSTS_FOLDER, post["filename"])
    with open(filepath, encoding="utf-8") as file:
        md_content = file.read()
    meta_tags, markdown_content = extract_front_matter(md_content)
    html_content = markdown.markdown(
        markdown_content, extensions=["fenced_code", "codehilite", "attr_list"]
    )
    return render_template("modals/post.html", markdown_content=html_content, meta_tags=meta_tags)

@app.route("/search-post")
def search_post():
    # Render the search post page.
    return render_template("/modals/search-post.html")

@app.route("/search_ajax")
def search_ajax():
    # API endpoint to search posts by title or content.
    query = request.args.get('q', '').lower()
    load_posts()
    results = [
        {
            "title": post["title"],
            "content": post["content"],
            "slug": post["slug"]
        }
        for post in posts_cache
        if query in post["title"].lower() or query in post["content"].lower()
    ][:5]
    return jsonify(results)

@app.route("/subscribe", methods=['GET', 'POST'])
def subscribe():
    # Render the subscribe page.
    if request.method == 'POST':
        name = request.form['full_name']
        email = request.form['email']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS subscribers (full_name TEXT, email TEXT)')
        c.execute('INSERT INTO subscribers (full_name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        conn.close()
        message = "Thank you for subscribing!"
        return render_template("/modals/subscribe.html", message=message)
    return render_template("/modals/subscribe.html")

@app.route("/legal")
def legal():
    # Render the legal information page.
    return render_template("modals/legal.html")

@app.errorhandler(404)
def page_not_found(e):
    # Render a custom 404 error page.
    return render_template("modals/404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)