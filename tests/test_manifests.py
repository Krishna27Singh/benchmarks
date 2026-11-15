import tomllib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from support import bench


ROOT = Path(__file__).resolve().parent.parent


class ManifestTests(unittest.TestCase):
    def test_real_manifests_are_well_formed(self):
        """Prevents malformed manifests from reaching benchmark execution."""
        manifests = sorted(bench.SUITES.glob("*/benchmark.toml"))
        self.assertTrue(manifests)
        for manifest in manifests:
            with self.subTest(manifest=manifest):
                data = tomllib.loads(manifest.read_text())
                ids = []
                for case in data["case"]:
                    self.assertIn("id", case)
                    self.assertIsInstance(case["id"], str)
                    self.assertTrue(case["id"])
                    self.assertIn("expected", case)
                    self.assertIsInstance(case["expected"], str)
                    if "args" in case:
                        self.assertIsInstance(case["args"], list)
                    runs = case.get("runs", 10)
                    self.assertIsInstance(runs, int)
                    self.assertNotIsInstance(runs, bool)
                    self.assertGreaterEqual(runs, 1)
                    warmup = case.get("warmup", 2)
                    self.assertIsInstance(warmup, int)
                    self.assertNotIsInstance(warmup, bool)
                    self.assertGreaterEqual(warmup, 0)
                    ids.append(case["id"])
                    for source in case.get("arx", {}).values():
                        self.assertTrue((manifest.parent / source).is_file())
                self.assertEqual(len(ids), len(set(ids)))
                for language, source in data.get("references", {}).items():
                    self.assertIn(language, bench.LANGS)
                    self.assertTrue((manifest.parent / source).is_file())

    def test_language_baselines_exist(self):
        """Prevents selected languages from lacking their startup baseline."""
        for language in bench.LANGS.values():
            with self.subTest(language=language.name):
                self.assertTrue((bench.BASELINES / language.baseline).is_file())

    def test_label_families(self):
        """Prevents report baseline matching from using the wrong label family."""
        self.assertEqual(bench.family("arx"), "arx")
        self.assertEqual(bench.family("arx-variant"), "arx")
        self.assertEqual(bench.family("python-checked"), "python")

    def test_unknown_language_exits(self):
        """Prevents typos in explicit language selections from being ignored."""
        with self.assertRaises(SystemExit):
            bench.select_langs("unknown")

    def test_unknown_suite_exits(self):
        """Prevents typos in explicit suite selections from running nothing."""
        with self.assertRaises(SystemExit):
            bench.load_suites(["unknown"])

    def test_optional_case_fields_follow_harness_defaults(self):
        """Prevents manifests from requiring fields that the harness defaults."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            suite = root / "defaults"
            suite.mkdir()
            (suite / "benchmark.toml").write_text(
                'name = "defaults"\n'
                "\n"
                "[[case]]\n"
                'id = "implicit"\n'
                'expected = "ok"\n'
                "\n"
                "[[case]]\n"
                'id = "zero-warmup"\n'
                'expected = "ok"\n'
                "warmup = 0\n"
            )
            with patch.object(bench, "SUITES", root):
                suites = bench.load_suites(["defaults"])
                plan = bench.select(suites, None)
            self.assertEqual(len(plan), 2)
            self.assertNotIn("args", plan[0][1])
            self.assertNotIn("runs", plan[0][1])
            self.assertNotIn("warmup", plan[0][1])
            self.assertEqual(plan[1][1]["warmup"], 0)
