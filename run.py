import subprocess
import sys
from pathlib import Path

def install_deps() -> None:
    req = Path(__file__).parent / "requirements.txt"
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req), "-q"])

if __name__ == "__main__":
    install_deps()
    from app.main import start
    start()
