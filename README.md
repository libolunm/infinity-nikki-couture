# Infinity Nikki · Couture Prompt Library

**无限暖暖 · 高定服设提示词库** — 104 套独立高定（含全服 100% 39 套五星）的结构化拆解，同时输出两套可直接喂给开源生图模型的提示词：**MOSS-Image** 嵌套框 JSON 与 **Krea2** 物理散文。

> 这是「服装设定 + 提示词」资料库，不是游戏素材包。所有图片仅作服装结构参考。

**在线浏览**：<https://libolunm.github.io/infinity-nikki-couture/>

> **给 agent 的话**：别看 `index.html`，看 [`llms.txt`](llms.txt) 和 [`agent.md`](agent.md)。
> 取数先读 `data/index.json`（63 KB，纯元数据）再按 slug 取 `data/outfits/{slug}.json`（9 KB 一份），
> 不要整包拉 `data/moss_wardrobe_full_15mp.json`（1 MB）。

---

## 这是什么

把游戏内衣柜截图变成机器可读的服装设计档案：廓形、头饰、上衣与袖型、下身与裙撑、鞋袜、配饰母题、材质、色板，然后按两套模型各自的提示词范式重新编译。

| 引擎 | 输出字段 | 格式 |
| --- | --- | --- |
| MOSS-Image（1.5MP 画布） | `original_moss_json` / `sonnet_moss_json` | 嵌套框 JSON（`summary.meta` + root caption + 分层 bbox，`abs_centralized` / `yxyx`） |
| Krea2 | `krea2_wardrobe_prose` / `krea2_full_prompt` | 自然语言散文（机位前置 + 分层受力 + 材质后果 + 收尾光与调色板） |
| 任意 LLM / NAI / SD | `outfit_card` | 纯文本服装结构卡（英文域字段 + 中文美学标签） |

浏览器打开 `index.html` 即可检索 104 套、实时筛选、一键复制三种提示词。

---

## 目录

```
llms.txt                          机器入口（llms.txt 规范：这是什么、有哪些文件、从哪开始）
agent.md                          agent 手册：取数策略、字段含义、四种引擎对应关系、jq 示例
index.html                        离线检索画廊（可中英文搜材质 / 流派，一键复制）
images/{{style}}/{{slug}}/*.webp   服装展示图（1100px webp，卡片用）
data/
  index.json                      104 条纯元数据索引（63 KB，先读这个再按需取）
  outfits/{{slug}}.json            单套全量记录（9 KB / 份，按需取最省 token）
  prompts.json                    104 套 × 4 种提示词的扁平数组（800 KB，批量才用）
  sample.json                     8 套五星起步包（62 KB）
  moss_wardrobe_full_15mp.json    主力库：104 套 × 4 种提示词形态（1 MB）
  outfit_cards.json               104 套纯服装结构卡（无角色、无 UI）
  curated_manifest.json           精选图集清单（含原站元数据与本地图片映射）
  outfits_index.json              全服 781 套结构化索引（281 套独立原版）
  moss_prompts_pack1.json         6 条手工深雕 MOSS 试装样板
  moss_prompts_pack2_linlang_crystal.json  7 条手工深雕（琳琅 / 晶纱珠绣向）
```

---

## 怎么用

### 0. 让 agent 自己取（推荐）

```bash
BASE=https://libolunm.github.io/infinity-nikki-couture

# 一步：筛出琳琅五星，取第一条的完整记录
curl -s $BASE/data/index.json \
  | jq -r '.outfits[] | select(.rarity==5 and (.labels|index("Linlang"))) | .slug' | head -1 \
  | xargs -I{} curl -s $BASE/data/outfits/{}.json \
  | jq -r '.krea2_full_prompt'
```

镜像（国内更快，路径完全一样）：`https://cdn.jsdelivr.net/gh/libolunm/infinity-nikki-couture@main/`

详细的取数策略、token 预算、字段陷阱见 [`agent.md`](agent.md)。

### 1. 直接取一条提示词

打开 `index.html` → 搜名字或材质（如 `velvet`、`琳琅`、`crystal`）→ 按引擎点复制按钮。

- **MOSS · 原创少女**：自定义发色瞳色的 1024×1536 试装版，适合新角色穿这套衣服。
- **MOSS · Sonnet 试装**：固定一个角色形象反复换装，方便横向对比。
- **Krea2 · 物理服设段**：只有服装那一段，可拼进自己的完整构图提示词。
- **Krea2 · 整条**：机位 + 人物 + 服装 + 光照全给齐，直接跑。

### 2. 从 JSON 取

