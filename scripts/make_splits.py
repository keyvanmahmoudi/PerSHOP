"""Build the official PerSHOP release from the original spreadsheets.

Usage:
    python scripts/make_splits.py --dialogues PerSHOP.xlsx --products Products_DataBASE.xlsx --out .

Outputs (relative to --out):
    data/dialogues/{train,validation,test}.jsonl   one row per utterance
    data/products/products.jsonl                   product database (750 items)
    data/products/slots.jsonl                      slot names and descriptions
    splits/{train,validation,test}_dialogue_ids.txt
    splits/split_stats.json

Splitting protocol
------------------
* The unit of splitting is the dialogue: all utterances of a dialogue go to the
  same split, so no dialogue context leaks between train and evaluation data.
* Ratio 80/10/10, stratified by each dialogue's primary domain (its most
  frequent non-"Chats" domain), so every product domain appears in all splits
  wherever it has enough dialogues.
* Fixed seed (42). Re-running this script on the same input reproduces the
  same split exactly.

Corrections
-----------
The documented corrections in scripts/corrections.json are applied to the
original annotations: 13 markup-syntax fixes, removal of 2 empty utterances,
and renaming the slot "super-product" to "super_product". Each fix is checked
against the original text, so the script fails if the input has changed.
`raw_text` is kept verbatim. `text` and `entities` are derived from the
corrected `annotated_text` by parsing the inline markup "[span](slot)".
"""

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

import pandas as pd

SEED = 42
RATIOS = {"train": 0.8, "validation": 0.1, "test": 0.1}

DOMAIN_EN = {
    "Chats": "chit-chat",
    "لبنیات": "dairy",
    "نوشیدنی": "beverages",
    "خوار و بار": "groceries",
    "خانه و سبک زندگی": "home and lifestyle",
    "پروتئین": "protein",
    "کودک": "baby and child",
    "کنسروجات": "canned food",
    "آرایشی و بهداشتی": "cosmetics and personal care",
    "خشکبار، دسر و شیرینی": "nuts, desserts and sweets",
    "میوه و سبزیجات": "fruits and vegetables",
    "مد و پوشاک": "fashion and clothing",
    "دستمال و شوینده": "tissues and detergents",
    "دیجیتال": "digital",
    "خودرو، موتور، دوچرخه": "car, motorcycle and bicycle",
}

MARKUP = re.compile(r"\[([^\[\]]+?)\]\(([^()]+?)\)")


def clean(value):
    """Convert pandas missing values to None and strip strings."""
    if pd.isna(value):
        return None
    return str(value).strip() if isinstance(value, str) else value


def parse_markup(annotated):
    """Return plain text and entity spans (character offsets on the plain text)."""
    if annotated is None:
        return None, []
    text_parts, entities, cursor, out_len = [], [], 0, 0
    for match in MARKUP.finditer(annotated):
        before = annotated[cursor:match.start()]
        text_parts.append(before)
        out_len += len(before)
        span, slot = match.group(1), match.group(2).strip()
        entities.append({"value": span, "slot": slot, "start": out_len, "end": out_len + len(span)})
        text_parts.append(span)
        out_len += len(span)
        cursor = match.end()
    text_parts.append(annotated[cursor:])
    return "".join(text_parts), entities


def apply_corrections(df, corrections_path):
    """Apply the documented corrections, checking each against the original text."""
    corrections = json.loads(corrections_path.read_text(encoding="utf-8"))
    df = df.copy()
    for fix in corrections["markup_fixes"]:
        mask = df.id == fix["utterance_id"]
        original = df.loc[mask, "user_text"].iloc[0]
        if original.count(fix["before"]) != 1:
            raise ValueError(f"Correction does not match utterance {fix['utterance_id']}")
        df.loc[mask, "user_text"] = original.replace(fix["before"], fix["after"])
    removed = [r["utterance_id"] for r in corrections["removed_utterances"]]
    if not df.loc[df.id.isin(removed), "user_text"].isna().all():
        raise ValueError("An utterance listed for removal is not empty")
    df = df[~df.id.isin(removed)]
    for old, new in corrections["renamed_slots"].items():
        df["user_text"] = df.user_text.str.replace(f"]({old})", f"]({new})", regex=False)
    return df


