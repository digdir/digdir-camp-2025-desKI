import os
from pathlib import Path
from googletrans import Translator

# ⚠️ Change these paths to your actual input/output folders
INPUT_DIR = Path("_docs")
OUTPUT_DIR = Path("_docs_en")

def translate_folder(input_dir: Path, output_dir: Path, src_lang='no', dest_lang='en'):
    translator = Translator()
    for txt_file in input_dir.rglob('*.txt'):
        rel_path = txt_file.relative_to(input_dir)
        out_file = output_dir / rel_path
        out_file.parent.mkdir(parents=True, exist_ok=True)

        text = txt_file.read_text(encoding='utf-8')
        print(f'Translating {txt_file} → {out_file}')
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        out_file.write_text(translated.text, encoding='utf-8')

if __name__ == '__main__':
    translate_folder(INPUT_DIR, OUTPUT_DIR)
    print("✅ Done.")
