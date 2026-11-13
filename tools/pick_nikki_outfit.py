"""
Quick CLI Picker for Infinity Nikki Wardrobe Library (104 Haute-Couture Outfits)
Usage:
  python tools/pick_nikki_outfit.py --engine moss --mode sonnet --tag Linlang --n 4
  python tools/pick_nikki_outfit.py --engine krea2 --rarity 5 --n 6
  python tools/pick_nikki_outfit.py --search "花漾梦萦"
"""
import argparse
import json
import random
from pathlib import Path

DB_PATH = Path(r"D:\deepseekharness\预设与酒馆\datasets\infinity-nikki\moss_wardrobe_full_15mp.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["moss", "krea2", "krea2-wardrobe"], default="moss")
    ap.add_argument("--mode", choices=["sonnet", "orig"], default="orig", help="For MOSS: sonnet or diverse maiden")
    ap.add_argument("--tag", default="", help="Filter by style or label, e.g. Linlang, Elegant, Fairy, Fresh")
    ap.add_argument("--rarity", type=int, default=0, help="Filter by rarity (5 or 4)")
    ap.add_argument("--search", default="", help="Substring search in CN/EN title or material")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    items = json.loads(DB_PATH.read_text(encoding="utf-8"))
    if args.rarity:
        items = [x for x in items if x.get("rarity") == args.rarity]
    if args.tag:
        t = args.tag.lower()
        items = [
            x for x in items
            if t == (x.get("style") or "").lower() or any(t in lb.lower() for lb in (x.get("labels") or []))
        ]
    if args.search:
        q = args.search.lower()
        items = [x for x in items if q in json.dumps([x.get("cn_name"), x.get("title"), x.get("outfit_card")], ensure_ascii=False).lower()]

    if not items:
        print("No matching outfits found.")
        return

    rng = random.Random(args.seed)
    chosen = items if args.search else rng.sample(items, min(args.n, len(items)))
    for i, c in enumerate(chosen, 1):
        zh_tag = (c.get("outfit_card") or {}).get("aesthetic_tag_zh", "")
        print(f"=== [{i}] ★{c['rarity']} {c.get('cn_name') or c['title']} ({c['title']}) · {zh_tag} ===")
        if args.engine == "moss":
            print(c["sonnet_moss_json"] if args.mode == "sonnet" else c["original_moss_json"])
        elif args.engine == "krea2":
            print(c["krea2_full_prompt"])
        else:
            print(c["krea2_wardrobe_prose"])
        print()


if __name__ == "__main__":
    main()
