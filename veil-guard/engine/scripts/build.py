"""Build both distributable Engine package formats."""

from package import main


if __name__ == "__main__":
    raise SystemExit(main(["--format", "both"]))