```python
import json
rows = json.load(open("data/moss_wardrobe_full_15mp.json", encoding="utf-8"))
pick = [r for r in rows if r["rarity"] == 5 and "Linlang" in (r["labels"] or [])]
print(len(pick), pick[0]["cn_name"])
print(pick[0]["krea2_full_prompt"])
```

### 3. 按条件抽

```bash
# MOSS 引擎、Sonnet 试装版、琳琅流派、随机 4 条
python tools/pick_nikki_outfit.py --engine moss --mode sonnet --tag Linlang --n 4

# Krea2、只要五星、随机 6 条
python tools/pick_nikki_outfit.py --engine krea2 --rarity 5 --n 6

# 按名字查
python tools/pick_nikki_outfit.py --search "花漾梦萦"
```

### 4. MOSS-Image 的踩坑提醒

- 画布 `1024×1536`（1.5MP），边长 16 的倍数；嵌套 bbox 用 `abs_centralized` + `yxyx`。
- 少步蒸馏档（8 步 DMD LoRA）必须 `cfg = 1`，否则糊。
- 质量档：`euler` / `sgm_uniform` / step ≥ 50 / `cfg 3.0` / `shift 5.0` / SLG single_layers 22。
- JSON 里已剔除会污染服装的负面元素（蘑菇、森林、紧身衣等），如需别的风格自己改 `meta` 与光照段。

### 5. Krea2 的写作纪律

- 第一句只写机位与视觉重量，不写人物。
- 服装分层写：内裙 / 外披 / 配饰，每层挂一个「相机能拍到的物理后果」（`slipped down to leave bare` / `cinched at the waist seam before releasing into folds`）。
- 皮肤写光学（`specular pools`），眼睛写形状 + 纹理 + 高光形态，不写「红眼」了事。
- 长度 180–350 词，超长会稀释注意力，主体计数和精确裸露这类高空间精度信息首先崩。
- 收尾固定式：`[风格] anime illustration with [线稿/阴影] + [palette: 主色 held together by 次色 + single accent]`。

---

## 字段字典（`moss_wardrobe_full_15mp.json`）

| 字段 | 含义 |
| --- | --- |
| `slug` / `title` / `cn_name` | 英文标识 / 英文名 / 中文名 |
| `rarity` | 星级（5 = 五星高定） |
| `style` / `labels` | 风格大类 / 细分流派（Linlang、Royal、Fairy、Pastoral…） |
| `local_sprite` / `local_wardrobe` | 服装展示图相对路径 |
| `outfit_card` | 纯服装结构卡：`silhouette`、`headpiece_and_hair_ornaments`、`upper_garment_and_sleeves`、`lower_garment_and_legwear`、`signature_props_and_motifs`、`color_palette`、`key_materials`、`aesthetic_tag_zh` |
| `original_moss_json` | MOSS 提示词（24 种不重样少女形象） |
| `sonnet_moss_json` | MOSS 提示词（固定试装角色，便于同角色横向对比） |
| `krea2_wardrobe_prose` | Krea2 服装段散文 |
| `krea2_full_prompt` | Krea2 整条提示词（机位 + 人物 + 服装 + 光照） |

---

## 收录范围

- 本地图集 104 套：**全服 39 套五星 100% 收录** + 65 套高颜值四星（优先琳琅中式、仙子晶翼、神圣珠绣、舞会礼服方向）。
- `outfits_index.json` 另含全服 781 套结构化索引（281 套独立原版 + 进化态）。
- 服装结构卡由视觉语言模型从游戏内衣柜截图蒸馏，不含角色本体、不含 UI。个别套装配图只有立绘/精灵图，`local_wardrobe` 为空是正常的。

---

## 加载与镜像

- `index.html` 是单文件应用，全部 104 套数据内联，gzip 后约 110 KB。
- 缩略图同时存在两处：仓库内 `images/**.webp`，以及 Cloudflare 图床镜像（`images_urls.json` 记录了映射）。页面优先走图床（国内访问更快），图床失败时自动回落到仓库内相对路径，所以整个仓库离线 clone 下来也能直接看。
- 想换自己的图床：改 `tools/build_nikki_share.py` 里的 `CDN_BASE`，或用 `tools/upload_share_images.mjs` 重新上传生成本地 `images_urls.json` 后重建。

---

## 版权

《无限暖暖》及其全部服装设计、角色形象、美术素材版权归 **叠纸游戏 / Infold Games** 所有。本仓库只提供**文本层**的服装结构描述与提示词编译结果，图片仅作服装结构对照，供个人学习与二次创作参考，**不得商用、不得用于训练商业模型、不得冒充官方物料**。若权利人要求，将立即移除图片资源。

提示词文本部分可自由取用、改写、二次分发。
