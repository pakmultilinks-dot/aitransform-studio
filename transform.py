"""Core content tools for AI Transform Studio.

Every function is deterministic and needs no API key, no network and no
secrets. The app is a working prototype of the aiTransform content tools:
it implements the transformations with real algorithms (extractive
summarization, Flesch readability formulas, frequency-based keywords,
AST-based code explanation) and template-based drafting.
"""
import ast
import math
import re
from collections import Counter

STOPWORDS = set("""
a an the and or but if then else for of to in on at by with from as is are was
were be been being have has had do does did will would shall should can could
may might must i you he she it we they this that these those there here what
when where who whom which why how all any both each few more most other some
such no nor not only own same so than too very just also because until while
about against between into through during before after above below up down out
off over under again further once am its it’s my your his her our their me him
us them my mine yours ours theirs
""".split())

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")


def split_sentences(text):
    """Split plain text into sentences, keeping the punctuation."""
    text = " ".join(text.split())
    if not text:
        return []
    parts = SENTENCE_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def words(text):
    return WORD_RE.findall(text.lower())


def count_syllables(word):
    """Heuristic syllable count: vowel groups, minus silent e, min 1."""
    word = word.lower().strip()
    if not word:
        return 0
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    if word.endswith("ed") and count > 1 and not word.endswith("ted") and not word.endswith("ded"):
        count -= 1
    return max(1, count)


def readability(text):
    """Flesch Reading Ease and Flesch-Kincaid Grade Level.

    Reading Ease = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    Grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    Returns a dict with counts plus both scores, rounded to 1 decimal.
    """
    sentences = split_sentences(text)
    ws = words(text)
    n_words = len(ws)
    n_sent = max(1, len(sentences))
    n_syll = sum(count_syllables(w) for w in ws)
    wps = n_words / n_sent if n_sent else 0
    spw = n_syll / n_words if n_words else 0
    ease = 206.835 - 1.015 * wps - 84.6 * spw
    grade = 0.39 * wps + 11.8 * spw - 15.59
    reading_minutes = max(1, math.ceil(n_words / 200)) if n_words else 0
    return {
        "words": n_words,
        "sentences": len(sentences),
        "syllables": n_syll,
        "words_per_sentence": round(wps, 1),
        "reading_ease": round(ease, 1),
        "grade_level": round(grade, 1),
        "reading_minutes": reading_minutes,
    }


def ease_label(score):
    if score >= 90:
        return "Very easy, a 5th grader can read it"
    if score >= 80:
        return "Easy, conversational English"
    if score >= 70:
        return "Fairly easy"
    if score >= 60:
        return "Standard, plain English"
    if score >= 50:
        return "Fairly difficult"
    if score >= 30:
        return "Difficult"
    return "Very difficult, academic level"


def keywords(text, top_n=10):
    """Most frequent meaningful words, with counts and density."""
    ws = [w for w in words(text) if w not in STOPWORDS and len(w) > 2]
    total = len(ws)
    counts = Counter(ws).most_common(top_n)
    return [
        {"word": w, "count": c,
         "density": round(100.0 * c / total, 1) if total else 0.0}
        for w, c in counts
    ]


def summarize(text, n_sentences=3):
    """Extractive summary: score each sentence by keyword frequency and
    keep the top n, in their original order."""
    sentences = split_sentences(text)
    if not sentences:
        return []
    if len(sentences) <= n_sentences:
        return sentences
    freq = Counter(w for w in words(text) if w not in STOPWORDS)
    scored = []
    for i, s in enumerate(sentences):
        score = sum(freq.get(w, 0) for w in words(s))
        score = score / max(1, len(words(s)))
        scored.append((score, i, s))
    scored.sort(key=lambda t: (-t[0], t[1]))
    picked = sorted(scored[:n_sentences], key=lambda t: t[1])
    return [s for _, _, s in picked]


def seo_title(topic, top_keywords):
    """SEO title suggestion, kept inside 60 characters."""
    title = topic.strip().title()
    if top_keywords:
        kw = top_keywords[0]["word"].title()
        if kw.lower() not in title.lower():
            candidate = f"{title}: {kw} Guide"
        else:
            candidate = f"{title} - Complete Guide"
    else:
        candidate = f"{title} - Complete Guide"
    if len(candidate) > 60:
        candidate = title[:57].rstrip() + "..."
    return candidate


