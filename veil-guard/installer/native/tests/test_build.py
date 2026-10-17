import json
import os
import plistlib
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

    def test_builds_desktop_app_with_tauri_cli(self) -> None:
        with patch.object(build.subprocess, "run") as run:
            build.build_desktop_app(allow_unsigned=True)

        command = run.call_args.args[0]
        self.assertEqual(command[:4], ["npx", "tauri", "build", "--bundles"])
        self.assertIn("--no-sign", command)

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

    def test_sets_installer_bundle_identity_from_tauri_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tauri_root = root / "src-tauri"
            bundle_info = root / "VEIL Guard Setup.app" / "Contents" / "Info.plist"
            tauri_root.mkdir()
            bundle_info.parent.mkdir(parents=True)
            (tauri_root / "tauri.conf.json").write_text(
                json.dumps(
                    {
                        "identifier": "com.example.veilguard",
                        "productName": "VEIL Guard",
                    }
                ),
                encoding="utf-8",
            )
            with bundle_info.open("wb") as info_plist_file:
                plistlib.dump(
                    {"CFBundleIdentifier": "com.yourcompany.installerbase"},
                    info_plist_file,
                )

            with patch.object(build, "TAURI_ROOT", tauri_root):
                build.update_installer_bundle_metadata(bundle_info.parents[1], "1.2.3")

            with bundle_info.open("rb") as info_plist_file:
                info_plist = plistlib.load(info_plist_file)
            self.assertEqual(
                info_plist["CFBundleIdentifier"],
                "com.example.veilguard.installer",
            )
            self.assertEqual(info_plist["CFBundleDisplayName"], "VEIL Guard Setup")
            self.assertEqual(info_plist["CFBundleShortVersionString"], "1.2.3")


if __name__ == "__main__":
    unittest.main()
