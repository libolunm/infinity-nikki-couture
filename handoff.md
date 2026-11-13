# 把这段贴给你的 agent

> 下面整块是一个可直接塞进 system prompt / 工具描述 / 首次消息的说明。
> 它不依赖本机环境，任何能发 HTTP 请求的 agent 都能用。

---

你可以查一个《无限暖暖》服装提示词库，104 套高定，每套预编译好 MOSS-Image 和 Krea2 两套提示词。

入口：`https://libolunm.github.io/infinity-nikki-couture/`
镜像（国内更快，路径一样）：`https://cdn.jsdelivr.net/gh/libolunm/infinity-nikki-couture@main/`

先读手册，里面写了取数策略和字段陷阱：`GET /agent.md`

取数规矩，别违反：

1. 先 `GET /data/index.json`（65 KB，104 条纯元数据：slug、中英名、星级、风格、标签、材质、色板、分片路径）。
2. 选定后再 `GET /data/outfits/{slug}.json`（10 KB 一份，含全部四种提示词）。
3. 不要拉 `/data/moss_wardrobe_full_15mp.json`（1 MB），除非用户真的要全部 104 套。

字段：

- `original_moss_json` — MOSS 提示词，随机新少女形象
- `sonnet_moss_json` — MOSS 提示词，固定同一角色，方便横向对比
- `krea2_wardrobe_prose` — Krea2 服装段，拼进用户自己的场景
- `krea2_full_prompt` — Krea2 整条，机位 + 人物 + 服装 + 光照，可直接用
- `outfit_card` — 纯服装结构卡，给 NAI / SD / Flux 等其它模型自己转提示词

两个 `*_moss_json` 是**字符串形式的 JSON**，已经序列化好了，原样传给模型，不要解析再重组。

筛选用 `labels`（稳定英文枚举：Linlang / Royal / Fairy / Divine / Ballroom / Whimsy…），中文关键词同时匹配 `labels_zh` 和 `cn_name`。`style` 只有 Cool / Elegant / Fresh / Sexy / Sweet。

例：找琳琅风五星，取第一条的 Krea2 整条提示词

```bash
curl -s https://libolunm.github.io/infinity-nikki-couture/data/index.json \
  | jq -r '.outfits[] | select(.rarity==5 and (.labels|index("Linlang"))) | .slug' | head -1 \
  | xargs -I{} curl -s https://libolunm.github.io/infinity-nikki-couture/data/outfits/{}.json \
  | jq -r '.krea2_full_prompt'
```

服装设计版权归叠纸游戏，提示词文本可自由取用改写。

---

## 本机 agent 的省事版

如果你是在本机跑，不想让它走网络，直接把这两行写进它的上下文：

```
本地路径：D:\deepseekharness\预设与酒馆\datasets\infinity-nikki\
取数先读 curated_manifest.json 或 moss_wardrobe_full_15mp.json，
按 slug 匹配，不要整份读进上下文。
```
