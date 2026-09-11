import os
from pathlib import Path

def print_tree(dir_path, prefix=""):
    path = Path(dir_path)
    if path.name in [".git", "__pycache__"]: return
    
    # Sort directories first, then files
    try:
        entries = sorted(list(path.iterdir()), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError:
        return
        
    for i, entry in enumerate(entries):
        if entry.name in [".git", "__pycache__", ".venv", "venv", "node_modules"]: continue
        
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(entry, prefix + extension)

if __name__ == "__main__":
    print_tree(".")
