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
@click.version_option("1.0.0")
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
@click.option("--mode", type=click.Choice(["golden", "short", "auto"]), default="auto",
              help="Validation mode: golden (黄金三章), short (10章短篇), auto-detect.")
def validate(file, mode):
    """Run full validation: word count + banned words + format check."""
    text = _read_file(file)
    chapters = _split_chapters(text)
    errors = []
    warnings = []

    if mode == "auto":
        mode = "golden" if len(chapters) <= 3 else "short"

    min_chars, max_chars = (2090, 2730) if mode == "golden" else (950, 1260)
    label = "2200-2600±5%" if mode == "golden" else "1000-1200±5%"

    for ch in chapters:
        cc = _count_chars(ch["body"])
        if cc < min_chars or cc > max_chars:
            errors.append(
                f"Ch {ch['number']}: {cc} chars — outside target {label}"
            )
        dr = _dialogue_ratio(ch["body"])
        threshold = 0.40 if mode == "golden" else 0.50
        if dr < threshold:
            warnings.append(
                f"Ch {ch['number']}: dialogue ratio {dr:.0%} < {threshold:.0%} target"
            )

    banned_count = 0
    for line in text.split("\n"):
        for word in BANNED_WORDS:
            banned_count += line.count(word)
        for pattern in BANNED_PATTERNS:
            banned_count += len(pattern.findall(line))
    if banned_count > 0:
        errors.append(f"Banned words/patterns found: {banned_count} instances (run 'scan' for details)")

    total = sum(_count_chars(ch["body"]) for ch in chapters)
    if mode == "short":
        if total < 9000 or total > 12000:
            errors.append(f"Total chars {total} outside 9000-12000 range")

    has_chapter_counts = bool(WORD_COUNT_RE.findall(text))
    if not has_chapter_counts and chapters:
        warnings.append("Missing [本章字数：XXXX] markers")

    expected = list(range(1, len(chapters) + 1))
    actual = [ch["number"] for ch in chapters]
    if actual != expected:
        errors.append(f"Non-sequential chapters: got {actual}, expected {expected}")

    result = {
        "mode": mode,
        "chapter_count": len(chapters),
        "total_chars": total,
        "errors": errors,
        "warnings": warnings,
        "passed": len(errors) == 0,
    }

    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    cli()
