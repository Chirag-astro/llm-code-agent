from pathlib import Path

def find_git_root(start_path):
    current = Path(start_path).resolve()

    while True:
        if (current / ".git").exists():
            return str(current)

        if current.parent == current:
            return None

        current = current.parent