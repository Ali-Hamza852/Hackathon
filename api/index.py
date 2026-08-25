import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

for path in (str(BACKEND_DIR), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.main import app
