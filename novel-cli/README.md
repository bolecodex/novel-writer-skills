# novel-cli

网文小说校验工具 — Web novel validation CLI for AI-written Chinese fiction.

## Install

```bash
pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"
```

Or install from local clone:

```bash
git clone https://github.com/bolecodex/novel-writer-skills.git
cd novel-writer-skills/novel-cli
pip install .
```

## Usage

```bash
novel-cli count <file>      # 章节字数与对话占比
novel-cli scan <file>       # 禁用词/AI味检测
novel-cli outline <file>    # 提取章节大纲
novel-cli validate <file>   # 综合校验
```
