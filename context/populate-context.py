#!/usr/bin/env python3
"""
populate-context.py
-------------------
Reads context/_onboarding-questionnaire.md and writes all SEO Machine
context files from the answers inside it.

Usage:
    python3 context/populate-context.py

Run from the repo root. Skips any field still showing [ANSWER].
"""

import re
import sys
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONNAIRE = os.path.join(SCRIPT_DIR, "_onboarding-questionnaire.md")

CONTEXT = {
    "brand_voice":        os.path.join(SCRIPT_DIR, "brand-voice.md"),
    "features":           os.path.join(SCRIPT_DIR, "features.md"),
    "style_guide":        os.path.join(SCRIPT_DIR, "style-guide.md"),
    "competitor":         os.path.join(SCRIPT_DIR, "competitor-analysis.md"),
    "internal_links":     os.path.join(SCRIPT_DIR, "internal-links-map.md"),
    "target_keywords":    os.path.join(SCRIPT_DIR, "target-keywords.md"),
    "seo_guidelines":     os.path.join(SCRIPT_DIR, "seo-guidelines.md"),
    "writing_examples":   os.path.join(SCRIPT_DIR, "writing-examples.md"),
}

TODAY = datetime.now().strftime("%B %d, %Y")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_questionnaire():
    with open(QUESTIONNAIRE, "r") as f:
        return f.read()

def get_answer(text, question_pattern):
    """
    Extract the answer line(s) immediately after a bold question label.
    Returns None if answer is still [ANSWER] or empty.
    """
    pattern = rf"\*\*{re.escape(question_pattern)}\*\*\s*\n(.+?)(?=\n\*\*|\n---|\n##|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    answer = match.group(1).strip()
    if not answer or answer == "[ANSWER]" or answer.startswith("[ANSWER]"):
        return None
    return answer

def get_numbered_answers(text, question_pattern):
    """Return answers for numbered sub-items like 1. [ANSWER] 2. [ANSWER]"""
    block = get_answer(text, question_pattern)
    if not block:
        return []
    items = re.findall(r"^\d+\.\s+(.+)$", block, re.MULTILINE)
    return [i for i in items if i != "[ANSWER]"]

def get_checked_items(text, question_pattern):
    """Return items marked with [x] in a checkbox list."""
    pattern = rf"\*\*{re.escape(question_pattern)}\*\*.*?\n((?:- \[.\] .+\n?)+)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    checked = re.findall(r"- \[x\] (.+)", block, re.IGNORECASE)
    return checked

def get_bullet_answers(text, question_pattern):
    """Return bullet items from a block, filtering out [ANSWER] ones."""
    block = get_answer(text, question_pattern)
    if not block:
        return []
    items = re.findall(r"^[-*]\s+(.+)$", block, re.MULTILINE)
    return [i for i in items if "[ANSWER]" not in i]

def val(answer, fallback="[To be completed]"):
    return answer if answer else fallback

def section_header(title, source):
    return f"# {title}\n\n> Auto-generated from _onboarding-questionnaire.md — {TODAY}\n> Source section: {source}\n\n"

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✓ Written: {os.path.basename(path)}")

def skip(reason):
    print(f"  ⟳ Skipped: {reason}")

# ---------------------------------------------------------------------------
# Parse questionnaire
# ---------------------------------------------------------------------------

