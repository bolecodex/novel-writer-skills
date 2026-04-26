# novel-writer-skills

基于 AI Agent 的网文小说创作技能包。支持脑洞生成、黄金三章、10章短篇、长篇续写、审稿润色五种创作模式，并内置 `novel-cli` 确定性校验工具。

## 一键安装

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/bolecodex/novel-writer-skills/main/scripts/setup.sh)
```

安装完成后，`novel-cli` 会被安装到 Python 环境，技能会通过 Skills CLI 写入 ArkClaw/OpenClaw/Cursor 等 Agent 的技能目录。

## 火山 ArkClaw 安装

在 ArkClaw 的终端环境中运行：

```bash
# 推荐：一键安装 CLI + Skill
bash <(curl -fsSL https://raw.githubusercontent.com/bolecodex/novel-writer-skills/main/scripts/setup.sh)

# 或分步安装
python3 -m pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"
npx skills add bolecodex/novel-writer-skills@web-novel-writer -g -y
```

安装后检查：

```bash
novel-cli --version
novel-cli --help
```

## 国内安装（Gitee 镜像）

如果 ArkClaw 环境访问 GitHub 超时，使用 Gitee 镜像：

```bash
bash <(curl -fsSL https://gitee.com/bolecodex/novel-writer-skills/raw/main/scripts/setup-gitee.sh)
```

也可以分步安装：

```bash
python3 -m pip install "novel-cli @ git+https://gitee.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli" -i https://pypi.tuna.tsinghua.edu.cn/simple
npx skills add https://gitee.com/bolecodex/novel-writer-skills.git@web-novel-writer -y -g
```

如果当前 Skills CLI 不支持 `repo@skill` 精确安装，改用整个仓库安装：

```bash
npx skills add https://gitee.com/bolecodex/novel-writer-skills.git -y -g
```

也可以写成一行：

```bash
python3 -m pip install "novel-cli @ git+https://gitee.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli" -i https://pypi.tuna.tsinghua.edu.cn/simple && npx skills add https://gitee.com/bolecodex/novel-writer-skills.git@web-novel-writer -y -g
```

安装后重启/刷新 ArkClaw，并检查：

```bash
novel-cli --version
novel-cli validate --help
```

## 安装 novel-cli

skills 依赖 `novel-cli` 命令行工具，安装方式：

```bash
# 方式一：直接从 GitHub 安装（推荐）
python3 -m pip install "novel-cli @ git+https://github.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli"

# 国内环境：从 Gitee 镜像安装
python3 -m pip install "novel-cli @ git+https://gitee.com/bolecodex/novel-writer-skills.git#subdirectory=novel-cli" -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方式二：克隆后本地安装
git clone https://github.com/bolecodex/novel-writer-skills.git
cd novel-writer-skills/novel-cli
python3 -m pip install .
```

## 安装技能

```bash
npx skills add bolecodex/novel-writer-skills@web-novel-writer -y -g

# 国内环境：从 Gitee 镜像安装
npx skills add https://gitee.com/bolecodex/novel-writer-skills.git@web-novel-writer -y -g
```

安装后技能会被 symlink 到对应 Agent 的 skills 目录（如 ArkClaw/OpenClaw/Cursor 的技能目录）。如果当前 Skills CLI 不支持 `repo@skill` 精确安装，也可以安装整个仓库：

```bash
npx skills add bolecodex/novel-writer-skills -y -g
npx skills add https://gitee.com/bolecodex/novel-writer-skills.git -y -g
```

## 项目结构

```
novel-writer-skills/
├── skills/
│   └── web-novel-writer/       # 技能定义（npx skills add 自动发现）
│       ├── SKILL.md            # 技能入口
│       ├── phases/             # 五个创作阶段指令
│       │   ├── brainstorm.md
│       │   ├── golden-three.md
│       │   ├── short-novel.md
│       │   ├── long-serial.md
│       │   └── review.md
│       └── references/         # 写作参考资料
│           ├── formulas.md
│           ├── writing-rules.md
│           ├── emotion-model.md
│           └── villain-dialogue-examples.md
├── novel-cli/                  # Python CLI 工具（pip install）
│   ├── pyproject.toml
│   ├── tests/
│   └── novel_cli/
│       ├── __init__.py
│       └── cli.py
├── scripts/
│   ├── setup.sh                # GitHub 一键安装脚本
│   └── setup-gitee.sh          # Gitee 一键安装脚本
└── README.md
```

## CLI 用法

```bash
novel-cli count <file>      # 章节字数与对话占比
novel-cli scan <file>       # 禁用词/AI味/机械断句检测
novel-cli outline <file>    # 提取章节大纲
novel-cli validate <file>   # 综合校验（字数+禁词+格式）
novel-cli summary <file>    # 每章摘要+角色出场统计
```

## 创作模式

| 模式 | 说明 | 输出 |
|------|------|------|
| 脑洞生成 | 从灵感火花生成3个高概念故事方案 | 3个完整方案 |
| 黄金三章 | 写出决定读者去留的前3章 | 每章2200-2600字 |
| 10章短篇 | 完整10章短篇小说 | 总计9000-12000字 |
| 长篇续写 | 将短篇扩展为长篇网文/短剧底稿 | 默认200章/100集 |
| 审稿润色 | 对已有稿件打分、点评、润色 | 评审报告+润色稿 |

## License

MIT
