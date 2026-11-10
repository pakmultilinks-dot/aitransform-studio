# AI Transform Studio

A working web application for aiTransform.com. Five content tools that run
entirely in the browser session, with no API key, no account and no secrets:

1. **AI Writer** — turn a topic and keywords into an article outline, an
   intro paragraph and a closing paragraph. Template-based, and it says so
   on screen.
2. **Summarizer** — paste long text and keep the sentences that carry the
   most meaning. Sentences are scored by keyword frequency and returned in
   their original order.
3. **Readability & SEO** — Flesch Reading Ease and Flesch-Kincaid Grade
   Level (the standard formulas), keyword density, and SEO title and meta
   description suggestions kept inside 60 and 160 characters.
4. **Image Prompt Builder** — build a detailed prompt for any AI image
   generator from a subject, style, mood, lighting and aspect ratio.
5. **Code Explainer** — paste Python code and get a plain-language
   explanation built from the code's own structure (AST): imports,
   functions, classes, line counts and decision points.

## Approach

The tools are deterministic and need no external service. That is a
deliberate choice: the app works offline, costs nothing to run, and every
result can be checked by hand. The Writer uses templates around the user's
own topic and keywords; nothing is presented as a language model. A real
language-model backend can be added later behind an API key, but this
version proves the workflow end to end without one.

## Data source

No real customer data is used anywhere. The sample inputs in
`sample_inputs/` are short texts written for this project, and the
evaluation in `evaluation/` runs the tools on them.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Open http://localhost:8501. A `.env.example` file is included; the app
needs no secrets, which the file states.

## Evaluation

Run the tests and the evaluation:

```bash
.venv/bin/python -m pytest tests/ -q
python evaluation/run_evaluation.py
```

- Tests: 17 tests covering sentence splitting, syllable counting,
  readability formulas, keyword extraction, summarization, SEO length
  limits, outline building, image prompts and code explanation.
  All 17 pass.
- Evaluation on the sample article (93 words, 8 sentences): reading ease
  69.5 (Fairly easy), grade level 6.5, about 1 minute to read. The
  2-sentence summary keeps the original sentence order. The SEO title is
  inside 60 characters and the meta description inside 160 characters.
  Full results in `evaluation/results.md`.

## Limitations

- The Writer drafts from templates, so its output is structured but not
  creative; it is a starting point, not a finished article.
- The Summarizer is extractive: it picks existing sentences, it never
  writes new ones.
- Readability formulas measure sentence and word length, not whether the
  writing is actually clear.
- The Code Explainer reads Python only, and it explains structure, not
  intent or bugs.
- Very long texts are processed in memory in one go.
