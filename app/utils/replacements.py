import os
from pathlib import Path

def batch_replace(root_dir: Path, replacements: dict, encoding='utf-8'):
    for file in root_dir.rglob('*.txt'):
        text = file.read_text(encoding=encoding)
        new_text = text
        for old, new in replacements.items():
            new_text = new_text.replace(old, new)
        if new_text != text:
            print(f"Updating {file.relative_to(root_dir)}")
            file.write_text(new_text, encoding=encoding)

if __name__ == "__main__":
    replacements = {
        "Emmedidling": "eFormidling",
        "usstotte@dir.no": "brukerstotte@digdir.no",
        "Digitization Directorate": "Norwegian Digitalisation Agency",
    }

    # adjust path as needed
    base = Path("./_docs_en")
    batch_replace(base, replacements)
    print("Done!")