def parse(q):
    data = {}

    # Section 1 – Business Overview
    data["business_name"]    = get_answer(q, "1.1 Business name (exact)")
    data["website_url"]      = get_answer(q, "1.2 Website URL")
    data["one_liner"]        = get_answer(q, "1.3 One-sentence description of what you do")
    data["locations"]        = get_answer(q, "1.4 Where do you operate? (Cities / Regions / Countries)")
    data["content_goal"]     = get_checked_items(q, "1.5 Primary goal of website content") or \
                               [get_answer(q, "1.5 Primary goal of website content")]
    data["primary_customer"] = get_answer(q, "1.6 Who is your primary customer? (Age, job, life situation)")
    data["sales_cycle"]      = get_checked_items(q, "1.7 What is your typical sales cycle?")

    # Section 2 – Target Audience
    data["age_range"]        = get_answer(q, "2.1 Primary audience demographics")
    data["pain_point"]       = get_answer(q, "2.2 Audience's #1 pain point your business solves")
    data["tried_before"]     = get_answer(q, "2.3 What have they tried before coming to you? (And why didn't it work?)")
    data["fears"]            = get_answer(q, "2.4 What does your audience fear or worry about?")
    data["win"]              = get_answer(q, "2.5 What does a \"win\" look like for your customer?")
    data["customer_words"]   = get_answer(q, "2.6 Words your best customers use to describe your service (3–5)")

    # Section 3 – Brand Voice
    data["tone"]             = get_checked_items(q, "3.1 Brand tone (mark all that apply)")
    data["adjectives"]       = get_answer(q, "3.2 Three adjectives that describe your brand personality")
    data["tagline"]          = get_answer(q, "3.3 Primary promise or tagline")
    data["pillars"]          = get_numbered_answers(q, "3.4 Three core messaging pillars")
    data["never_say"]        = get_answer(q, "3.5 Words / phrases that should NEVER appear in your content")
    data["always_say"]       = get_answer(q, "3.6 Words / phrases that should ALWAYS appear in your content")
    data["ideal_customer"]   = get_answer(q, "3.7 Describe your ideal customer in a short paragraph")

    # Section 4 – Products & Services
    data["products_raw"]     = get_answer(q, "4.1 Main products / services")
    data["flagship"]         = get_answer(q, "4.2 Flagship / most important offering")
    data["benefits"]         = get_numbered_answers(q, "4.3 Top 3–5 customer benefits (outcomes, not features)")
    data["differentiators"]  = get_answer(q, "4.4 What makes you different from everyone else?")
    data["proof"]            = get_answer(q, "4.5 Proof points (testimonials, stats, case studies, awards)")
    data["dont_do"]          = get_answer(q, "4.6 Anything you DON'T do that competitors do?")

    # Section 5 – Writing Style
    data["headline_case"]    = get_checked_items(q, "5.1 Preferred headline casing")
    data["oxford_comma"]     = get_checked_items(q, "5.2 Oxford comma?")
    data["language"]         = get_checked_items(q, "5.3 Language variant")
    data["contractions"]     = get_checked_items(q, "5.4 Use contractions?")
    data["avoid_phrases"]    = get_answer(q, "5.5 Words / phrases to always avoid")
    data["formatting_prefs"] = get_answer(q, "5.6 Formatting preferences")
    data["article_length"]   = get_checked_items(q, "5.7 Ideal article length")

    # Section 6 – Competitors
    data["competitors_raw"]  = get_answer(q, "6.1 Top 3–5 direct competitors")
    data["comp_weaknesses"]  = get_answer(q, "6.2 Their biggest weaknesses")
    data["comp_strengths"]   = get_answer(q, "6.3 What they do well that you need to match or beat")
    data["why_us"]           = get_answer(q, "6.4 #1 reason customers choose you over them")
    data["indirect_comp"]    = get_answer(q, "6.5 Indirect competitors (other ways customers solve the same problem)")
    data["comp_keywords"]    = get_answer(q, "6.6 Keywords competitors rank for that you want to own")

    # Section 7 – Website & Key Pages
    data["homepage_url"]     = get_answer(q, "7.1 Most important pages")
    data["conversion_action"]= get_answer(q, "7.2 #1 conversion action on your site")
    data["ticketing"]        = get_answer(q, "7.3 Ticketing or booking platform (include URL)")
    data["community"]        = get_answer(q, "7.4 Community or loyalty program (name + URL)")
    data["venues"]           = get_answer(q, "7.5 Venue or partner pages to link to (name + URL)")

    # Section 8 – SEO & Keywords
    data["top_keyword"]      = get_answer(q, "8.1 #1 target keyword")
    data["keyword_formula"]  = get_answer(q, "8.2 Primary keyword formula")
    data["keywords_raw"]     = get_answer(q, "8.3 Top 10–15 target keywords")
    data["service_locations"] = get_answer(q, "8.4 Cities, regions, or locations you serve")
    data["search_intent"]    = get_checked_items(q, "8.5 Primary search intent (mark all that apply)")
    data["paa_questions"]    = get_numbered_answers(q, "8.6 \"People Also Ask\" questions you want to own (up to 5)")
    data["seo_tools"]        = get_checked_items(q, "8.7 SEO / analytics tools in use (mark all that apply)")
    data["cms"]              = get_checked_items(q, "8.8 Primary CMS / website platform")

    # Section 9 – Writing Examples
    data["example1_title"]   = get_answer(q, "9.1 Example 1 — Title:")
    data["example2_title"]   = get_answer(q, "9.2 Example 2 — Title:")
    data["example3_title"]   = get_answer(q, "9.3 Example 3 — Title:")
    data["writing_admire"]   = get_answer(q, "9.5 Competitors or brands whose writing style you admire")
    data["content_formats"]  = get_checked_items(q, "9.6 Content formats that work best for your audience (mark all that apply)")

    # Extract code blocks for writing examples
    examples = re.findall(r"```\n(.*?)```", q, re.DOTALL)
    data["examples"] = [e.strip() for e in examples if e.strip() and e.strip() != "[Paste full content here]"]

    return data

