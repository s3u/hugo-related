# hugo-related

Generate related post data for a Hugo site using local Sentence-Transformers embeddings.

## Features

- Scans content/articles/**/*.md
- Extracts title, slug, date from front matter
- Embeds full document text (BAAI/bge-large-en by default)
- Computes cosine similarity and stores top 5 related items
- Outputs data/related/index.json (no content file mutation)
- Ready for Hugo partial via .Site.Data.related.index

## Requirements

Python 3.9+
pip install sentence-transformers scikit-learn pyyaml

## Usage

From site repository root (where content/ lives):

```
python3 related/find-related.py
```

(If this repo is a submodule at related/, adjust path accordingly.)

## Hugo Template Example

```
{{ $db := .Site.Data.related.index }}
{{ $key := .File.Path }}
{{ if not (hasPrefix $key "/") }}{{ $key = print "/" $key }}{{ end }}
{{ with (index $db $key) }}
<ul class="related-posts">
  {{ range . }}
    <li><a href="{{ .url }}">{{ .title }}</a></li>
  {{ end }}
</ul>
{{ end }}
```

## Netlify Build
In netlify.toml:
```
[build]
  command = "python3 related/find-related.py && hugo --gc --minify"
```

## Environment Overrides
| Var | Default | Description |
|-----|---------|-------------|
| RELATED_ARTICLES_DIR | content/articles | Content root (relative to site root) |
| RELATED_URL_PREFIX | /articles/ | URL prefix |
| RELATED_DATA_OUT | data/related/index.json | Output JSON path |
| RELATED_TOP_N | 5 | Number of related links |
| RELATED_MODEL | BAAI/bge-large-en | Embedding model name |

Example:
```
RELATED_MODEL=all-MiniLM-L6-v2 RELATED_TOP_N=8 python3 related/find-related.py
```

## Changing the Model
Edit in script:
```
model = SentenceTransformer('BAAI/bge-large-en')
```
Swap with a faster model (e.g. all-MiniLM-L6-v2) if build time is high.

## Performance Tips
- Cache embeddings keyed by file hash (not implemented yet).
- Use smaller model for large corpora.
- Limit TOP_N to reduce JSON size.

## Output JSON Structure
```
{
  "/articles/2024/some-post.md": [
    { "title": "...", "url": "/articles/2024/other-post/", "date": "2024-07-01", "score": 0.7321 },
    ...
  ]
}
```

## License
MIT (adjust if different).

## Roadmap
- Embedding cache
- Optional BM25 fallback
- Tag/category boost
- CLI flags (argparse)

## Contributing
Fork, branch, PR.

```// filepath: /Users/subbu/web/hugo-related/README.md
# hugo-related

Generate related post data for a Hugo site using local Sentence-Transformers embeddings.

## Features
- Scans content/articles/**/*.md
- Extracts title, slug, date from front matter
- Embeds full document text (BAAI/bge-large-en by default)
- Computes cosine similarity and stores top 5 related items
- Outputs data/related/index.json (no content file mutation)
- Ready for Hugo partial via .Site.Data.related.index

## Requirements
Python 3.9+
pip install sentence-transformers scikit-learn pyyaml

## Usage
From site repository root (where content/ lives):
```
python3 related/find-related.py
```
(If this repo is a submodule at related/, adjust path accordingly.)

## Hugo Template Example
```
{{ $db := .Site.Data.related.index }}
{{ $key := .File.Path }}
{{ if not (hasPrefix $key "/") }}{{ $key = print "/" $key }}{{ end }}

{{ with (index $db $key) }}
    <h3>See Also</h3>
    <ul class="related-posts">
      {{ range . }}
        {{ $url := index . "url" }}
        {{ $title := index . "title" }}
        {{ $date := index . "date" }}
        {{ $score := index . "score" }}
        {{ $scoref := float $score }}
        {{ $pct := mul 100.0 $scoref }}
        <li>
          <a href="{{ absURL $url }}">{{ $title }}</a>{{ with $date }} <small>({{ printf "%.0f%%" $pct }} match, {{ dateFormat "Jan 2, 2006" (time .) }})</small>{{ end }}
        </li>
      {{ end }}
    </ul>
{{ end }}
```



## Netlify Build
In netlify.toml:
```
[build]
  command = "python3 related/find-related.py && hugo --gc --minify"
```

## Environment Overrides
| Var | Default | Description |
|-----|---------|-------------|
| RELATED_ARTICLES_DIR | content/articles | Content root (relative to site root) |
| RELATED_URL_PREFIX | /articles/ | URL prefix |
| RELATED_DATA_OUT | data/related/index.json | Output JSON path |
| RELATED_TOP_N | 5 | Number of related links |
| RELATED_MODEL | BAAI/bge-large-en | Embedding model name |

Example:
```
RELATED_MODEL=all-MiniLM-L6-v2 RELATED_TOP_N=8 python3 related/find-related.py
```

## Changing the Model
Edit in script:
```
model = SentenceTransformer('BAAI/bge-large-en')
```
Swap with a faster model (e.g. all-MiniLM-L6-v2) if build time is high.

## Performance Tips
- Cache embeddings keyed by file hash (not implemented yet).
- Use smaller model for large corpora.
- Limit TOP_N to reduce JSON size.

## Output JSON Structure
```
{
  "/articles/2024/some-post.md": [
    { "title": "...", "url": "/articles/2024/other-post/", "date": "2024-07-01", "score": 0.7321 },
    ...
  ]
}
```

## License
MIT (adjust if different).

## Roadmap
- Embedding cache
- Optional BM25 fallback
- Tag/category boost
- CLI flags (argparse)

## Contributing