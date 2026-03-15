# Export Article to Bootstrap 5 HTML

Converts a finalized markdown article into a clean, Bootstrap 5-ready HTML fragment — no `<html>`, `<head>`, `<header>`, or `<footer>`. Includes Schema.org JSON-LD structured data. Drop it straight into any Bootstrap 5 template.

## Usage
`/html-export [file]`

### Examples
```
/html-export drafts/speed-dating-tips-2026-03-14.md
/html-export published/what-to-expect-at-a-speed-dating-event.md
/html-export rewrites/dating-app-alternatives-rewrite-2026-02-01.md
```

## What This Command Does

1. **Reads the source file** — parses frontmatter metadata and article body
2. **Detects schema types** — determines which Schema.org types apply based on content
3. **Generates JSON-LD** — outputs structured data block above the article
4. **Converts Markdown to Bootstrap 5 HTML** — applies correct classes to every element
5. **Strips non-content blocks** — removes SEO checklists, agent reports, and frontmatter
6. **Saves the output** — writes to `exports/[original-filename].html`
7. **Reports the result** — confirms output path, schema types used, and any notes

---

## Schema.org Structured Data

### Step 1: Detect Schema Types

Analyze the article content and apply the following detection rules:

| Schema Type | Always include? | Detection rule |
|---|---|---|
| `BlogPosting` | ✅ Yes | Always — every article gets this |
| `FAQPage` | If detected | Article contains a section with 3+ Q&A pairs (question as heading/bold, answer as paragraph) |
| `HowTo` | If detected | H1 starts with "How to", "How To", or article contains a numbered step section with 3+ steps |

A single article can have multiple schema blocks — output each as its own `<script type="application/ld+json">` tag.

---

### BlogPosting Schema

Always output this block. Extract values from the article and frontmatter:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[H1 title — max 110 characters]",
  "description": "[Meta description if present in frontmatter, otherwise first paragraph trimmed to 160 chars]",
  "image": "[First image URL found in article, or omit property if no images]",
  "author": {
    "@type": "Organization",
    "name": "[Brand name from context/brand-voice.md, or '[AUTHOR]' if not found]"
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Brand name from context/brand-voice.md, or '[PUBLISHER]' if not found]",
    "logo": {
      "@type": "ImageObject",
      "url": "[LOGO_URL]"
    }
  },
  "datePublished": "[Date from filename (YYYY-MM-DD format) or today's date]",
  "dateModified": "[Today's date in YYYY-MM-DD format]",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "[URL slug from frontmatter if present, otherwise '[PAGE_URL]']"
  },
  "keywords": "[Target keyword from frontmatter if present, otherwise omit]",
  "articleSection": "[Category from frontmatter if present, otherwise omit]"
}
</script>
```

**Extraction rules**:
- `headline`: The H1 heading from the article (strip markdown formatting)
- `description`: Look for `**Meta Description**:` line in frontmatter block; if not found, use first paragraph
- `image`: First `![alt](url)` found in article body; omit the property entirely if none
- `datePublished`: Parse date from filename (e.g. `article-name-2026-03-14.md` → `2026-03-14`); fall back to today
- `dateModified`: Always today's date
- Brand name: Read from `context/brand-voice.md` first line/title; use `[AUTHOR]` placeholder if file unavailable

---

### FAQPage Schema

Include only if 3 or more Q&A pairs are detected. Detection patterns:

- A heading (H2, H3, or **bold line**) that reads as a question (ends with `?`, or starts with What/How/Why/When/Where/Is/Are/Can/Should/Do/Does/Which/Who)
- Followed immediately by one or more paragraphs as the answer
- These pairs can be in a dedicated "FAQ" section or scattered throughout the article

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question text — exact heading or bold text]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer text — paragraph(s) following the question, plain text, max 300 chars recommended]"
      }
    },
    {
      "@type": "Question",
      "name": "[Next question]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Next answer]"
      }
    }
  ]
}
</script>
```

**Important**: Include ALL detected Q&A pairs, not just the first few. Strip markdown formatting from both questions and answers in the schema values.

---

### HowTo Schema

Include only if the H1 starts with "How to" OR the article contains a numbered list section with 3+ steps (ordered list `1. 2. 3.`).

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[H1 title]",
  "description": "[Meta description or first paragraph, max 160 chars]",
  "totalTime": "PT[X]M",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "[Step heading if present, otherwise first sentence of step]",
      "text": "[Full step text, plain text, markdown stripped]"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "[Step 2 heading or first sentence]",
      "text": "[Step 2 text]"
    }
  ]
}
</script>
```

**Extraction rules**:
- `name`: Same as the H1 title
- `step`: Map each numbered list item (`1.`, `2.`, etc.) to a HowToStep. If a numbered item has a following paragraph, include both as the `text` value
- `totalTime`: Omit this property if no time estimate is mentioned in the article; if "X minutes" appears near the steps, format as `PTXm` (e.g. `PT15M`)
- `position`: Use the original list numbering

---

## Output Structure

The final file is structured as follows — schema blocks first, then the article:

```html
<!-- ============================================================
     SCHEMA.ORG STRUCTURED DATA
     Place this in <head> or immediately before </body>
     ============================================================ -->

[BlogPosting JSON-LD block — always present]

[FAQPage JSON-LD block — only if FAQ pairs detected]

[HowTo JSON-LD block — only if how-to content detected]