# ---------------------------------------------------------------------------
# Writers — one per context file
# ---------------------------------------------------------------------------

def write_brand_voice(d):
    name = val(d["business_name"])
    tone = ", ".join(d["tone"]) if d["tone"] else "[To be completed]"
    pillars = ""
    for i, p in enumerate(d["pillars"], 1):
        pillars += f"{i}. {p}\n"
    if not pillars:
        pillars = "1. [To be completed]\n2. [To be completed]\n3. [To be completed]\n"

    content = f"""# Brand Voice — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Business overview

**Business:** {name}
**Website:** {val(d["website_url"])}
**What we do:** {val(d["one_liner"])}
**Where we operate:** {val(d["locations"])}

## Brand tone

**Overall tone:** {tone}
**Brand personality adjectives:** {val(d["adjectives"])}
**Primary promise / tagline:** {val(d["tagline"])}

## Messaging pillars

{pillars}
## Target audience

**Primary customer:** {val(d["primary_customer"])}
**#1 pain point we solve:** {val(d["pain_point"])}
**What they've tried before:** {val(d["tried_before"])}
**Their fears:** {val(d["fears"])}
**What a "win" looks like:** {val(d["win"])}
**Words they use to describe us:** {val(d["customer_words"])}

## Ideal customer profile

{val(d["ideal_customer"])}

## Language rules

**Always say:** {val(d["always_say"])}
**Never say:** {val(d["never_say"])}
"""
    write_file(CONTEXT["brand_voice"], content)


def write_features(d):
    name = val(d["business_name"])
    benefits = ""
    for i, b in enumerate(d["benefits"], 1):
        benefits += f"{i}. {b}\n"
    if not benefits:
        benefits = "1. [To be completed]\n"

    content = f"""# Features & Benefits — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## What we offer

**Flagship offering:** {val(d["flagship"])}

### Products & services

{val(d["products_raw"])}

## Core customer benefits

{benefits}
## Unique differentiators

{val(d["differentiators"])}

## Proof points

{val(d["proof"])}

## What we don't do

{val(d["dont_do"])}
"""
    write_file(CONTEXT["features"], content)


def write_style_guide(d):
    name = val(d["business_name"])
    headline_case = d["headline_case"][0] if d["headline_case"] else "[To be completed]"
    oxford = d["oxford_comma"][0] if d["oxford_comma"] else "[To be completed]"
    language = d["language"][0] if d["language"] else "[To be completed]"
    contractions = d["contractions"][0] if d["contractions"] else "[To be completed]"
    lengths = ", ".join(d["article_length"]) if d["article_length"] else "[To be completed]"

    content = f"""# Style Guide — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Grammar & mechanics

- **Headline casing:** {headline_case}
- **Oxford comma:** {oxford}
- **Language variant:** {language}
- **Contractions:** {contractions}

## Words & phrases

**Always avoid:** {val(d["avoid_phrases"])}

**Formatting preferences:** {val(d["formatting_prefs"])}

## Content length

**Target article length:** {lengths}

## Quick reference

| Rule | Setting |
|------|---------|
| Headlines | {headline_case} |
| Oxford comma | {oxford} |
| Language | {language} |
| Contractions | {contractions} |
| Ideal length | {lengths} |
"""
    write_file(CONTEXT["style_guide"], content)


def write_competitor_analysis(d):
    name = val(d["business_name"])

    content = f"""# Competitor Analysis — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Direct competitors

{val(d["competitors_raw"])}

## Competitive intelligence

**Their biggest weaknesses:**
{val(d["comp_weaknesses"])}

**What they do well (must match or beat):**
{val(d["comp_strengths"])}

**#1 reason customers choose us:**
{val(d["why_us"])}

## Indirect competitors

{val(d["indirect_comp"])}

## Keyword opportunities

Keywords competitors rank for that we want to own:
{val(d["comp_keywords"])}
"""
    write_file(CONTEXT["competitor"], content)


def write_internal_links(d):
    name = val(d["business_name"])

    content = f"""# Internal Links Map — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Key pages

{val(d["homepage_url"])}

## Primary conversion action

{val(d["conversion_action"])}

## Ticketing / booking platform

{val(d["ticketing"])}

## Community / loyalty program

{val(d["community"])}

## Venue & partner pages

{val(d["venues"])}

---

*Always link to the primary conversion action (ticket purchase / booking) in every article.*
"""
    write_file(CONTEXT["internal_links"], content)


