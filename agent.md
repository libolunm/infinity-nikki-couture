# Agent Guide — Infinity Nikki Couture Prompt Library

Read this instead of `index.html`. The HTML page is for humans who want to browse pictures;
everything below is the machine path.

Base URL: `https://libolunm.github.io/infinity-nikki-couture/`
Mirror: `https://cdn.jsdelivr.net/gh/libolunm/infinity-nikki-couture@main/` (identical paths, use when github.io is slow)

All files are static JSON served with `Access-Control-Allow-Origin: *`.

---

## 1. Pick a strategy first

| You need | Fetch | Size | Why |
| --- | --- | --- | --- |
| 1-3 specific outfits | `data/outfits/{slug}.json` | 10 KB each | Cheapest. Skip the index if you already know the slug. |
| Filter by rarity / style / tag, then fetch | `data/index.json` then shards | 65 KB + 10 KB per pick | Two-step, still cheap. |
| Everything, once | `data/prompts.json` | 800 KB | Only when you genuinely need all 104. |
| A few good defaults | `data/sample.json` | 62 KB | 8 hand-picked five-stars with full prompts. |
| Text plus images | `data/moss_wardrobe_full_15mp.json` | ~1 MB | Rarely worth it; images are metadata-only strings. |

Rule of thumb: `index.json` is 65 KB, one shard is 10 KB, the whole library is 1 MB.
Fetching the whole library to answer "give me one 琳琅 outfit" wastes about 240k tokens.

---

## 2. Record shape

`data/outfits/{slug}.json`:

```json
{
  "slug": "clouded-loong",
  "title": "Clouded Loong",
  "cn_name": "龙隐云墨间",
  "rarity": 5,
  "style": "Cool",
  "labels": ["Linlang", "Royal"],
  "aliases": ["Clouded Loong", "龙隐云墨间"],
  "outfit_card": {
    "silhouette": "...",
    "headpiece_and_hair_ornaments": "...",
    "upper_garment_and_sleeves": "...",
    "lower_garment_and_legwear": "...",
    "signature_props_and_motifs": "...",
    "color_palette": ["moonlight white", "celadon cyan"],
    "key_materials": ["crystal", "jacquard", "silk"],
    "aesthetic_tag_zh": "清冷水墨琳琅仙气"
  },
  "original_moss_json": "<JSON string, feed as-is>",
  "sonnet_moss_json": "<JSON string, feed as-is>",
  "krea2_wardrobe_prose": "<one dense paragraph>",
  "krea2_full_prompt": "<complete prompt with camera + figure + outfit + light>",
  "images": ["images/Cool/clouded-loong/sprite.png", "..."]
}
```

The two `*_moss_json` fields are **strings that happen to contain JSON** — they are
already serialised for the model. Pass them through verbatim; do not parse and re-emit.

---

## 3. Which prompt variant to hand the user

- MOSS-Image, new character each time → `original_moss_json`
- MOSS-Image, same character across outfits (comparisons, lookbooks) → `sonnet_moss_json`
- Krea2, user has their own scene/camera → `krea2_wardrobe_prose` (splice the outfit clause into their prompt)
- Krea2, user wants one sentence to paste → `krea2_full_prompt`
- Any other model (NAI, SD, Flux) → `outfit_card`, render it into tags or prose yourself

Canvas assumptions: MOSS is 1024x1536 (1.5 MP, sides divisible by 16), bboxes are
`abs_centralized` with `yxyx` order. Krea2 prompts assume no fixed canvas.

---

## 4. Worked examples

Give me one 琳琅 five-star:

```bash
curl -s https://libolunm.github.io/infinity-nikki-couture/data/index.json \
  | jq -r '.outfits[] | select(.rarity==5 and (.labels|index("Linlang"))) | .slug' \
  | head -1 \
  | xargs -I{} curl -s https://libolunm.github.io/infinity-nikki-couture/data/outfits/{}.json \
  | jq -r '.krea2_full_prompt'
```

Search by Chinese name:

```bash
curl -s https://libolunm.github.io/infinity-nikki-couture/data/index.json \
  | jq -r '.outfits[] | select(.cn_name|test("花漾")) | "\(.slug)\t\(.cn_name)\t\(.labels|join(","))"'
```

Filter by fabric:

```bash
curl -s https://libolunm.github.io/infinity-nikki-couture/data/index.json \
  | jq -r '.outfits[] | select(.materials|map(test("velvet";"i"))|any) | .slug' 
```

Three random five-stars with MOSS prompts:

```bash
curl -s https://libolunm.github.io/infinity-nikki-couture/data/prompts.json \
  | jq -r 'map(select(.rarity==5)) | .[0:3][] | .cn_name + "\n" + .moss + "\n---"'
```

---

## 5. Notes and traps

- Labels: `labels` is a stable English enum (`Linlang`, `Royal`, `Fairy`, `Pastoral`, `Ballroom`, `Divine`, `Whimsy`...). `labels_zh` carries the Chinese form of the same tags for Chinese keyword matching. Filter on `labels`; match user wording against both.
- `style` is one of `Cool` / `Elegant` / `Fresh` / `Sexy` / `Sweet`.
- Some outfits only have a sprite, so `images` may hold one entry. That is normal, not a bug.
- Prompt text is English throughout, even for Chinese-named outfits. Do not translate it before feeding an image model.
- Prompt text already excludes the usual pollution terms (mushrooms, forests, skin-tight bodysuits); do not re-add them.

---

## 6. Licence

Outfit designs, character likenesses and game art are copyright Infold Games (叠纸游戏).
This dataset ships the **text layer** — structure descriptions and prompt compilations —
for personal study and derivative creation. Images are reference only: no commercial use,
no training commercial models, no passing off as official material.
Prompt text itself is free to reuse, rewrite and redistribute.
