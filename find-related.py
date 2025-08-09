import os
import yaml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
from pathlib import Path
import datetime

ARTICLES_DIR = "./content/articles"
PREFIX = "/articles/"
DATA_OUT = "./data/related/index.json"

def extract_yaml_and_body(content):
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        end_idx = 1
        while end_idx < len(lines) and lines[end_idx].strip() != "---":
            end_idx += 1
        yaml_str = "\n".join(lines[1:end_idx])
        body = "\n".join(lines[end_idx+1:])
        return yaml.safe_load(yaml_str), yaml_str, end_idx, body
    return {}, "", 0, content

def collect_markdown_files(articles_dir):
    docs, filenames, full_paths, slugs, dates = [], [], [], {}, {}
    for root, _, files in os.walk(articles_dir):
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    docs.append(content)
                    filenames.append(os.path.relpath(full_path, articles_dir))
                    full_paths.append(full_path)
                    lines = content.splitlines()
                    if lines and lines[0].strip() == "---":
                        end_idx = 1
                        while end_idx < len(lines) and lines[end_idx].strip() != "---":
                            end_idx += 1
                        yaml_str = "\n".join(lines[1:end_idx])
                        try:
                            meta = yaml.safe_load(yaml_str)
                            if meta:
                                if "slug" in meta:
                                    slugs[full_path] = meta["slug"]
                                if "date" in meta:
                                    d = meta["date"]
                                    if isinstance(d, (datetime.date, datetime.datetime)):
                                        dates[full_path] = d.isoformat()
                                    else:
                                        dates[full_path] = str(d)
                        except Exception:
                            pass
    return docs, filenames, full_paths, slugs, dates

def main():
    docs, filenames, full_paths, slugs, dates = collect_markdown_files(ARTICLES_DIR)
    print(f"Found {len(docs)} markdown files.")

    model = SentenceTransformer('BAAI/bge-large-en')
    embeddings = model.encode(docs, convert_to_tensor=True)
    similarity = cosine_similarity(embeddings.cpu().numpy())

    related_db = {}

    for idx, fname in enumerate(filenames):
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = [s for s in sim_scores if s[0] != idx]
        sim_scores.sort(key=lambda x: x[1], reverse=True)
        top_related = sim_scores[:5]

        items = []
        for ridx, score in top_related:
            related_content = docs[ridx]
            related_yaml, _, _, _ = extract_yaml_and_body(related_content)
            related_title = related_yaml.get("title", filenames[ridx])

            rel_path = filenames[ridx]
            subdir = os.path.dirname(rel_path)
            slug = slugs.get(full_paths[ridx])
            date = dates.get(full_paths[ridx], "")
            if isinstance(date, (datetime.date, datetime.datetime)):
                date = date.isoformat()
            elif date is None:
                date = ""

            if slug:
                url = f"{PREFIX}{subdir}{slug}/"
            else:
                url = f"{PREFIX}{filenames[ridx][:-3]}/"

            items.append({
                "title": str(related_title),
                "url": url,
                "date": date,
                "score": float(score),
            })

        # key the entry by the source page's content path so Hugo can use .File.Path
        related_db[PREFIX + fname] = items

    # ensure data dir exists and write JSON
    out_path = Path(DATA_OUT)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # print(json)  # remove noisy debug print

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(related_db, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()