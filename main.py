# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "markdown",
#     "rich",
#     "typer",
# ]
# ///


from typing import Annotated, Optional
import shutil
import markdown
from pathlib import Path
from datetime import datetime
import random
import string
import json

from typer import Typer
import typer
from rich import get_console, print


app = Typer()
console = get_console()

BASE_URL = None


SOURCE_DIR = Path("content")
TEST_DIR = Path("test_site")
DEPLOY_DIR = Path("docs")
BUILD_CACHE = Path(".build_cache.json")

WEBSITE_URL = "https://farbdrucker.github.io/"

# These will be set by the build command
OUTPUT_DIR = None
HOME_INDEX = None

# HTML templates
HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="{base}/style.css">
</head>
<body>
<header>
  <h1><a href="{base}">My Blog</a></h1>
</header>
<main>
"""

HTML_FOOT = """
</main>
<footer>
  <p>Generated {date}</p>
</footer>
</body>
</html>
"""


def load_build_cache():
    """Load the build cache to track which files have been rendered."""
    if BUILD_CACHE.exists():
        with open(BUILD_CACHE, "r") as f:
            return json.load(f)
    return {}


def save_build_cache(cache):
    """Save the build cache."""
    with open(BUILD_CACHE, "w") as f:
        json.dump(cache, f, indent=2)


def strip_metadata(content: str) -> str:
    """Strip YAML frontmatter from markdown content."""
    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        # Find the closing ---
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                # Return content after the closing ---
                return "\n".join(lines[i + 1 :])
    return content


def collect_articles(force_files: Optional[list[Path]] = None):
    """Collect all markdown files with metadata."""
    articles = []
    cache = load_build_cache()

    console.log(f"Looking for *.md files at {SOURCE_DIR}")
    for md_file in SOURCE_DIR.rglob("*.md"):
        console.log(f"Found {md_file}")
        rel = md_file.relative_to(SOURCE_DIR)
        year = rel.parts[0]
        slug = md_file.stem
        url = f"{BASE_URL}/articles/{year}/{slug}/"
        mtime = md_file.stat().st_mtime

        # Check if file needs to be rebuilt
        cache_key = str(md_file)
        needs_rebuild = (
            force_files
            and md_file in force_files
            or cache_key not in cache
            or cache[cache_key] != mtime
        )

        articles.append(
            {
                "path": md_file,
                "year": year,
                "slug": slug,
                "url": url,
                "mtime": datetime.fromtimestamp(mtime),
                "mtime_ts": mtime,
                "needs_rebuild": needs_rebuild,
            }
        )

    # sort newest first
    return sorted(articles, key=lambda a: a["mtime"], reverse=True)


def render_article(article, articles):
    """Render one article into HTML with navigation."""
    content = article["path"].read_text()
    content = strip_metadata(content)
    html = markdown.markdown(content, extensions=["fenced_code", "tables"])

    idx = articles.index(article)
    prev_articles = articles[idx + 1 : idx + 4]  # next 3 newer

    nav = "<nav><ul>"
    nav += f'<li><a href="{BASE_URL}">🏠 Home</a></li>'
    for prev in prev_articles:
        nav += f'<li><a href="{prev["url"]}">{prev["slug"].replace("_", " ")}</a></li>'
    nav += "</ul></nav>"

    content = (
        HTML_HEAD.format(title=article["slug"], base=BASE_URL)
        + f"<article><h2>{article['slug'].replace('_',' ').title()}</h2>{html}</article>"
        + nav
        + HTML_FOOT.format(date=datetime.now().strftime("%Y-%m-%d"))
    )
    return content


def write_article(article, html):
    outdir = OUTPUT_DIR / "articles" / article["year"] / article["slug"]
    outdir.mkdir(parents=True, exist_ok=True)
    console.log(f"Writing article {article['slug']} at {outdir}/index.html")
    with open(outdir / "index.html", "w") as f:
        f.write(html)


def render_home(articles):
    items = "<ul>"
    for art in articles:
        items += f'<li><a href="{art["url"]}">{art["slug"].replace("_", " ")}</a></li>'
    items += "</ul>"

    return (
        HTML_HEAD.format(title="Home", base=BASE_URL)
        + "<h2>Articles</h2>"
        + items
        + HTML_FOOT.format(date=datetime.now().strftime("%Y-%m-%d"))
    )


def random_base64(n: int) -> str:
    alphabet = string.ascii_letters + string.digits + "+/"
    return "".join(random.choice(alphabet) for _ in range(n))


@app.command()
def build(
    test: bool = typer.Option(
        False, "--test", help="Build to test directory instead of deploy"
    ),
    files: Optional[list[str]] = typer.Argument(
        None, help="Specific markdown files to rebuild"
    ),
):
    global BASE_URL, OUTPUT_DIR, HOME_INDEX

    if test:
        OUTPUT_DIR = TEST_DIR
        BASE_URL = str(Path().cwd() / TEST_DIR)
        console.log(f"[yellow]Building for local testing to {OUTPUT_DIR}[/yellow]")
    else:
        OUTPUT_DIR = DEPLOY_DIR
        BASE_URL = WEBSITE_URL
        console.log(f"[green]Building for deployment to {OUTPUT_DIR}[/green]")

    HOME_INDEX = OUTPUT_DIR / "index.html"

    # Parse force files if provided
    force_files = []
    if files:
        for f in files:
            p = Path(f)
            if not p.exists():
                console.log(f"[yellow]Warning: {f} does not exist[/yellow]")
            else:
                force_files.append(p)

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    articles = collect_articles(force_files=force_files if force_files else None)

    # Track which articles were rebuilt
    rebuilt_count = 0
    cache = load_build_cache()

    for article in articles:
        if article["needs_rebuild"]:
            html = render_article(article, articles)
            write_article(article, html)
            cache[str(article["path"])] = article["mtime_ts"]
            rebuilt_count += 1
        else:
            console.log(f"[dim]Skipping {article['slug']} (unchanged)[/dim]")

    # Always regenerate home page
    HOME_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(HOME_INDEX, "w") as f:
        f.write(render_home(articles))

    # Save the build cache
    save_build_cache(cache)

    print(f"✅ Built {rebuilt_count}/{len(articles)} articles into {OUTPUT_DIR}")


@app.command()
def new(title: Optional[str] = None):
    title = title or "Untitled"
    year = datetime.now().year

    base_path = SOURCE_DIR / str(year)
    base_path.mkdir(parents=True, exist_ok=True)
    fname = f"{title}_{random_base64(5)}.md"

    if not (base_path / fname).exists():
        print(f"Creating new blog draft at {base_path / fname}")
        with open(base_path / fname, "w") as f:
            f.writelines(
                [
                    "---\n",
                    f"title: {title}\n",
                    f"date: {datetime.now().strftime('%Y-%m-%d')}\n",
                    "---\n\n",
                    f"# {title}\n\n",
                    "Your content here...\n",
                ]
            )
    else:
        print(f"Blog post {base_path / fname} already exists")


if __name__ == "__main__":
    app()