def split_dialogues(primary_domain):
    """Stratified dialogue-level split with a fixed seed."""
    rng = random.Random(SEED)
    assignment = {}
    for domain in sorted(primary_domain.unique()):
        ids = sorted(primary_domain[primary_domain == domain].index.tolist())
        rng.shuffle(ids)
        n = len(ids)
        n_val = round(n * RATIOS["validation"])
        n_test = round(n * RATIOS["test"])
        for i, dialogue_id in enumerate(ids):
            if i < n_test:
                assignment[dialogue_id] = "test"
            elif i < n_test + n_val:
                assignment[dialogue_id] = "validation"
            else:
                assignment[dialogue_id] = "train"
    return assignment


def build_rows(df):
    rows = []
    df = df.sort_values(["dialogue_number", "id"])
    for dialogue_id, group in df.groupby("dialogue_number", sort=True):
        for turn_index, record in enumerate(group.itertuples(index=False)):
            annotated = clean(record.user_text)
            text, entities = parse_markup(annotated)
            domain = clean(record.domain)
            rows.append({
                "utterance_id": int(record.id),
                "dialogue_id": int(dialogue_id),
                "turn_index": turn_index,
                "speaker": clean(record.Speecher).lower(),
                "domain": domain,
                "domain_en": DOMAIN_EN.get(domain, domain),
                "intent": clean(record.intent),
                "super_product": clean(record.SuperProduct),
                "text": text,
                "annotated_text": annotated,
                "raw_text": clean(record.RawText),
                "entities": entities,
            })
    return rows


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialogues", required=True)
    parser.add_argument("--products", required=True)
    parser.add_argument("--out", default=".")
    args = parser.parse_args()
    out = Path(args.out)

    df = pd.read_excel(args.dialogues, sheet_name="Chats").rename(columns={"Intents & Actions": "intent"})
    df = apply_corrections(df, Path(__file__).with_name("corrections.json"))

    product_turns = df[df.domain != "Chats"]
    primary = product_turns.groupby("dialogue_number").domain.agg(lambda s: s.value_counts().index[0])
    primary = primary.reindex(sorted(df.dialogue_number.unique())).fillna("Chats")
    assignment = split_dialogues(primary)

    rows = build_rows(df)
    stats = {"seed": SEED, "ratios": RATIOS, "splits": {}}
    for split in RATIOS:
        split_rows = [r for r in rows if assignment[r["dialogue_id"]] == split]
        write_jsonl(out / "data" / "dialogues" / f"{split}.jsonl", split_rows)
        dialogue_ids = sorted({r["dialogue_id"] for r in split_rows})
        ids_path = out / "splits" / f"{split}_dialogue_ids.txt"
        ids_path.parent.mkdir(parents=True, exist_ok=True)
        ids_path.write_text("\n".join(map(str, dialogue_ids)) + "\n", encoding="utf-8")
        stats["splits"][split] = {
            "dialogues": len(dialogue_ids),
            "utterances": len(split_rows),
            "primary_domain_dialogues": dict(Counter(DOMAIN_EN[primary[i]] for i in dialogue_ids).most_common()),
        }

    products = pd.read_excel(args.products, sheet_name="woz_product")
    product_records = [
        {col.replace("-", "_"): clean(val) for col, val in rec.items() if clean(val) is not None}
        for rec in products.to_dict(orient="records")
    ]
    for rec in product_records:
        rec["domain_en"] = DOMAIN_EN.get(rec.get("domain"), rec.get("domain"))
    write_jsonl(out / "data" / "products" / "products.jsonl", product_records)

    slots = pd.read_excel(args.products, sheet_name="Slots")
    write_jsonl(out / "data" / "products" / "slots.jsonl",
                [{"slot": clean(s), "description": clean(d)} for s, d in zip(slots.iloc[:, 0], slots.iloc[:, 1])])

    stats["products"] = len(product_records)
    (out / "splits" / "split_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
