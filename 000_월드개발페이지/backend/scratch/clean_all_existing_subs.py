import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_COIN_DIR = BACKEND_ROOT / 'research' / 'coin'

# Add skills/kodari path to import youtube_book_maker
sys.path.append(os.path.abspath(os.path.join('.agent', 'skills', 'kodari')))
from youtube_book_maker import refine_srt_content

def main():
    sub_dirs = [
        RESEARCH_COIN_DIR / 'sung' / '레거시(성정길)' / '자막',
        RESEARCH_COIN_DIR / 'coinjin' / '레거시(코인진)' / '자막',
    ]
    
    for sub_dir in sub_dirs:
        if not sub_dir.exists():
            print(f"Directory {sub_dir} does not exist.")
            continue

        txt_dir = sub_dir.parent / '대본'
        txt_dir.mkdir(exist_ok=True)

        srt_files = sorted(sub_dir.glob('*.srt'))
        print(f"\nFound {len(srt_files)} SRT files in {sub_dir}.")

        total_removed = 0
        for idx, srt_path in enumerate(srt_files, 1):
            file_name = srt_path.name
            txt_path = txt_dir / srt_path.with_suffix('.txt').name
            
            content = srt_path.read_text(encoding='utf-8')
                
            removed, refined_srt, plain_text = refine_srt_content(content)
            total_removed += removed
            
            # [1] Output removed counts
            print(f"  [{idx}/{len(srt_files)}] {file_name}:")
            print(f"    Removed: {removed} blocks.")
            
            # [2] Save refined SRT
            srt_path.write_text(refined_srt, encoding='utf-8')
                
            # [3] Save plain text TXT
            txt_path.write_text(plain_text, encoding='utf-8')

        # Cleanup leftover TXT files in sub_dir (자막 folder)
        leftover_txts = sub_dir.glob('*.txt')
        for lt in leftover_txts:
            try:
                lt.unlink()
            except Exception as e:
                print(f"    Failed to remove leftover {lt}: {e}")

        print(f"Successfully cleaned all {len(srt_files)} files in {sub_dir}. Leftover text files removed from 자막 folder.")

if __name__ == '__main__':
    main()