def write_target_keywords(d):
    name = val(d["business_name"])
    intent = ", ".join(d["search_intent"]) if d["search_intent"] else "[To be completed]"
    paa = ""
    for i, q in enumerate(d["paa_questions"], 1):
        paa += f"{i}. {q}\n"
    if not paa:
        paa = "[To be completed]\n"

    content = f"""# Target Keywords — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Primary keyword

**#1 target keyword:** {val(d["top_keyword"])}

## Keyword formula

{val(d["keyword_formula"])}

## Full keyword list

{val(d["keywords_raw"])}

## Geographic targets

{val(d["service_locations"])}

## Search intent

{intent}

## "People Also Ask" targets

{paa}
"""
    write_file(CONTEXT["target_keywords"], content)


def write_seo_guidelines(d):
    name = val(d["business_name"])
    tools = ", ".join(d["seo_tools"]) if d["seo_tools"] else "[To be completed]"
    cms = d["cms"][0] if d["cms"] else "[To be completed]"
    intent = ", ".join(d["search_intent"]) if d["search_intent"] else "[To be completed]"

    content = f"""# SEO Guidelines — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Business context

**Site:** {val(d["website_url"])}
**CMS:** {cms}
**Locations served:** {val(d["service_locations"])}

## Keyword strategy

**Primary keyword formula:** {val(d["keyword_formula"])}
**#1 target keyword:** {val(d["top_keyword"])}
**Primary search intent:** {intent}

## Analytics & tools

{tools}

## On-page rules

- Always target the primary keyword in the H1 and first 100 words
- Include location modifiers for all local pages
- Link to the primary conversion page ({val(d["conversion_action"])}) in every article
- Use the keyword formula: {val(d["keyword_formula"])}

## Content guidelines

- Language: {d["language"][0] if d["language"] else "[To be completed]"}
- Headline casing: {d["headline_case"][0] if d["headline_case"] else "[To be completed]"}
- Target article length: {", ".join(d["article_length"]) if d["article_length"] else "[To be completed]"}
"""
    write_file(CONTEXT["seo_guidelines"], content)


def write_writing_examples(d):
    name = val(d["business_name"])
    formats = "\n".join(f"- {f}" for f in d["content_formats"]) if d["content_formats"] else "[To be completed]"

    examples_section = ""
    titles = [d["example1_title"], d["example2_title"], d["example3_title"]]
    bodies = d["examples"]

    for i, (title, body) in enumerate(zip(titles, bodies), 1):
        if title and body:
            examples_section += f"## Example {i}: {title}\n\n{body}\n\n---\n\n"

    if not examples_section:
        examples_section = "*No writing examples provided yet. Add 3–5 real content samples to help SEO Machine match your voice.*\n\n"

    content = f"""# Writing Examples — {name}

> Auto-generated from _onboarding-questionnaire.md — {TODAY}

## Brands / styles we admire

{val(d["writing_admire"])}

## Best content formats for this audience

{formats}

## Content examples

{examples_section}"""
    write_file(CONTEXT["writing_examples"], content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'='*55}")
    print("  SEO Machine — Context Populator")
    print(f"{'='*55}\n")

    if not os.path.exists(QUESTIONNAIRE):
        print(f"ERROR: Questionnaire not found at:\n  {QUESTIONNAIRE}")
        sys.exit(1)

    print(f"Reading: {QUESTIONNAIRE}\n")
    q = load_questionnaire()
    d = parse(q)

    name = d["business_name"] or "Unknown client"
    print(f"Client detected: {name}\n")
    print("Writing context files...")

    # Check if business name was filled in — if not, warn
    if not d["business_name"]:
        print("\n⚠  WARNING: Business name (1.1) is still [ANSWER].")
        print("   Fill in the questionnaire before running this script.\n")
        sys.exit(1)

    write_brand_voice(d)
    write_features(d)
    write_style_guide(d)
    write_competitor_analysis(d)
    write_internal_links(d)
    write_target_keywords(d)
    write_seo_guidelines(d)
    write_writing_examples(d)

    print(f"\n{'='*55}")
    print("  All context files updated successfully.")
    print(f"  Client: {name}")
    print(f"  Date:   {TODAY}")
    print(f"{'='*55}\n")
    print("Next step: review each file in context/ and fill any")
    print("[To be completed] fields that need manual input.\n")


if __name__ == "__main__":
    main()
