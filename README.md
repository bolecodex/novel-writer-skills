# novel-writer-skills

基于 AI Agent 的网文小说创作技能包。支持脑洞生成、黄金三章、10章短篇、审稿润色四种创作模式。

## 一键安装

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/bolecodex/novel-writer-skills/main/scripts/setup.sh)
```

安装完成后，skills 会被写入 `~/.agents/skills/`。

## 安装 novel-cli

skills 依赖 `novel-cli` 命令行工具，安装方式：

```bash
# 方式一：直接从 GitHub 安装（推荐）
pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"

# 方式二：克隆后本地安装
git clone https://github.com/bolecodex/novel-writer-skills.git
cd novel-writer-skills/novel-cli
pip install .
```

## 安装技能

```bash
npx skills add bolecodex/novel-writer-skills -y -g
```

安装后技能会被 symlink 到对应 Agent 的 skills 目录（如 Cursor 的 `~/.cursor/skills/`、OpenClaw 的 `~/.openclaw/skills/`）。

## 项目结构

```
novel-writer-skills/
├── skills/
│   └── web-novel-writer/       # 技能定义（npx skills add 自动发现）
│       ├── SKILL.md            # 技能入口
│       ├── phases/             # 四个创作阶段指令
│       │   ├── brainstorm.md
│       │   ├── golden-three.md
│       │   ├── short-novel.md
│       │   └── review.md
│       └── references/         # 写作参考资料
│           ├── formulas.md
│           ├── writing-rules.md
│           ├── emotion-model.md
│           └── villain-dialogue-examples.md
├── novel-cli/                  # Python CLI 工具（pip install）
│   ├── pyproject.toml
│   └── novel_cli/
│       ├── __init__.py
│       └── cli.py
├── scripts/
│   └── setup.sh                # 一键安装脚本
└── README.md
```

## CLI 用法

```bash
novel-cli count <file>      # 章节字数与对话占比
novel-cli scan <file>       # 禁用词/AI味检测
novel-cli outline <file>    # 提取章节大纲
novel-cli validate <file>   # 综合校验（字数+禁词+格式）
```

## 创作模式

| 模式 | 说明 | 输出 |
|------|------|------|
| 脑洞生成 | 从灵感火花生成3个高概念故事方案 | 3个完整方案 |
| 黄金三章 | 写出决定读者去留的前3章 | 每章2200-2600字 |
| 10章短篇 | 完整10章短篇小说 | 总计9000-12000字 |
| 审稿润色 | 对已有稿件打分、点评、润色 | 评审报告+润色稿 |

## License

MIT
