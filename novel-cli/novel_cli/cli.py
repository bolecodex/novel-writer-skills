#!/usr/bin/env python3
"""Web novel validation CLI — deterministic checks for AI-written fiction."""

import json
import re
import sys
from pathlib import Path

import click

BANNED_WORDS = [
    # 眼神相关
    "眼神", "目光", "瞳孔",
    # 表情相关
    "嘴角", "勾起", "紧锁",
    # 声音相关
    "语气", "沙哑", "冰冷",
    # 比喻连词
    "仿佛", "好像", "宛如", "犹如", "如同",
    # 手部动作
    "握紧", "攥紧", "指节", "泛白", "掌心", "手心",
    # 呼吸动作
    "深吸", "吸了口气",
    # 夸张形容
    "淬了毒", "淬了冰", "不容置疑", "不容忽视", "不易察觉",
    # 过度转折
    "毋庸置疑", "显而易见",
    # 模糊量词
    "一丝", "略微", "稍许",
    # 内心独白套路
    "深知",
]

BANNED_PATTERNS = [
    re.compile(r"眼神.{0,2}(坚定|迷离|复杂)"),
    re.compile(r"嘴角.{0,2}(上扬|抽搐|勾起)"),
    re.compile(r"深吸一口气"),
    re.compile(r"握紧拳头"),
    re.compile(r"指节泛白"),
    re.compile(r"眉头紧锁"),
    re.compile(r"瞳孔一缩"),
]

CHAPTER_RE = re.compile(r"【第(\d+)章[^】]*】")
WORD_COUNT_RE = re.compile(r"\[本章字数[：:](\d+)\]")
TOTAL_COUNT_RE = re.compile(r"【总字数】[：:](\d+)字")
DIALOGUE_RE = re.compile(r'[\"\'].+?[\"\']|\u201c[^\u201d]+\u201d|\u2018[^\u2019]+\u2019')


def _read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        click.echo(f"Error: file not found: {path}", err=True)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _split_chapters(text: str) -> list[dict]:
    """Split text into chapters. Returns list of {number, title, body}."""
    parts = CHAPTER_RE.split(text)
    chapters = []
    # parts layout: [preamble, ch_num, ch_body, ch_num, ch_body, ...]
    i = 1
    while i < len(parts) - 1:
        ch_num = int(parts[i])
        ch_body = parts[i + 1].strip()
        title_match = re.match(r"\s*(.*?)】", text[text.find(f"【第{ch_num}章"):])
        title = ""
        if title_match:
            raw = text[text.find(f"【第{ch_num}章"):]
            end = raw.find("】")
            title = raw[len(f"【第{ch_num}章"):end].strip()
        chapters.append({"number": ch_num, "title": title, "body": ch_body})
        i += 2
    return chapters


def _count_chars(text: str) -> int:
    """Count meaningful characters (excluding whitespace and markup)."""
    cleaned = re.sub(r"\[本章字数[：:]\d+\]", "", text)
    cleaned = re.sub(r"【[^】]+】", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    return len(cleaned)


def _dialogue_ratio(text: str) -> float:
    """Estimate dialogue character ratio."""
    total = _count_chars(text)
    if total == 0:
        return 0.0
    dialogue_chars = sum(len(m.group()) for m in DIALOGUE_RE.finditer(text))
    return round(dialogue_chars / total, 3)


@click.group()
@click.version_option("1.1.0")
def cli():
    """novel-cli: Web novel validation toolkit."""
    pass




@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="json")
def count(file, fmt):
    """Count chapter word counts and dialogue ratio."""
    text = _read_file(file)
    chapters = _split_chapters(text)
    results = []
    for ch in chapters:
        char_count = _count_chars(ch["body"])
        ratio = _dialogue_ratio(ch["body"])
        results.append({
            "chapter": ch["number"],
            "title": ch["title"],
            "chars": char_count,
            "dialogue_ratio": ratio,
        })
    total = sum(r["chars"] for r in results)
    output = {"chapters": results, "total_chars": total, "chapter_count": len(results)}

    if fmt == "json":
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = ""
            if len(results) <= 3:  # golden-three mode
                if r["chars"] < 2090 or r["chars"] > 2730:
                    status = " *** OUT OF RANGE (target: 2200-2600±5%)"
            else:  # short-novel mode
                if r["chars"] < 950 or r["chars"] > 1260:
                    status = " *** OUT OF RANGE (target: 1000-1200±5%)"
            click.echo(
                f"Ch {r['chapter']:>2}: {r['chars']:>5} chars, "
                f"dialogue {r['dialogue_ratio']:.0%}{status}"
            )
        click.echo(f"\nTotal: {total} chars across {len(results)} chapters")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="json")
