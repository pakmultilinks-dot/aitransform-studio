"""Tests for the AI Transform Studio core tools. Run: pytest tests/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transform import (
    build_image_prompt, build_intro, build_outline, count_syllables,
    ease_label, explain_code, keywords, readability, seo_meta, seo_title,
    split_sentences, summarize, words,
)

SAMPLE = ("Solar panels turn sunlight into electricity. A typical home system "
          "in Lahore has 10 panels and covers most of the daytime load. "
          "The panels last 25 years with little maintenance. "
          "Net metering lets owners sell extra power back to the grid. "
          "The upfront cost is high, but the payback period is usually "
          "four to six years.")


def test_split_sentences():
    assert len(split_sentences(SAMPLE)) == 5
    assert split_sentences("") == []
    assert split_sentences("One sentence.") == ["One sentence."]


def test_words():
    assert words("Hello, World!") == ["hello", "world"]


def test_count_syllables():
    assert count_syllables("cat") == 1
    assert count_syllables("electricity") == 5
    assert count_syllables("beautiful") == 3


def test_readability_easy_text_scores_high():
    text = "The cat sat on the mat. It was a sunny day. The dog ran fast."
    r = readability(text)
    assert r["words"] == 15
    assert r["sentences"] == 3
    assert r["reading_ease"] > 90
    assert r["grade_level"] < 3


def test_readability_counts():
    r = readability(SAMPLE)
    assert r["words"] == 54
    assert r["sentences"] == 5
    assert r["reading_minutes"] >= 1
    assert 0 <= r["reading_ease"] <= 100


def test_ease_label_bands():
    assert "Very easy" in ease_label(95)
    assert "Standard" in ease_label(65)
    assert "Very difficult" in ease_label(10)


def test_keywords_finds_repeated_word():
    kws = keywords(SAMPLE, 5)
    top = [k["word"] for k in kws]
    assert "panels" in top
    assert all(k["count"] >= 1 for k in kws)
    assert all("density" in k for k in kws)


def test_summarize_keeps_top_sentences_in_order():
    out = summarize(SAMPLE, 2)
    assert len(out) == 2
    assert out[0] in SAMPLE and out[1] in SAMPLE
    assert SAMPLE.index(out[0]) < SAMPLE.index(out[1])


def test_summarize_short_text_returns_all():
    assert summarize("Only one sentence.", 3) == ["Only one sentence."]


def test_seo_title_length():
    t = seo_title("How to start a small online shop in Pakistan",
                  [{"word": "shop"}])
    assert len(t) <= 60
    assert "shop" in t.lower() or "Shop" in t


def test_seo_meta_length():
    m = seo_meta("solar panels", [{"word": "panels"}], SAMPLE)
    assert len(m) <= 160
    assert "solar panels" in m.lower()


def test_build_outline_sections():
    o = build_outline("solar panels", ["panels", "cost"], "Friendly", 5)
    assert len(o["sections"]) == 5
    assert all("solar panels" in s for s in o["sections"])
    assert o["title"]
    assert o["closing"]


def test_build_intro_mentions_topic_and_keywords():
    intro = build_intro("solar panels", ["panels", "cost"], "Simple")
    assert "solar panels" in intro.lower()
    assert "panels" in intro.lower()


def test_image_prompt_contains_inputs():
    p = build_image_prompt("A Lahore bazaar", "Watercolor", "Calm and quiet",
                           "Moonlight", "1:1")
    assert "A Lahore bazaar" in p
    assert "watercolor" in p
    assert "moonlight" in p
    assert "1:1" in p


def test_explain_code_finds_function_and_import():
    code = "import math\n\ndef area(r):\n    \"\"\"Circle area.\"\"\"\n    return math.pi * r * r\n"
    info = explain_code(code)
    assert "math" in info["imports"]
    assert [f["name"] for f in info["functions"]] == ["area"]
    assert info["functions"][0]["args"] == ["r"]
    assert "Circle area" in info["functions"][0]["docstring"]
    assert "area" in info["summary"]


def test_explain_code_finds_class():
    code = "class Shop:\n    def __init__(self):\n        self.items = []\n"
    info = explain_code(code)
    assert [c["name"] for c in info["classes"]] == ["Shop"]
    assert info["classes"][0]["methods"] == ["__init__"]


def test_explain_code_bad_syntax_raises():
    try:
        explain_code("def broken(:\n")
    except SyntaxError:
        pass
    else:
        raise AssertionError("expected SyntaxError")
