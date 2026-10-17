import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import clean  # noqa: E402
import package  # noqa: E402


class PackageScriptTests(unittest.TestCase):
    def test_builds_requested_distribution_formats(self) -> None:
        with (
            patch.object(package, "DIST_DIR", Path("/tmp/veil-engine-dist")),
            patch.object(package.build_meta, "build_wheel", return_value="engine.whl") as wheel,
            patch.object(package.build_meta, "build_sdist", return_value="engine.tar.gz") as sdist,
            patch.object(Path, "mkdir") as mkdir,
        ):
            artifacts = package.build_distributions("both")

        mkdir.assert_called_once_with(parents=True, exist_ok=True)
        wheel.assert_called_once_with("/tmp/veil-engine-dist")
        sdist.assert_called_once_with("/tmp/veil-engine-dist")
        self.assertEqual(
            artifacts,
            [
                Path("/tmp/veil-engine-dist/engine.whl"),
                Path("/tmp/veil-engine-dist/engine.tar.gz"),
            ],
        )

    def test_clean_removes_only_known_engine_build_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build = root / "build"
            dist = root / "dist"
            egg_info = root / "libs" / "veil_guard_engine.egg-info"
            unrelated = root / "user-data.txt"
            for target in (build, dist, egg_info):
                target.mkdir(parents=True)
            unrelated.write_text("keep", encoding="utf-8")

            with patch.object(clean, "PROJECT_ROOT", root):
                removed = clean.clean_artifacts()

            self.assertEqual(set(removed), {build, dist, egg_info})
            self.assertTrue(unrelated.exists())
            self.assertTrue(all(not path.exists() for path in removed))

    def test_clean_does_not_follow_symlinked_build_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "engine"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            sentinel = outside / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            (root / "dist").symlink_to(outside, target_is_directory=True)

            with patch.object(clean, "PROJECT_ROOT", root):
                removed = clean.clean_artifacts()

            self.assertIn(root / "dist", removed)
            self.assertTrue(sentinel.exists())
            self.assertFalse((root / "dist").is_symlink())


if __name__ == "__main__":
    unittest.main()
