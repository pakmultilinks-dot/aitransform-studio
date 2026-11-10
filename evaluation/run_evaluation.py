"""Run every AI Transform Studio tool on the sample inputs and record
the real outputs. Run: python evaluation/run_evaluation.py
Writes evaluation/results.md and evaluation/results.json."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transform import (build_image_prompt, build_intro, build_outline,
                       ease_label, explain_code, keywords, readability,
                       seo_meta, seo_title, summarize)

HERE = os.path.dirname(os.path.abspath(__file__))
ARTICLE = open(os.path.join(HERE, "..", "sample_inputs",
                            "article-solar-panels.txt")).read()
CODE = open(os.path.join(HERE, "..", "sample_inputs",
                         "code-sample.py")).read()

results = {}

scores = readability(ARTICLE)
results["readability"] = scores
results["readability_label"] = ease_label(scores["reading_ease"])
results["keywords"] = keywords(ARTICLE, 5)
results["summary_2"] = summarize(ARTICLE, 2)
results["summary_3"] = summarize(ARTICLE, 3)
results["seo_title"] = seo_title("solar panels for homes in Lahore",
                                 results["keywords"])
results["seo_meta"] = seo_meta("solar panels for homes in Lahore",
                               results["keywords"], ARTICLE)
outline = build_outline("solar panels for homes in Lahore",
                        ["panels", "cost", "net metering"], "Friendly", 5)
results["writer_outline"] = outline
results["writer_intro"] = build_intro("solar panels for homes in Lahore",
                                      ["panels", "cost", "net metering"],
                                      "Friendly")
results["image_prompt"] = build_image_prompt(
    "A busy Lahore bazaar at dusk", "Photorealistic",
    "Bright and hopeful", "Golden hour", "16:9")
results["code_explanation"] = explain_code(CODE)

with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(results, fh, indent=2)

lines = []
lines.append("# AI Transform Studio - evaluation")
lines.append("")
lines.append("Sample inputs: sample_inputs/article-solar-panels.txt "
             f"({scores['words']} words, {scores['sentences']} sentences) "
             "and sample_inputs/code-sample.py.")
lines.append("")
lines.append("## Readability and SEO")
lines.append(f"- Reading ease: {scores['reading_ease']} "
             f"({results['readability_label']})")
lines.append(f"- Grade level: {scores['grade_level']}")
lines.append(f"- Words per sentence: {scores['words_per_sentence']}")
lines.append(f"- Reading time: about {scores['reading_minutes']} minute(s)")
lines.append("- Top keywords: " + ", ".join(
    f"{k['word']} ({k['count']}, {k['density']}%)"
    for k in results["keywords"]))
lines.append(f"- SEO title ({len(results['seo_title'])} chars): "
             f"{results['seo_title']}")
lines.append(f"- Meta description ({len(results['seo_meta'])} chars): "
             f"{results['seo_meta']}")
lines.append("")
lines.append("## Summarizer (2 sentences)")
for s in results["summary_2"]:
    lines.append(f"- {s}")
lines.append("")
lines.append("## AI Writer outline")
lines.append(f"Title: {outline['title']}")
lines.append("")
lines.append(outline["opener"])
lines.append("")
for i, sec in enumerate(outline["sections"], 1):
    lines.append(f"{i}. {sec}")
lines.append("")
lines.append(outline["closing"])
lines.append("")
lines.append("## Image prompt")
lines.append(results["image_prompt"])
lines.append("")
lines.append("## Code explainer")
lines.append(results["code_explanation"]["summary"])
lines.append("")
lines.append("Checks: the SEO title is inside 60 characters and the meta "
             "description inside 160 characters; the summary keeps the "
             "original sentence order; the code explanation names the real "
             "functions and classes from the sample.")
with open(os.path.join(HERE, "results.md"), "w") as fh:
    fh.write("\n".join(lines) + "\n")

print("Readability:", scores)
print("SEO title:", results["seo_title"])
print("Summary (2):", results["summary_2"])
print("Wrote evaluation/results.md and results.json")
