import os
import re
import json
from collections import Counter

def clean_srt(srt_content):
    lines = srt_content.split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if '-->' in line:
            continue
        text_lines.append(line)
    return " ".join(text_lines)

def main():
    sung_dir = os.path.join('sung', '레거시', '자막')
    if not os.path.exists(sung_dir):
        print(f"Directory {sung_dir} does not exist.")
        return
        
    srt_files = [f for f in os.listdir(sung_dir) if f.endswith('.srt')]
    print(f"Found {len(srt_files)} SRT files in '{sung_dir}' for analysis.")
    
    all_texts = {}
    full_corpus = ""
    
    for f in srt_files:
        path = os.path.join(sung_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        cleaned = clean_srt(content)
        all_texts[f] = cleaned
        full_corpus += " " + cleaned

    keywords_list = {
        '120일선 (120-Day Line)': ['120일선', '120일', '120선', '120일 이동평균선'],
        '역프리미엄 및 김프 (Negative Premium/Kimp)': ['역프리미엄', '역프', '김프', '김치프리미엄', '프리미엄'],
        '달러 및 나스닥 (Dollar/Nasdaq)': ['달러', '나스닥', '환율', '미국'],
        '비트코인 및 알트코인 (Bitcoin/Altcoin)': ['비트코인', '비트', '이더리움', '알트코인', '알트'],
        '매크로 및 유동성 (Macro/Liquidity)': ['금리', ' cpi ', '유동성', '연준', '파월'],
        '투자 마인드셋 (HODL/Mindset)': ['HODL', '홀드', '10년', '강남', '전주', '장기투자', '장투']
    }

    stats = {}
    for category, syns in keywords_list.items():
        category_counts = {}
        for syn in syns:
            pattern = re.compile(re.escape(syn.strip()), re.IGNORECASE)
            count = len(pattern.findall(full_corpus))
            category_counts[syn.strip()] = count
        stats[category] = {
            'total_count': sum(category_counts.values()),
            'breakdown': category_counts
        }
        
    contexts = {}
    for category, syns in keywords_list.items():
        sample_sentences = []
        primary_term = syns[0].strip()
        sentences = re.split(r'(?<=[.!?])\s+', full_corpus)
        for s in sentences:
            if re.search(re.escape(primary_term), s, re.IGNORECASE):
                s_cleaned = re.sub(r'\s+', ' ', s.strip())
                if s_cleaned not in sample_sentences:
                    sample_sentences.append(s_cleaned)
                if len(sample_sentences) >= 5:
                    break
        contexts[category] = sample_sentences

    words = re.findall(r'[가-힣a-zA-Z]{2,}', full_corpus)
    fillers = {'그래서', '이제', '근데', '하고', '이때', '현재', '되고', '됩니다', '그죠', '여러분들', '말씀을', '보고', '조금', '여러분들이', '여러분들에게', '생각을', '정도', '많이', '얘기를', '실제로', '겁니다', '그러면', '있습니다', '어느', '다음에', '되는', '이미', '다시', '합니다', '그렇게', '보시면', '되면', '있다', '대해서', '수가', '것이다라고', '그런', '거예요', '계속', '한번', '거는', '돼요', '크게', '제일', '혹은', '시장의', '하겠습니다', '오늘', '쉽게', '있어요', '그다음에', '된다', '하면', '것이다', '전에', '했죠', '일봉상으로', '그럼', '시장에', '날에', '분들은', '어떤', '일단', '저는', '가능성이', '있고', '차트', '가지고', '대해', '보고서', '다시한번', '이렇게', '그냥', '이거', '제가', '이게', '우리가', '있는', '진짜', '여기서', '지금', '어떻게', '이런', '그리고', '그렇기', '때문에', '하는', '하는것', '보면', '생각', '상황', '대한', '해서', '올라', '내려'}
    filtered_words = [w for w in words if w not in fillers and len(w) > 1]
    top_words = Counter(filtered_words).most_common(100)

    analysis_report = {
        'keyword_stats': stats,
        'contexts': contexts,
        'top_words': top_words
    }
    
    with open('sung_analysis_report.json', 'w', encoding='utf-8') as out:
        json.dump(analysis_report, out, ensure_ascii=False, indent=2)
        
    print("Seong Jeong-gil analysis report saved to sung_analysis_report.json.")

if __name__ == '__main__':
    main()