def scan(file, fmt):
    """Scan for banned words and AI-slop patterns."""
    text = _read_file(file)
    lines = text.split("\n")
    findings = []

    for line_no, line in enumerate(lines, 1):
        for word in BANNED_WORDS:
            start = 0
            while True:
                idx = line.find(word, start)
                if idx == -1:
                    break
                findings.append({
                    "line": line_no,
                    "column": idx + 1,
                    "word": word,
                    "type": "banned_word",
                    "context": line[max(0, idx - 10):idx + len(word) + 10].strip(),
                })
                start = idx + 1

        for pattern in BANNED_PATTERNS:
            for m in pattern.finditer(line):
                findings.append({
                    "line": line_no,
                    "column": m.start() + 1,
                    "word": m.group(),
                    "type": "banned_pattern",
                    "context": line[max(0, m.start() - 10):m.end() + 10].strip(),
                })

    output = {"total_issues": len(findings), "findings": findings}

    if fmt == "json":
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if not findings:
            click.echo("No banned words or patterns found.")
        else:
            click.echo(f"Found {len(findings)} issues:\n")
            for f in findings:
                click.echo(
                    f"  L{f['line']}:C{f['column']} [{f['type']}] "
                    f"\"{f['word']}\" — ...{f['context']}..."
                )


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="json")
def outline(file, fmt):
    """Extract chapter outline structure."""
    text = _read_file(file)
    chapters = _split_chapters(text)
    results = []
    for ch in chapters:
        body_lines = [l.strip() for l in ch["body"].split("\n") if l.strip()]
        first_line = body_lines[0] if body_lines else ""
        last_line = body_lines[-1] if body_lines else ""
        results.append({
            "chapter": ch["number"],
            "title": ch["title"],
            "opening": first_line[:80],
            "closing": last_line[:80],
            "chars": _count_chars(ch["body"]),
        })

    output = {"chapters": results}
    if fmt == "json":
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            click.echo(f"\n--- Ch {r['chapter']}: {r['title']} ({r['chars']} chars) ---")
            click.echo(f"  Opens: {r['opening']}")
            click.echo(f"  Closes: {r['closing']}")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["golden", "short", "long", "auto"]), default="auto",
              help="Validation mode: golden (黄金三章), short (10章短篇), long (长篇), auto-detect.")
@click.option("--from", "ch_from", type=int, default=None,
              help="Only validate chapters starting from this number (inclusive).")
@click.option("--to", "ch_to", type=int, default=None,
              help="Only validate chapters up to this number (inclusive).")
def validate(file, mode, ch_from, ch_to):
    """Run full validation: word count + banned words + format check."""
    text = _read_file(file)
    chapters = _split_chapters(text)
    errors = []
    warnings = []

    if mode == "auto":
        if len(chapters) <= 3:
            mode = "golden"
        elif len(chapters) <= 15:
            mode = "short"
        else:
            mode = "long"

    if ch_from is not None or ch_to is not None:
        lo = ch_from if ch_from is not None else 0
        hi = ch_to if ch_to is not None else 999999
        chapters = [ch for ch in chapters if lo <= ch["number"] <= hi]
        if not chapters:
            errors.append(f"No chapters found in range {lo}-{hi}")

    if mode == "golden":
        min_chars, max_chars, label = 2090, 2730, "2200-2600±5%"
        dialogue_threshold = 0.40
    else:
        min_chars, max_chars, label = 950, 1260, "1000-1200±5%"
        dialogue_threshold = 0.50

    for ch in chapters:
        cc = _count_chars(ch["body"])
        if cc < min_chars or cc > max_chars:
            errors.append(
                f"Ch {ch['number']}: {cc} chars — outside target {label}"
            )
        dr = _dialogue_ratio(ch["body"])
        if dr < dialogue_threshold:
            warnings.append(
                f"Ch {ch['number']}: dialogue ratio {dr:.0%} < {dialogue_threshold:.0%} target"
            )

    banned_count = 0
    for ch in chapters:
        for line in ch["body"].split("\n"):
            for word in BANNED_WORDS:
                banned_count += line.count(word)
            for pattern in BANNED_PATTERNS:
                banned_count += len(pattern.findall(line))
    if banned_count > 0:
        errors.append(f"Banned words/patterns found: {banned_count} instances (run 'scan' for details)")

    total = sum(_count_chars(ch["body"]) for ch in chapters)

    if mode == "short" and ch_from is None and ch_to is None:
        if total < 9000 or total > 12000:
            errors.append(f"Total chars {total} outside 9000-12000 range")

    has_chapter_counts = bool(WORD_COUNT_RE.findall(text))
    if not has_chapter_counts and chapters:
        warnings.append("Missing [本章字数：XXXX] markers")

    actual = [ch["number"] for ch in chapters]
    expected = list(range(actual[0], actual[0] + len(actual))) if actual else []
    if actual != expected:
        errors.append(f"Non-sequential chapters: got {actual}")

    result = {
        "mode": mode,
        "chapter_range": f"{actual[0]}-{actual[-1]}" if actual else None,
        "chapter_count": len(chapters),
        "total_chars": total,
        "errors": errors,
        "warnings": warnings,
        "passed": len(errors) == 0,
    }

    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="text")
