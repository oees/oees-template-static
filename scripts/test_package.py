"""Tests for scripts/package.py. Run with: python3 -m unittest discover -s scripts"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("package", Path(__file__).with_name("package.py"))
assert _SPEC is not None and _SPEC.loader is not None
package = importlib.util.module_from_spec(_SPEC)
sys.modules["package"] = package  # dataclasses resolve annotations through sys.modules
_SPEC.loader.exec_module(package)

# Built at runtime so this file does not itself look like it holds a secret.
FAKE_DO_TOKEN = "dop_v1_" + "a" * 64
FAKE_REMOTE_URL = "postgresql://app:" + "s3cret" + "@db-cluster.example.com:25060/app"


def make_project(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "project"
        self.out = Path(self._tmp.name) / "out"
        self.root.mkdir()
        self.out.mkdir()

    def test_clean_project_is_zipped_without_dependencies_or_build_output(self) -> None:
        make_project(
            self.root,
            {
                "package.json": '{"name": "campaign-site"}',
                "index.html": "<h1>Hola</h1>",
                ".env.example": "VITE_SITE_URL=http://localhost:5173\n",
                "node_modules/react/index.js": "module.exports = {}",
                "dist/index.html": "<h1>built</h1>",
                ".DS_Store": "x",
            },
        )

        code = package.main(["--out", str(self.out)], root=self.root)

        self.assertEqual(code, 0)
        [archive_path] = list(self.out.glob("campaign-site-*.zip"))
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
        self.assertEqual(
            names,
            {
                "campaign-site/package.json",
                "campaign-site/index.html",
                "campaign-site/.env.example",
            },
        )

    def test_env_and_key_files_are_never_zipped(self) -> None:
        make_project(
            self.root,
            {
                "package.json": '{"name": "site"}',
                ".env": "VITE_SITE_URL=x",
                ".env.production": "X=y",
                "certs/server.key": "k",
            },
        )

        code = package.main(["--out", str(self.out)], root=self.root)

        self.assertEqual(code, 0)
        [archive_path] = list(self.out.glob("site-*.zip"))
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(archive.namelist(), ["site/package.json"])

    def test_token_in_source_blocks_packaging(self) -> None:
        make_project(self.root, {"src/api.ts": f'const token = "{FAKE_DO_TOKEN}";\n'})

        result = package.scan(self.root)

        self.assertEqual(len(result.problems), 1)
        self.assertIn("src/api.ts:1", result.problems[0])
        self.assertNotIn(FAKE_DO_TOKEN, result.problems[0])

    def test_remote_connection_string_blocks_but_local_one_does_not(self) -> None:
        local = "DATABASE_URL=postgres://postgres:postgres@localhost:5432/app\n"
        self.assertEqual(package.find_secrets(local), [])
        self.assertEqual(
            package.find_secrets(f"DATABASE_URL={FAKE_REMOTE_URL}\n"),
            [(1, "a connection string with a password")],
        )

    def test_secrets_inside_excluded_folders_are_ignored(self) -> None:
        make_project(
            self.root,
            {"index.html": "ok", "node_modules/pkg/key.txt": FAKE_DO_TOKEN},
        )

        self.assertEqual(package.scan(self.root).problems, [])

    def test_oversized_file_blocks_packaging(self) -> None:
        make_project(self.root, {"index.html": "ok"})
        with (self.root / "video.mp4").open("wb") as handle:
            handle.truncate(package.MAX_FILE_BYTES + 1)

        problems = package.scan(self.root).problems

        self.assertEqual(len(problems), 1)
        self.assertIn("video.mp4", problems[0])

    def test_zip_name_comes_from_the_project_table_of_pyproject(self) -> None:
        make_project(
            self.root,
            {
                "pyproject.toml": (
                    '[tool.example]\nname = "not-this"\n\n'
                    '[project]\nversion = "0.1.0"\nname = "campaign-2027"\n'
                )
            },
        )

        self.assertEqual(package.project_name(self.root), "campaign-2027")


if __name__ == "__main__":
    unittest.main()
