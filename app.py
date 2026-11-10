"""AI Transform Studio - a working web application for aiTransform.com.

Five content tools that run entirely in the browser session, with no API
key, no account and no secrets: AI Writer, Summarizer, Readability and
SEO, Image Prompt Builder, and Code Explainer. Every transformation is
deterministic and implemented in transform.py; the draft builder is
template-based and says so on screen.
"""
import streamlit as st

from transform import (
    build_image_prompt,
    build_intro,
    build_outline,
    ease_label,
    explain_code,
    keywords,
    readability,
    seo_meta,
    seo_title,
    split_sentences,
    summarize,
)

st.set_page_config(page_title="AI Transform Studio", page_icon="✦",
                   layout="wide")

TOOLS = ["Home", "AI Writer", "Summarizer", "Readability & SEO",
         "Image Prompt Builder", "Code Explainer"]


def download_button(label, text, filename):
    st.download_button(label, data=text, file_name=filename,
                       mime="text/plain")


def home_page():
    st.title("✦ AI Transform Studio")
    st.write(
        "A working web application for aiTransform.com. Five content tools "
        "that run entirely in your browser session: no API key, no account, "
        "no data leaves the page.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tools", "5")
    with col2:
        st.metric("API keys needed", "0")
    with col3:
        st.metric("Cost to run", "Free")
    st.divider()
    st.subheader("What you can do here")
    st.write(
        "**AI Writer** — turn a topic and keywords into an article outline, "
        "an intro and a closing paragraph.\n\n"
        "**Summarizer** — paste long text and get the key sentences back.\n\n"
        "**Readability & SEO** — Flesch reading scores, keyword density, and "
        "SEO title and meta description suggestions.\n\n"
        "**Image Prompt Builder** — build a detailed prompt for any AI image "
        "generator from a subject, style, mood and lighting.\n\n"
        "**Code Explainer** — paste Python code and get a plain-language "
        "explanation of what it does.")
    st.info("How it works: the Writer uses templates, the Summarizer scores "
            "sentences by keyword frequency, Readability uses the standard "
            "Flesch formulas, and the Code Explainer reads the code's own "
            "structure. Nothing is faked and nothing is sent anywhere.")


def writer_page():
    st.title("AI Writer")
    st.write("Turn a topic into a structured article draft. The draft is "
             "built from templates around your own topic and keywords.")
    topic = st.text_input("Topic", "How to start a small online shop in Pakistan")
    kw_text = st.text_input("Keywords, comma separated",
                            "online shop, payment, delivery")
    tone = st.selectbox("Tone", ["Friendly", "Professional", "Bold", "Simple"])
    n_sections = st.slider("Sections", 3, 7, 5)
    if st.button("Build draft", type="primary"):
        kws = [k.strip() for k in kw_text.split(",") if k.strip()]
        outline = build_outline(topic, kws, tone, n_sections)
        st.subheader(topic.strip().title())
        st.caption("SEO title suggestion: " + outline["title"])
        st.write(build_intro(topic, kws, tone))
        st.subheader("Outline")
        for i, section in enumerate(outline["sections"], 1):
            st.write(f"{i}. {section}")
        st.subheader("Closing")
        st.write(outline["closing"])
        draft = (outline["title"] + "\n\n" + build_intro(topic, kws, tone) +
                 "\n\n" + "\n".join(f"{i}. {s}" for i, s in
                                     enumerate(outline["sections"], 1)) +
                 "\n\n" + outline["closing"])
        download_button("Download draft (.txt)", draft, "ai-writer-draft.txt")


def summarizer_page():
    st.title("Summarizer")
    st.write("Paste long text and keep only the sentences that carry the "
             "most meaning. Sentences are scored by keyword frequency and "
             "returned in their original order.")
    text = st.text_area("Text to summarize", height=220,
                        placeholder="Paste an article, a report or notes here...")
    n = st.slider("Sentences in the summary", 1, 5, 3)
    if st.button("Summarize", type="primary"):
        if not text.strip():
            st.warning("Paste some text first.")
        else:
            result = summarize(text, n)
            st.subheader("Summary")
            for sentence in result:
                st.write("• " + sentence)
            st.caption(f"Kept {len(result)} of "
                       f"{len(split_sentences(text))} sentences.")
            download_button("Download summary (.txt)",
                            "\n".join(result), "summary.txt")


