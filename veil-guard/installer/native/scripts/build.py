"""Build the macOS VEIL Guard Qt Installer Framework package."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

INSTALLER_ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = INSTALLER_ROOT.parents[1]
INTERFACE_ROOT = REPOSITORY_ROOT / "veil-guard" / "interface"
TAURI_ROOT = INTERFACE_ROOT / "src-tauri"
APP_BUNDLE = (
    TAURI_ROOT
    / "target"
    / "release"
    / "bundle"
    / "macos"
    / "VEIL Guard.app"
)
STAGING_ROOT = NATIVE_ROOT / "build" / "stage"
OUTPUT_ROOT = NATIVE_ROOT / "dist"
PACKAGE_NAME = "com.hacksmiths.veilguard.desktop"


def find_binarycreator() -> Path:
    configured_dir = os.environ.get("QTIFW_BIN_DIR")
    if configured_dir:
        candidate = Path(configured_dir).expanduser() / "binarycreator"
        if candidate.is_file():
            return candidate

    executable = shutil.which("binarycreator")
    if executable:
        return Path(executable)

    raise FileNotFoundError(
        "Qt Installer Framework binarycreator was not found. Install Qt "
        "Installer Framework and add its bin directory to PATH or set "
        "QTIFW_BIN_DIR."
    )


def get_product_version() -> str:
    config_path = TAURI_ROOT / "tauri.conf.json"
    config = json_load(config_path)
    version = config.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Missing string version in {config_path}")
    return version


def json_load(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return config


def build_desktop_app(allow_unsigned: bool) -> None:
    command = ["npx", "tauri", "build", "--bundles", "app", "--ci"]
    if allow_unsigned:
        command.append("--no-sign")
    subprocess.run(command, cwd=INTERFACE_ROOT, check=True)


def prepare_staging(app_bundle: Path, version: str) -> Path:
    if not app_bundle.is_dir():
        raise FileNotFoundError(f"Tauri app bundle not found: {app_bundle}")
    executable = app_bundle / "Contents" / "MacOS" / "app"
    if not executable.is_file():
        raise FileNotFoundError(f"App executable not found: {executable}")

    if STAGING_ROOT.exists():
        shutil.rmtree(STAGING_ROOT)

    staged_config = STAGING_ROOT / "config"
    staged_packages = STAGING_ROOT / "packages" / PACKAGE_NAME
    staged_data = staged_packages / "data"
    staged_meta = staged_packages / "meta"
    staged_config.mkdir(parents=True)
    staged_data.mkdir(parents=True)
    staged_meta.mkdir(parents=True)

    shutil.copy2(NATIVE_ROOT / "config" / "config.xml", staged_config / "config.xml")
    shutil.copy2(NATIVE_ROOT / "config" / "veilguard.qss", staged_config / "veilguard.qss")
    shutil.copy2(
        TAURI_ROOT / "icons" / "icon.icns",
        staged_config / "veilguard.icns",
    )
    shutil.copy2(
        TAURI_ROOT / "icons" / "128x128.png",
        staged_config / "veilguard.png",
    )
    shutil.copytree(app_bundle, staged_data / app_bundle.name, symlinks=True)

    package_xml = ET.parse(NATIVE_ROOT / "packages" / PACKAGE_NAME / "meta" / "package.xml")
    package_root = package_xml.getroot()
    package_root.find("Version").text = version
    package_root.find("ReleaseDate").text = date.today().isoformat()
    package_xml.write(staged_meta / "package.xml", encoding="UTF-8", xml_declaration=True)

    config_xml_path = staged_config / "config.xml"
    config_xml = ET.parse(config_xml_path)
    config_root = config_xml.getroot()
    config_root.find("Version").text = version
    config_xml.write(config_xml_path, encoding="UTF-8", xml_declaration=True)
    return STAGING_ROOT


def build_installer(binarycreator: Path, version: str) -> Path:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_ROOT / f"VEIL Guard Setup {version}.app"
    if output_path.exists():
        if output_path.is_dir():
            shutil.rmtree(output_path)
        else:
            output_path.unlink()

    subprocess.run(
        [
            str(binarycreator),
            "-c",
            str(STAGING_ROOT / "config" / "config.xml"),
            "-p",
            str(STAGING_ROOT / "packages"),
            str(output_path),
        ],
        cwd=NATIVE_ROOT,
        check=True,
    )
    update_installer_bundle_metadata(output_path, version)
    return output_path


def update_installer_bundle_metadata(bundle_path: Path, version: str) -> None:
    tauri_config = json_load(TAURI_ROOT / "tauri.conf.json")
    identifier = tauri_config.get("identifier")
    product_name = tauri_config.get("productName")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError("Missing string identifier in Tauri configuration")
    if not isinstance(product_name, str) or not product_name:
        raise ValueError("Missing string productName in Tauri configuration")

    info_plist_path = bundle_path / "Contents" / "Info.plist"
    with info_plist_path.open("rb") as info_plist_file:
        info_plist = plistlib.load(info_plist_file)
    if not isinstance(info_plist, dict):
        raise ValueError(f"Expected a dictionary in {info_plist_path}")

    setup_name = f"{product_name} Setup"
    info_plist.update(
        {
            "CFBundleIdentifier": f"{identifier}.installer",
            "CFBundleName": setup_name,
            "CFBundleDisplayName": setup_name,
            "CFBundleShortVersionString": version,
            "CFBundleVersion": version,
        }
    )
    with info_plist_path.open("wb") as info_plist_file:
        plistlib.dump(info_plist, info_plist_file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-app-build",
        action="store_true",
        help="use the existing Tauri .app bundle instead of rebuilding it",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="stage and validate the package payload without binarycreator",
    )
    parser.add_argument(
        "--allow-unsigned",
        action="store_true",
        help="build an unsigned local test package; not for distribution",
    )
    args = parser.parse_args(argv)

    if sys.platform != "darwin":
        parser.error("The initial Qt IF package target is macOS; build on macOS.")

    binarycreator = None
    if not args.stage_only:
        try:
            binarycreator = find_binarycreator()
        except FileNotFoundError as error:
            parser.error(str(error))

    if not args.skip_app_build:
        build_desktop_app(args.allow_unsigned)

    version = get_product_version()
    prepare_staging(APP_BUNDLE, version)
    print(f"Staged VEIL Guard {version} at {STAGING_ROOT}")

    if args.stage_only:
        return 0

    output_path = build_installer(binarycreator, version)
    print(f"Built installer: {output_path}")
    if args.allow_unsigned:
        print("This unsigned installer is for local testing only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
