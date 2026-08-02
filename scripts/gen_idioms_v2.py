#!/usr/bin/env python3
"""
Batch-generate N new Chinese idioms and append to idioms.json.
Draws candidates directly from the 30895-entry whitelist (data/idiom_whitelist.json)
and uses whitelist fields (pinyin, explanation, derivation, example) as hints for the LLM.

Usage:
  python3 gen_idioms.py <count>           # generate count new idioms
  python3 gen_idioms.py <count> --push    # also regenerate site + git push
"""
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

BASE = Path("/Users/zhangyunyi/projects/idiom-dict")
IDIOMS_FILE = BASE / "idioms" / "idioms.json"
WHITELIST_FILE = BASE / "data" / "idiom_whitelist.json"


def load_existing():
    if not IDIOMS_FILE.exists():
        return [], set()
    with open(IDIOMS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = {item["chinese"] for item in data}
    return data, existing


def load_whitelist():
    if not WHITELIST_FILE.exists():
        raise SystemExit(f"Whitelist missing: {WHITELIST_FILE}")
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def build_detail_prompt(chinese, pinyin, explanation, derivation, example):
    """Build a prompt for the LLM to generate full English-oriented idiom details.
    Uses the whitelist Chinese explanation/derivation as authoritative context."""
    return f"""You are generating a dictionary entry for the classical Chinese idiom (成语) "{chinese}" (pinyin: {pinyin}).

Authoritative Chinese context:
- 释义: {explanation}
- 出处: {derivation}
- 例句: {example}

Output strict JSON only (no markdown, no commentary), with exactly these fields:
{{
  "chinese": "{chinese}",
  "pinyin": "{pinyin}",
  "literal": "<English literal word-by-word translation, comma separated>",
  "meaning": "<2-3 sentence English explanation>",
  "origin": "<3-5 sentence English summary of the origin story, naming dynasties/figures if known>",
  "example_zh": "<one natural Chinese example sentence that USES this idiom>",
  "example_en": "<natural English translation of that example>",
  "category": "<one of: Action, Attitude, Communication, Condition, Determination, Emotion, Knowledge, Leadership, Learning, Logic, Method, Morality, Perseverance, Philosophy, Power, Quality, Recovery, Success, Wisdom, Status, Skill, Variety, Distance, Clarity, Lifestyle>",
  "similar": ["<2-3 similar Chinese idioms, characters only>"],
  "opposite": ["<1-2 opposite Chinese idioms, characters only>"]
}}

Rules:
- example_zh MUST contain the idiom "{chinese}" verbatim
- example_zh must be a single natural sentence (10-40 chars), no English, no Chinglish
- Do NOT mix this idiom with other idioms (no 杂糅)
- Output the JSON only, nothing else."""


def parse_llm_json(text):
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        return None
    return json.loads(text[first:last+1])


def slugify_pinyin(pinyin):
    import unicodedata
    normalized = unicodedata.normalize("NFKD", pinyin)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_only.lower().replace(" ", "-")


def gen_idiom(chinese, pinyin, explanation, derivation, example):
    prompt = build_detail_prompt(chinese, pinyin, explanation, derivation, example)
    try:
        result = subprocess.run(
            ["hermes", "--yolo", "-z", prompt],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0:
            print(f"  hermes ask failed: {result.stderr[:200]}")
            return None
        text = result.stdout
    except Exception as e:
        print(f"  LLM call error: {e}")
        return None

    try:
        data = parse_llm_json(text)
    except Exception as e:
        print(f"  JSON parse error: {e}")
        return None

    if not data or "chinese" not in data:
        return None

    # Quality checks
    if data.get("chinese") != chinese:
        print(f"  WARN: chinese mismatch, expected {chinese}, got {data.get('chinese')}")
        data["chinese"] = chinese
    if data.get("pinyin") != pinyin:
        data["pinyin"] = pinyin  # Trust whitelist pinyin
    ez = data.get("example_zh", "")
    if chinese not in ez:
        print(f"  WARN: example_zh doesn't contain the idiom, regenerating...")
        return None
    # Reject English chars in example_zh
    import re
    if re.search(r"[a-zA-Z]", ez):
        print(f"  WARN: example_zh has English chars, rejecting: {ez[:60]}")
        return None

    data["id"] = slugify_pinyin(data.get("pinyin", pinyin))
    return data


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    do_push = "--push" in sys.argv

    existing_data, existing_set = load_existing()
    print(f"Existing: {len(existing_data)} idioms")

    whitelist = load_whitelist()
    print(f"Whitelist: {len(whitelist)} total")

    # Pick candidates: in whitelist, not yet generated, 4-char chinese (skip longer/shorter)
    import re
    candidates = [
        x for x in whitelist
        if x.get("word", "") not in existing_set
        and len(re.sub(r"[^\u4e00-\u9fff]", "", x.get("word", ""))) == 4
        and x.get("pinyin")
    ]
    print(f"Candidates available: {len(candidates)} (4-char, not yet generated)")

    random.shuffle(candidates)
    selected = candidates[:count]
    print(f"Generating {len(selected)} new idioms...\n")

    new_entries = []
    failed = []
    for i, item in enumerate(selected, 1):
        chinese = item["word"]
        pinyin = item.get("pinyin", "")
        explanation = item.get("explanation", "")[:200]
        derivation = item.get("derivation", "")[:200]
        example = item.get("example", "")[:200]
        print(f"[{i}/{len(selected)}] -> {chinese} ({pinyin})")
        entry = gen_idiom(chinese, pinyin, explanation, derivation, example)
        if entry:
            new_entries.append(entry)
            print(f"    OK: literal='{entry.get('literal','')[:50]}...'")
        else:
            failed.append(chinese)
            print(f"    FAIL")

    if not new_entries:
        print("\nNo new idioms generated. Exiting.")
        return 1

    combined = existing_data + new_entries
    with open(IDIOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {len(new_entries)} idioms. Total: {len(combined)}")
    if failed:
        print(f"Failed: {len(failed)} ({', '.join(failed[:5])}...)")

    if do_push:
        print("\nRegenerating site...")
        r = subprocess.run(["python3", "scripts/generate.py"], cwd=BASE, capture_output=True, text=True)
        print(r.stdout[-200:] if r.stdout else "")
        if r.returncode != 0:
            print(f"generate.py failed: {r.stderr[-300:]}")
        else:
            print("Site regenerated. Push via auto_push.py or daily_cron.sh")

    return 0


if __name__ == "__main__":
    sys.exit(main())