def readability_page():
    st.title("Readability & SEO")
    st.write("Paste a page or article and get real readability scores, "
             "keyword density and SEO suggestions.")
    text = st.text_area("Text to analyse", height=220,
                        placeholder="Paste your article text here...")
    topic = st.text_input("Page topic (for the SEO title)",
                          "How to start a small online shop in Pakistan")
    if st.button("Analyse", type="primary"):
        if not text.strip():
            st.warning("Paste some text first.")
        else:
            scores = readability(text)
            kws = keywords(text, 10)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", scores["words"])
            with col2:
                st.metric("Reading ease", scores["reading_ease"])
            with col3:
                st.metric("Grade level", scores["grade_level"])
            st.write(f"**Reading level:** {ease_label(scores['reading_ease'])}")
            st.write(f"Sentences: {scores['sentences']} · "
                     f"Words per sentence: {scores['words_per_sentence']} · "
                     f"Reading time: about {scores['reading_minutes']} minute(s).")
            st.subheader("Top keywords")
            for kw in kws:
                st.write(f"{kw['word']} — {kw['count']} times "
                         f"({kw['density']}% density)")
            st.subheader("SEO suggestions")
            title = seo_title(topic, kws)
            meta = seo_meta(topic, kws, text)
            st.write(f"**Title ({len(title)} characters):** {title}")
            st.write(f"**Meta description ({len(meta)} characters):** {meta}")
            report = (f"Reading ease: {scores['reading_ease']} "
                      f"({ease_label(scores['reading_ease'])})\n"
                      f"Grade level: {scores['grade_level']}\n"
                      f"Words: {scores['words']}, sentences: {scores['sentences']}\n"
                      f"SEO title: {title}\nMeta description: {meta}\n")
            download_button("Download analysis (.txt)", report,
                            "readability-seo.txt")


def prompt_page():
    st.title("Image Prompt Builder")
    st.write("Describe the picture you want and get a detailed prompt, ready "
             "to paste into any AI image generator.")
    subject = st.text_input("Subject", "A busy Lahore bazaar at dusk")
    style = st.selectbox("Style", ["Photorealistic", "Digital painting",
                                   "Watercolor", "3D render", "Minimal flat",
                                   "Cinematic"])
    mood = st.selectbox("Mood", ["Bright and hopeful", "Calm and quiet",
                                 "Dramatic", "Playful", "Elegant"])
    lighting = st.selectbox("Lighting", ["Soft daylight", "Golden hour",
                                         "Neon night", "Studio light",
                                         "Moonlight"])
    aspect = st.selectbox("Aspect ratio", ["16:9", "1:1", "4:5", "9:16"])
    if st.button("Build prompt", type="primary"):
        prompt = build_image_prompt(subject, style, mood, lighting, aspect)
        st.subheader("Your prompt")
        st.write(prompt)
        st.caption(f"{len(prompt)} characters.")
        download_button("Download prompt (.txt)", prompt, "image-prompt.txt")


def code_page():
    st.title("Code Explainer")
    st.write("Paste Python code and get a plain-language explanation of what "
             "it does, built from the code's own structure.")
    sample = ('def total(items):\n    """Add up a list of prices."""\n'
              '    s = 0\n    for price in items:\n        s += price\n'
              '    return s\n')
    code = st.text_area("Python code", value=sample, height=220)
    if st.button("Explain", type="primary"):
        if not code.strip():
            st.warning("Paste some code first.")
        else:
            try:
                info = explain_code(code)
            except SyntaxError as exc:
                st.error(f"That code does not parse as Python: {exc}")
            else:
                st.subheader("What it does")
                st.write(info["summary"])
                if info["imports"]:
                    st.write("**Imports:** " + ", ".join(info["imports"]))
                if info["functions"]:
                    st.subheader("Functions")
                    for fn in info["functions"]:
                        args = ", ".join(fn["args"]) or "no arguments"
                        st.write(f"**{fn['name']}**({args}) — "
                                 f"{fn['lines']} lines")
                        if fn["docstring"]:
                            st.write(f"_{fn['docstring']}_")
                if info["classes"]:
                    st.subheader("Classes")
                    for cls in info["classes"]:
                        methods = ", ".join(cls["methods"]) or "no methods"
                        st.write(f"**{cls['name']}** — methods: {methods}")
                        if cls["docstring"]:
                            st.write(f"_{cls['docstring']}_")
                st.caption(f"{info['lines']} non-empty lines, "
                           f"{info['branches']} decision points.")


PAGES = {
    "Home": home_page,
    "AI Writer": writer_page,
    "Summarizer": summarizer_page,
    "Readability & SEO": readability_page,
    "Image Prompt Builder": prompt_page,
    "Code Explainer": code_page,
}

choice = st.sidebar.radio("Tools", TOOLS)
st.sidebar.divider()
st.sidebar.write("AI Transform Studio — a working prototype of the "
                 "aiTransform content tools. No API key, no account, no "
                 "data leaves the page.")
PAGES[choice]()