<!-- ============================================================
     ARTICLE CONTENT
     Bootstrap 5 fragment — paste inside your page layout
     ============================================================ -->

<article class="seo-article py-4">

  <!-- Article Header -->
  <header class="article-header mb-5">
    <h1 class="display-5 fw-bold mb-3">[H1 from article]</h1>
    <p class="lead text-muted mb-0">[First paragraph]</p>
  </header>

  <!-- Article Body -->
  <div class="article-body">
    [All remaining content converted with Bootstrap classes]
  </div>

</article>
```

---

## Bootstrap 5 Conversion Rules

Apply these class mappings exactly when converting:

### Headings
```
# H1  → <h1 class="display-5 fw-bold mb-4">[text]</h1>
## H2  → <h2 class="h3 fw-semibold mt-5 mb-3">[text]</h2>
### H3 → <h3 class="h5 fw-semibold mt-4 mb-2">[text]</h3>
#### H4 → <h4 class="h6 fw-semibold mt-3 mb-2">[text]</h4>
```

### Body Text
```
Paragraph → <p class="lead mb-4"> (first paragraph after H1 only)
Paragraph → <p class="mb-4">[text]</p> (all other paragraphs)
```

### Lists
```
Unordered list  → <ul class="mb-4 ps-3">
Ordered list    → <ol class="mb-4 ps-3">
List item       → <li class="mb-2">[text]</li>
```

### Emphasis & Inline
```
**bold**    → <strong>[text]</strong>
*italic*    → <em>[text]</em>
`code`      → <code class="bg-light px-1 rounded">[text]</code>
[text](url) → <a href="[url]" class="text-decoration-underline">[text]</a>
```

### Blockquotes
```
> quote → <blockquote class="blockquote border-start border-3 border-primary ps-4 py-2 my-4">
            <p class="mb-0 fst-italic">[text]</p>
          </blockquote>
```

### Code Blocks
````
```lang       → <div class="bg-light rounded p-3 mb-4">
code            <pre class="mb-0"><code>[text]</code></pre>
```           </div>
````

### Tables
```
| table | → <div class="table-responsive mb-4">
              <table class="table table-bordered table-striped align-middle">
                <thead class="table-dark">
                  <tr><th>[col]</th>...</tr>
                </thead>
                <tbody>
                  <tr><td>[cell]</td>...</tr>
                </tbody>
              </table>
            </div>
```

### Images
```
![alt](url) → <figure class="figure mb-4 w-100">
                <img src="[url]" alt="[alt]" class="figure-img img-fluid rounded">
                <figcaption class="figure-caption text-muted">[alt]</figcaption>
              </figure>
```

### Horizontal Rules
```
--- → <hr class="my-5">
```

---

## What to Strip

Remove these blocks entirely — they are internal SEO Machine metadata, not content:

- YAML/TOML frontmatter blocks (between `---` delimiters at the top)
- Any section starting with `## SEO Analysis`, `## Meta Elements`, `## SEO Checklist`
- Agent report blocks (lines starting with `> **SEO Optimizer**`, `> **Meta Creator**`, etc.)
- Lines containing `**Target Keyword**:`, `**Meta Title**:`, `**Meta Description**:`, `**URL Slug**:`, `**Category**:`, `**Tags**:`
- Publishing checklists (`- [ ]` and `- [x]` lines in SEO/checklist sections)

---

## Process

### Step 1: Read and Parse
- Open the specified file
- Read frontmatter metadata: meta description, target keyword, URL slug, category, date
- Extract H1 title and first paragraph
- Identify and strip all non-content blocks

### Step 2: Detect Schema Types
- Scan for FAQ patterns (question headings/bold followed by answers)
- Check H1 for "How to" and scan for numbered step lists
- Note which schema types will be output

### Step 3: Generate Schema JSON-LD
- Build BlogPosting block (always)
- Build FAQPage block if ≥3 Q&A pairs found
- Build HowTo block if how-to content detected
- Flag any placeholder values that need manual completion (`[LOGO_URL]`, `[PAGE_URL]`, etc.)

### Step 4: Convert Article to Bootstrap HTML
- Apply all Bootstrap 5 class mappings
- Convert the entire article body section by section
- Preserve all internal and external links intact
- Do not alter any text content — only wrap in HTML

### Step 5: Save Output
```
exports/[original-filename-without-extension].html
```
Create the `exports/` directory if it doesn't exist.

### Step 6: Report
Display:
- Output file path
- Schema types included (e.g. "BlogPosting + FAQPage")
- Number of FAQ pairs detected (if any)
- Number of HowTo steps detected (if any)
- List of placeholder values that need manual completion
- Reminder that schema blocks should go in `<head>` or before `</body>` in the parent template

---

## Notes

- The output is a **fragment only** — no `<html>`, `<head>`, or `<body>` tags
- Schema `<script>` blocks can live in `<head>` or anywhere before `</body>` — most CMS platforms accept either
- Bootstrap 5 CSS must be loaded by the parent template (CDN or compiled)
- No inline styles are added — all styling comes from Bootstrap utility classes
- Internal links are preserved as-is; update slugs to match your live URLs before publishing
- Images are referenced by their original URL — host images separately if needed
- `[LOGO_URL]` and `[PAGE_URL]` placeholders must be filled in manually or configured in `context/brand-voice.md`
