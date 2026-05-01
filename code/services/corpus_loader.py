import hashlib
from pathlib import Path

import frontmatter

from models.schemas import Article
from config import DATA_DIR, PRODUCT_AREA_MAP


def _derive_product_area(rel_path: str) -> str:
    parts = rel_path.split("/")
    for depth in range(len(parts), 0, -1):
        candidate = "/".join(parts[:depth])
        if candidate in PRODUCT_AREA_MAP:
            return PRODUCT_AREA_MAP[candidate]
    return "general_support"


def _extract_domain(rel_path: str) -> str:
    return rel_path.split("/")[0]


def load_all_articles() -> list[Article]:
    articles = []
    for md_file in DATA_DIR.rglob("*.md"):
        if md_file.name == "index.md":
            continue

        rel_path = str(md_file.relative_to(DATA_DIR))
        domain = _extract_domain(rel_path)

        try:
            post = frontmatter.load(str(md_file))
        except Exception:
            continue

        title = post.get("title", md_file.stem)
        breadcrumbs_raw = post.get("breadcrumbs", [])
        breadcrumbs = breadcrumbs_raw if isinstance(breadcrumbs_raw, list) else []
        source_url = post.get("source_url", post.get("url", ""))
        content = post.content.strip()

        if not content:
            continue

        article_id = hashlib.md5(rel_path.encode()).hexdigest()
        product_area = _derive_product_area(rel_path)

        articles.append(
            Article(
                id=article_id,
                path=rel_path,
                domain=domain,
                title=str(title),
                content=content,
                product_area=product_area,
                breadcrumbs=breadcrumbs,
                source_url=str(source_url),
                metadata={
                    "last_updated": str(
                        post.get(
                            "last_updated_iso",
                            post.get("last_updated_exact", post.get("last_modified", "")),
                        )
                    )
                },
            )
        )

    print(f"Loaded {len(articles)} articles from {DATA_DIR}")
    return articles
