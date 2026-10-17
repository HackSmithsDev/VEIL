"""Build wheel and source-distribution artifacts for the Engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from setuptools import build_meta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"


def build_distributions(distribution: str = "both") -> list[Path]:
    """Build selected distributions into the Engine's dist directory."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    artifacts: list[Path] = []

    if distribution in {"wheel", "both"}:
        artifacts.append(Path(build_meta.build_wheel(str(DIST_DIR))))
    if distribution in {"sdist", "both"}:
        artifacts.append(Path(build_meta.build_sdist(str(DIST_DIR))))

    return [path if path.is_absolute() else DIST_DIR / path for path in artifacts]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("wheel", "sdist", "both"),
        default="both",
        help="distribution artifact to build (default: both)",
    )
    args = parser.parse_args(argv)

    for artifact in build_distributions(args.format):
        print(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())