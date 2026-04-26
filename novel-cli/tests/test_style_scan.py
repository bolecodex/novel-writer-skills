import json
import sys
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from novel_cli.cli import _scan_text, cli  # noqa: E402


def finding_types(text):
    return {finding["type"] for finding in _scan_text(text)}


class StyleScanTest(unittest.TestCase):
    def test_detects_general_staccato_action_chain(self):
        text = "我翻包。我找卡。我递过去。护士接了。"

        types = finding_types(text)

        self.assertIn("staccato_action_chain", types)
        self.assertIn("repeated_subject_chain", types)

    def test_detects_process_chain_without_exact_phrase(self):
        text = "她挂号。她扫码。她刷卡。她办手续。"

        types = finding_types(text)

        self.assertIn("low_value_process_chain", types)

    def test_detects_cross_line_action_chain(self):
        text = "我推门。\n我拿包。\n我关灯。"

        types = finding_types(text)

        self.assertIn("staccato_action_chain", types)

    def test_detects_speech_tag_chain(self):
        text = "他说。她问。我开口。"

        types = finding_types(text)

        self.assertIn("speech_tag_chain", types)

    def test_does_not_flag_pure_short_dialogue(self):
        text = '"你疯了。"\n"我没有。"\n"那你解释。"'

        self.assertEqual([], _scan_text(text))

    def test_does_not_flag_normal_one_or_two_action_beats(self):
        text = "我把病历递给医生，纸角被汗浸软。她看完以后，把产检单推回我面前。"

        self.assertEqual([], _scan_text(text))

    def test_validate_fails_on_severe_style_issue(self):
        body = "我翻包。我找卡。我递过去。护士接了。\n" + (
            "病房里的争执没有停，所有人都等着下一句话落下来。" * 45
        )
        text = f"【第1章 测试】\n{body}\n[本章字数：1000]\n"
        runner = CliRunner()
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
            handle.write(text)
            path = handle.name
        try:
            result = runner.invoke(cli, ["validate", path, "--mode", "long"])
        finally:
            Path(path).unlink(missing_ok=True)

        self.assertNotEqual(0, result.exit_code)
        payload = json.loads(result.output)
        self.assertFalse(payload["passed"])
        self.assertTrue(any("Severe mechanical narration" in item for item in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