def summary(file, fmt):
    """Generate per-chapter summary and character statistics."""
    text = _read_file(file)
    chapters = _split_chapters(text)

    STOP_WORDS = {
        "我", "你", "他", "她", "它", "我们", "你们", "他们", "她们",
        "这", "那", "什么", "怎么", "哪", "谁", "自己", "别人", "大家",
        "所有", "没有", "不是", "可以", "已经", "还是", "因为", "但是",
        "如果", "虽然", "然后", "不过", "为什么", "可能", "应该", "当然",
        "我没", "我不", "你不", "你少", "你别", "她又", "他又", "我站",
        "我看", "我要", "你要", "我让", "他让", "她让", "我转", "我听",
        "见他", "见她", "见我", "抬头", "出来", "进来", "过来", "过去",
        "起来", "下去", "回来", "一个", "一下", "两个", "三个",
        "听见他", "听见她", "门外", "门口", "身后", "面前", "旁边",
        "对面", "楼下", "楼上", "房间", "客厅", "走廊", "沙发",
        "她就", "他没", "她没", "你想", "我来", "他来", "她来",
        "小声", "大声", "床边", "桌上", "人去", "下去", "上去",
    }
    NAME_SUFFIX_RE = re.compile(
        r"(说|笑|问|喊|看|站|走|坐|跑|起身|拍|打|开口|关|拿|接|放|指|让|叫|听|转身|提"
        r"|拉|推|跟|进来|出去|抬|低头|退|扑|挡|伸手|挤|冲|停|摇头|点头|扔|摔|捂|甩|靠|哭|抖)"
    )

    char_counts: dict[str, int] = {}
    chapter_summaries = []

    for ch in chapters:
        body = ch["body"]
        lines = [l.strip() for l in body.split("\n") if l.strip()]

        for line in lines:
            for m in NAME_SUFFIX_RE.finditer(line):
                start = m.start()
                for length in (3, 2):
                    if start >= length:
                        candidate = line[start - length:start]
                        if (all("\u4e00" <= c <= "\u9fff" for c in candidate)
                                and candidate not in STOP_WORDS):
                            char_counts[candidate] = char_counts.get(candidate, 0) + 1

        opening = lines[0][:60] if lines else ""
        closing = lines[-1][:60] if lines else ""
        chars = _count_chars(body)

        chapter_summaries.append({
            "chapter": ch["number"],
            "title": ch["title"],
            "chars": chars,
            "opening": opening,
            "closing": closing,
        })

    top_characters = sorted(char_counts.items(), key=lambda x: -x[1])[:20]

    if fmt == "json":
        output = {
            "chapters": chapter_summaries,
            "characters": [{"name": n, "mentions": c} for n, c in top_characters],
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        click.echo(f"=== {len(chapters)} chapters ===\n")
        for s in chapter_summaries:
            title_part = f" {s['title']}" if s["title"] else ""
            click.echo(f"Ch {s['chapter']:>3}{title_part} ({s['chars']} chars)")
            click.echo(f"  > {s['opening']}")
        click.echo(f"\n=== Top characters ===\n")
        for name, cnt in top_characters:
            click.echo(f"  {name}: {cnt} mentions")


if __name__ == "__main__":
    cli()
