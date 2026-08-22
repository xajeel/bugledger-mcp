import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = REPO_ROOT / "shared"
TARGET_DIR = REPO_ROOT / "python" / "src" / "bugledger_mcp" / "shared"

def sync() -> None:
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    
    shutil.copytree(SHARED_DIR, TARGET_DIR)
    print(f"Successfully synced:\n  From: {SHARED_DIR}\n  To:   {TARGET_DIR}")

if __name__ == "__main__":
    sync()