def seo_meta(topic, top_keywords, text):
    """Meta description suggestion, kept inside 160 characters."""
    kws = ", ".join(k["word"] for k in top_keywords[:3])
    base = f"Learn {topic.strip().lower()}"
    if kws:
        base += f", including {kws}."
    else:
        base += " in this clear, practical guide."
    first = split_sentences(text)
    if first:
        extra = first[0]
        if len(base) + 1 + len(extra) <= 160:
            base = base + " " + extra
    if len(base) > 160:
        base = base[:157].rstrip() + "..."
    return base


SECTION_TITLES = [
    "What {topic} means",
    "Why {topic} matters now",
    "How {topic} works, step by step",
    "Common mistakes with {topic}",
    "Practical tips for {topic}",
    "Tools and resources for {topic}",
    "What to do next with {topic}",
]

TONE_OPENERS = {
    "Friendly": "Let's talk about {topic} in plain words.",
    "Professional": "{Topic} deserves a clear, practical look.",
    "Bold": "{Topic} is changing fast, and here is what actually matters.",
    "Simple": "{Topic} sounds complicated, but it is not.",
}


def build_outline(topic, keywords_list, tone="Friendly", n_sections=5):
    """Article outline: title, intro line, section headings, closing line."""
    topic = topic.strip()
    titles = [t.format(topic=topic) for t in SECTION_TITLES[:max(3, min(7, n_sections))]]
    opener = TONE_OPENERS.get(tone, TONE_OPENERS["Friendly"]).format(
        topic=topic.lower(), Topic=topic)
    kw_line = ", ".join(keywords_list) if keywords_list else "the basics"
    return {
        "title": seo_title(topic, [{"word": k} for k in keywords_list[:1]]),
        "opener": opener,
        "sections": titles,
        "keywords_line": kw_line,
        "closing": f"Start with one small step on {topic} today, then build from there.",
    }


def build_intro(topic, keywords_list, tone="Friendly"):
    outline = build_outline(topic, keywords_list, tone)
    kw = outline["keywords_line"]
    return (f"{outline['opener']} This guide covers {topic.lower()} from the "
            f"ground up, with a focus on {kw}. By the end you will know what "
            f"it is, why it matters, and exactly what to do next.")


def build_image_prompt(subject, style="Photorealistic", mood="Bright and hopeful",
                       lighting="Soft daylight", aspect="16:9"):
    """A detailed image-generation prompt assembled from the inputs."""
    return (f"{subject.strip()}, {style.lower()} style, {mood.lower()} mood, "
            f"{lighting.lower()}, highly detailed, sharp focus, professional "
            f"composition, aspect ratio {aspect}")


def explain_code(source):
    """Plain-language explanation of Python code, from its AST.

    Returns functions, classes, imports, counts and a short summary.
    Raises SyntaxError on code that does not parse.
    """
    tree = ast.parse(source)
    imports = []
    functions = []
    classes = []
    branches = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                               ast.With, ast.comprehension)):
            branches += 1
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "docstring": (ast.get_docstring(node) or "").strip()[:200],
                "lines": (node.end_lineno or 0) - (node.lineno or 0) + 1,
            })
        elif isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes.append({
                "name": node.name,
                "methods": methods,
                "docstring": (ast.get_docstring(node) or "").strip()[:200],
            })
    lines = [ln for ln in source.splitlines() if ln.strip()]
    summary = []
    if classes:
        summary.append(f"Defines {len(classes)} class(es): " +
                       ", ".join(c["name"] for c in classes) + ".")
    if functions:
        summary.append(f"Defines {len(functions)} top-level function(s): " +
                       ", ".join(f["name"] for f in functions) + ".")
    if imports:
        summary.append("Uses " + ", ".join(sorted(set(imports))) + ".")
    summary.append(f"{len(lines)} non-empty lines, about {branches} decision "
                   f"points (if/for/while/try blocks).")
    return {
        "imports": sorted(set(i for i in imports if i)),
        "functions": functions,
        "classes": classes,
        "lines": len(lines),
        "branches": branches,
        "summary": " ".join(summary),
    }
