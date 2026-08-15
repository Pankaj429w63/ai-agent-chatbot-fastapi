import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_APP_DIR = os.path.join(_PROJECT_ROOT, "app")

for _p in (_PROJECT_ROOT, _APP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
