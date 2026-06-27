import re
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_COIN_DIR = BACKEND_ROOT / 'research' / 'coin'
SUNG_SUBTITLE_DIR = RESEARCH_COIN_DIR / 'sung' / '레거시(성정길)' / '자막'
OUTPUT_DIR = Path(__file__).resolve().parent / 'output'

def ts_to_ms(ts):
    m = re.match(r'(\d+):(\d+):(\d+),(\d+)', ts.strip())
    if m:
        h, mins, sec, ms = map(int, m.groups())
        return h*3600000 + mins*60000 + sec*1000 + ms
    return 0

def ms_to_ts(ms):
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def normalize_text(text):
    if not text:
        return ""
    return re.sub(r'[^a-zA-Z0-9가-힣]', '', text)

def refine_srt_content(srt_content):
    # Parse SRT content
    blocks = srt_content.strip().split('\n\n')
    subtitles = []
    
    for b in blocks:
        lines = [l.strip() for l in b.split('\n') if l.strip()]
        if len(lines) < 3:
            continue
        idx_str = lines[0]
        time_str = lines[1]
        text_lines = lines[2:]
        
        if '-->' not in time_str:
            continue
            
        time_parts = time_str.split('-->')
        start_ts = time_parts[0].strip()
        end_ts = time_parts[1].strip()
        
        subtitles.append({
            'start': start_ts,
            'end': end_ts,
            'lines': text_lines,
            'text': " ".join(text_lines)
        })
        
    removed_count = 0
    
    # Stage 1: Filtering duplicates, subsets, and short interim results
    subtitles_1st = []
    i = 0
    while i < len(subtitles):
        curr = subtitles[i]
        curr_text = curr['text'].strip()
        curr_norm = normalize_text(curr_text)
        
        if not curr_norm:
            removed_count += 1
            i += 1
            continue
            
        curr_dur = ts_to_ms(curr['end']) - ts_to_ms(curr['start'])
        is_short = curr_dur <= 100
        
        # Rule 2 & 3: Prefix/Subset expansion check
        is_subset = False
        for j in range(i + 1, min(i + 6, len(subtitles))):
            next_sub = subtitles[j]
            next_norm = normalize_text(next_sub['text'])
            if curr_norm in next_norm and curr_norm != next_norm:
                is_subset = True
                break
                
        # Rule 5: Consecutive repetitions check
        is_duplicate = False
        if i + 1 < len(subtitles):
            next_sub = subtitles[i+1]
            next_norm = normalize_text(next_sub['text'])
            if curr_norm == next_norm:
                is_duplicate = True
                
        # Rule 1: Short duration (<= 0.1s) is removed only if it's a subset or duplicate (no new info)
        if (is_short and (is_subset or is_duplicate)) or is_subset or is_duplicate:
            removed_count += 1
            i += 1
            continue
            
        subtitles_1st.append(curr)
        i += 1
        
    # Stage 2: Merge sentences and remove duplicate lines
    refined = []
    i = 0
    while i < len(subtitles_1st):
        curr = subtitles_1st[i]
        
        if not curr['lines']:
            removed_count += 1
            i += 1
            continue
            
        merged = False
        if i + 1 < len(subtitles_1st):
            next_sub = subtitles_1st[i+1]
            
            # Rule 4: Remove duplicate lines between current and next
            if curr['lines'] and next_sub['lines']:
                last_line_norm = normalize_text(curr['lines'][-1])
                first_line_norm = normalize_text(next_sub['lines'][0])
                if last_line_norm and first_line_norm and last_line_norm == first_line_norm:
                    next_sub['lines'] = next_sub['lines'][1:]
                    next_sub['text'] = " ".join(next_sub['lines'])
                    
            if not next_sub['lines']:
                # If next_sub becomes empty, merge is trivial, but let's just skip it
                # and let the loop continue
                subtitles_1st[i+1] = curr
                removed_count += 1
                i += 1
                merged = True
                continue
            
            # Rule 6: Merge consecutive short sentences if they continue
            gap = ts_to_ms(next_sub['start']) - ts_to_ms(curr['end'])
            curr_text = curr['text'].strip()
            next_text = next_sub['text'].strip()
            ends_with_terminator = curr_text and curr_text[-1] in ['.', '?', '!']
            
            if gap <= 1200 and len(curr_text) < 50 and len(next_text) < 50 and not ends_with_terminator:
                curr['end'] = next_sub['end']
                curr['lines'] = curr['lines'] + next_sub['lines']
                curr['text'] = " ".join(curr['lines'])
                subtitles_1st[i+1] = curr
                removed_count += 1
                i += 1
                merged = True
                continue
                
        if not merged:
            refined.append(curr)
            i += 1
            
    # Re-index and format refined SRT
    refined_srt_lines = []
    for idx, sub in enumerate(refined, 1):
        refined_srt_lines.append(f"{idx}\n{sub['start']} --> {sub['end']}\n" + "\n".join(sub['lines']) + "\n")
        
    refined_srt = "\n".join(refined_srt_lines)
    
    # Generate final plain text transcript (Rule 8)
    plain_text_sentences = []
    for sub in refined:
        text = sub['text'].strip()
        if text:
            # Clean double spaces
            text = re.sub(r'\s+', ' ', text)
            plain_text_sentences.append(text)
            
    # Group sentences into paragraphs based on sentence count & terminators
    paragraphs = []
    temp_p = []
    for s in plain_text_sentences:
        temp_p.append(s)
        if len(temp_p) >= 4 or s.endswith('.') or s.endswith('?') or s.endswith('!'):
            paragraphs.append(" ".join(temp_p))
            temp_p = []
    if temp_p:
        paragraphs.append(" ".join(temp_p))
        
    plain_text = "\n\n".join(paragraphs)
    
    return removed_count, refined_srt, plain_text

def main():
    sample_file = SUNG_SUBTITLE_DIR / "(260602)Negative Premium -4%, Bitcoin Breaks 120-Day Line! Strategy's First Bitcoin Sell.srt"
    if not sample_file.exists():
        print(f"File {sample_file} not found.")
        return
        
    content = sample_file.read_text(encoding='utf-8')
        
    removed, refined_srt, plain_text = refine_srt_content(content)
    print(f"Original blocks: {len(content.split('\n\n'))}")
    print(f"Removed blocks: {removed}")
    print(f"Remaining blocks: {len(refined_srt.split('\n\n'))}")
    
    # Save test outputs
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / 'refined_test.srt').write_text(refined_srt, encoding='utf-8')
    (OUTPUT_DIR / 'refined_test.txt').write_text(plain_text, encoding='utf-8')
        
    print(f"Saved refined_test.srt and refined_test.txt to {OUTPUT_DIR}.")

if __name__ == '__main__':
    main()
