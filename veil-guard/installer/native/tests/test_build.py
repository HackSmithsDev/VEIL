import os
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import build  # noqa: E402


class InstallerBuildTests(unittest.TestCase):
    def test_finds_binarycreator_from_configured_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "binarycreator"
            executable.touch()
            with (
                patch.dict(os.environ, {"QTIFW_BIN_DIR": directory}),
                patch.object(build.shutil, "which", return_value=None),
            ):
                self.assertEqual(build.find_binarycreator(), executable)

    def test_reports_missing_binarycreator(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(build.shutil, "which", return_value=None),
            self.assertRaisesRegex(FileNotFoundError, "binarycreator was not found"),
        ):
            build.find_binarycreator()

    def test_stages_app_bundle_and_syncs_package_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native_root = root / "installer" / "native"
            tauri_root = root / "interface" / "src-tauri"
            staging_root = native_root / "build" / "stage"
            package_name = build.PACKAGE_NAME

            (native_root / "config").mkdir(parents=True)
            meta_dir = native_root / "packages" / package_name / "meta"
            meta_dir.mkdir(parents=True)
            (native_root / "config" / "config.xml").write_text(
                "<Installer><Version>0.0.0</Version></Installer>",
                encoding="utf-8",
            )
            (native_root / "config" / "veilguard.qss").write_text(
                "QWidget { color: black; }",
                encoding="utf-8",
            )
            (meta_dir / "package.xml").write_text(
                "<Package><Version>0.0.0</Version>"
                "<ReleaseDate>2000-01-01</ReleaseDate></Package>",
                encoding="utf-8",
            )

            icon_dir = tauri_root / "icons"
            icon_dir.mkdir(parents=True)
            (icon_dir / "icon.icns").write_bytes(b"test icon")
            (icon_dir / "128x128.png").write_bytes(b"test logo")

            app_bundle = root / "VEIL Guard.app"
            app_executable = app_bundle / "Contents" / "MacOS" / "app"
            app_executable.parent.mkdir(parents=True)
            app_executable.write_bytes(b"test app")

            with (
                patch.object(build, "NATIVE_ROOT", native_root),
                patch.object(build, "STAGING_ROOT", staging_root),
                patch.object(build, "TAURI_ROOT", tauri_root),
            ):
                result = build.prepare_staging(app_bundle, "1.2.3")

            self.assertEqual(result, staging_root)
            self.assertTrue(
                (
                    staging_root
                    / "packages"
                    / package_name
                    / "data"
                    / "VEIL Guard.app"
                    / "Contents"
                    / "MacOS"
                    / "app"
                ).is_file()
            )
            config_xml = ET.parse(staging_root / "config" / "config.xml")
            package_xml = ET.parse(
                staging_root
                / "packages"
                / package_name
                / "meta"
                / "package.xml"
            )
            self.assertEqual(config_xml.findtext("Version"), "1.2.3")
            self.assertEqual(package_xml.findtext("Version"), "1.2.3")
            self.assertEqual(
                package_xml.findtext("ReleaseDate"),
                build.date.today().isoformat(),
            )


if __name__ == "__main__":
    unittest.main()
