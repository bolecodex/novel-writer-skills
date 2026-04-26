---
name: web_novel_writer
description: >-
  创作网文小说，包括脑洞生成、黄金三章、10章短篇、长篇续写、审稿润色。当用户想写小说、
  生成故事创意、创作章节、续写长篇、或者润色审稿时使用。支持男频和女频。
metadata:
  openclaw:
    requires:
      bins: [novel-cli, python3]
  arkclaw:
    requires:
      bins: [novel-cli, python3]
---

# 网文小说创作

编排型技能，支持五种创作模式，可组合为完整流水线。

## 安装前提

本技能依赖 `novel-cli` 命令行工具，请确认已安装：

```bash
pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"
```

## 工作流程

### 第一步：确定创作模式

询问用户要执行哪种模式：

- **脑洞生成** — 从一个灵感火花生成3个高概念故事方案
- **黄金三章** — 写出决定读者去留的前3章（每章2200-2600字）
- **10章短篇** — 写一个完整的10章短篇小说（总计9000-12000字）
- **长篇续写** — 将短篇扩展为长篇网文（200章/100集短剧，20-25万字）
- **审稿润色** — 对已有稿件打分、点评、润色

同时询问题材方向（男频/女频）和具体子类型偏好。

### 第二步：加载阶段指令

读取对应的阶段文件获取详细指令：

| 模式 | 阶段文件 |
|------|---------|
| 脑洞生成 | [phases/brainstorm.md](phases/brainstorm.md) |
| 黄金三章 | [phases/golden-three.md](phases/golden-three.md) |
| 10章短篇 | [phases/short-novel.md](phases/short-novel.md) |
| 长篇续写 | [phases/long-serial.md](phases/long-serial.md) |
| 审稿润色 | [phases/review.md](phases/review.md) |

### 第三步：执行

按加载的阶段文件中的指令执行。核心原则：

1. **独立则并行**：对互不依赖的任务并行启动独立子任务（如同时生成3个脑洞方案）。
2. **依赖则串行**：需要情节连贯性的章节按顺序写。
3. **CLI 校验**：写完后运行 `novel-cli` 校验字数、禁用词和机械断句。
4. **人在回路**：将关键选择（公式选择、情节走向、角色弧线）交给用户决定。

### 第四步：流水线模式

如果用户需要完整流水线，按以下顺序串联：

1. 脑洞生成 → 用户选择一个方案
2. 黄金三章（基于选中的方案）或 10章短篇（基于用户提供的大纲）
3. 审稿润色
4. （可选）长篇续写 — 将已有短篇扩展为 200 章长篇/100 集短剧

## 参考资料

详细领域知识在 `references/` 目录中，按需加载：

- [references/formulas.md](references/formulas.md) — 脑洞公式库
- [references/writing-rules.md](references/writing-rules.md) — 写作规则与禁用词表
- [references/emotion-model.md](references/emotion-model.md) — 情绪价值量化模型
- [references/villain-dialogue-examples.md](references/villain-dialogue-examples.md) — 反派/绿茶/渣男台词参考
- [references/long-serial-arcs.md](references/long-serial-arcs.md) — 长篇卷结构模板库

## CLI 工具

全局安装的 `novel-cli` 命令提供确定性校验：

```bash
novel-cli count <file>                            # 章节字数与对话占比
novel-cli scan <file>                             # 禁用词/AI味/机械断句检测
novel-cli outline <file>                          # 提取章节大纲
novel-cli validate <file>                         # 综合校验（自动检测模式）
novel-cli validate <file> --mode long             # 长篇模式校验
novel-cli validate <file> --from 11 --to 45       # 只校验第11-45章
novel-cli summary <file>                          # 每章摘要+角色出场统计
```

每个写作阶段完成后务必运行 `novel-cli scan` 和 `novel-cli validate`，严重风格问题必须修复后再交付。

## 输出规范

- 所有小说正文必须是**纯文本**——不加粗、不用 Markdown 格式
- 正文使用自然段换行，同一自然段内多句连写；不要每句话单独换行，也不要在每句话之间插空行
- 禁止机械动作清单式断句，如连续罗列动作、流程、位移、操作或说话标签
- 章节标题格式：`【第X章 章节标题】`
- 每章结尾标注：`[本章字数：XXXX]`
