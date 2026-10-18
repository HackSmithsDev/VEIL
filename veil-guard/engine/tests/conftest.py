import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ENGINE_ROOT / "libs"),
    str(ENGINE_ROOT / "scripts"),
]