import os
import glob
import sys

# Add skills/kodari path to import youtube_book_maker
sys.path.append(os.path.abspath(os.path.join('.agent', 'skills', 'kodari')))
from youtube_book_maker import refine_srt_content

def main():
    sub_dirs = [
        os.path.join('coin', 'sung', '레거시(성정길)', '자막'),
        os.path.join('coin', 'coinjin', '레거시(코인진)', '자막')
    ]
    
    for sub_dir in sub_dirs:
        if not os.path.exists(sub_dir):
            print(f"Directory {sub_dir} does not exist.")
            continue

        txt_dir = sub_dir.replace('자막', '대본')
        os.makedirs(txt_dir, exist_ok=True)

        srt_files = glob.glob(os.path.join(sub_dir, '*.srt'))
        print(f"\nFound {len(srt_files)} SRT files in {sub_dir}.")

        total_removed = 0
        for idx, srt_path in enumerate(srt_files, 1):
            file_name = os.path.basename(srt_path)
            txt_path = os.path.join(txt_dir, file_name.replace('.srt', '.txt'))
            
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            removed, refined_srt, plain_text = refine_srt_content(content)
            total_removed += removed
            
            # [1] Output removed counts
            print(f"  [{idx}/{len(srt_files)}] {file_name}:")
            print(f"    Removed: {removed} blocks.")
            
            # [2] Save refined SRT
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(refined_srt)
                
            # [3] Save plain text TXT
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)

        # Cleanup leftover TXT files in sub_dir (자막 folder)
        leftover_txts = glob.glob(os.path.join(sub_dir, '*.txt'))
        for lt in leftover_txts:
            try:
                os.remove(lt)
            except Exception as e:
                print(f"    Failed to remove leftover {lt}: {e}")

        print(f"Successfully cleaned all {len(srt_files)} files in {sub_dir}. Leftover text files removed from 자막 folder.")

if __name__ == '__main__':
    main()
