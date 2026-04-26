# novel-cli

网文小说校验工具 — Web novel validation CLI for AI-written Chinese fiction.

## Install

```bash
python3 -m pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"
```

Or install from local clone:

```bash
git clone https://github.com/bolecodex/novel-writer-skills.git
cd novel-writer-skills/novel-cli
python3 -m pip install .
```

## Usage

```bash
novel-cli count <file>      # 章节字数与对话占比
novel-cli scan <file>       # 禁用词/AI味/机械断句检测
novel-cli outline <file>    # 提取章节大纲
novel-cli validate <file>   # 综合校验
```

`scan` 会泛化识别机械动作清单式叙述，包括连续短动作链、同主语反复开头、低价值流程链和连续说话标签。
