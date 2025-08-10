# hugo-related

Generate related post data for a Hugo site using local Sentence-Transformers embeddings.

## Requirements

Python 3.9+

``` python3
pip install sentence-transformers scikit-learn pyyaml
```

## Usage

From site repository root (where content/ lives):

``` python3
python3 related/find-related.py
```

This will generate a related content index in `data/related/index.json`.

Then, update your Hugo template to show related articles. Here is an example.

``` Hugo
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

## Environment Overrides

```
| Var | Default | Description |
|-----|---------|-------------|
| RELATED_ARTICLES_DIR | content/articles | Content root (relative to site root) |
| RELATED_URL_PREFIX | /articles/ | URL prefix |
| RELATED_DATA_OUT | data/related/index.json | Output JSON path |
| RELATED_TOP_N | 5 | Number of related links |
| RELATED_MODEL | BAAI/bge-large-en | Embedding model name |
```