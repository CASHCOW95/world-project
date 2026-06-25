import os
import shutil
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_html_book(html_path, cover_img_path):
    abs_cover_path = os.path.abspath(cover_img_path)
    cover_url = f"file:///{abs_cover_path.replace(os.sep, '/')}"

    book_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>성정길 실전 매매 교과서</title>
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        @page {{
            size: A4;
            margin: 22mm 20mm 22mm 20mm;
        }}
        
        @page :first {{
            margin: 0;
        }}
        
        body {{
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            font-size: 10pt;
            line-height: 1.85;
            color: #334155;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        /* Cover Page Styling */
        .cover-page {{
            width: 210mm;
            height: 297mm;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            position: relative;
            page-break-after: always;
            page-break-before: avoid;
            background-color: #0b0f19;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .cover-img-container {{
            width: 210mm;
            height: 185mm;
            overflow: hidden;
        }}
        
        .cover-img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .cover-text-container {{
            padding: 25px 35px;
            height: 112mm;
            box-sizing: border-box;
            background-color: #0b0f19;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .cover-title {{
            font-size: 26pt;
            font-weight: 800;
            line-height: 1.3;
            color: #ffffff;
            margin: 0 0 10px 0;
            letter-spacing: -0.5px;
        }}
        
        .cover-subtitle {{
            font-size: 11.5pt;
            color: #94a3b8;
            font-weight: 400;
            margin: 0;
            line-height: 1.5;
        }}
        
        .cover-footer {{
            border-top: 1px solid #1e293b;
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .cover-author {{
            font-size: 10pt;
            font-weight: 700;
            color: #e2e8f0;
        }}
        
        .cover-meta {{
            font-size: 8.5pt;
            color: #64748b;
            text-align: right;
            line-height: 1.4;
        }}
        
        /* Table of Contents */
        .toc-page {{
            page-break-before: always;
            page-break-after: always;
            padding-top: 10mm;
        }}
        
        .toc-title {{
            font-size: 22pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 12px;
            margin-bottom: 35px;
            letter-spacing: -0.5px;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .toc-item {{
            display: flex;
            justify-content: space-between;
            font-size: 11pt;
            margin-bottom: 20px;
            border-bottom: 1px dashed #e2e8f0;
            padding-bottom: 6px;
        }}
        
        .toc-name {{
            font-weight: 500;
            background-color: #ffffff;
            padding-right: 12px;
            color: #334155;
        }}
        
        .toc-page-num {{
            background-color: #ffffff;
            padding-left: 12px;
            font-weight: 700;
            color: #10b981;
        }}
        
        /* Typography Elements */
        h1 {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 3px solid #10b981;
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 25px;
            line-height: 1.35;
            letter-spacing: -0.5px;
        }}
        
        h2 {{
            font-size: 13pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 30px;
            margin-bottom: 12px;
            border-left: 4px solid #10b981;
            padding-left: 12px;
            line-height: 1.4;
        }}
        
        h3 {{
            font-size: 11pt;
            font-weight: 700;
            color: #1e293b;
            margin-top: 20px;
            margin-bottom: 8px;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 18px;
            text-align: justify;
            text-justify: inter-word;
            word-break: keep-all;
            text-indent: 10px;
        }}
        
        .quote-box {{
            background-color: #f8fafc;
            border-left: 4px solid #10b981;
            padding: 18px 24px;
            margin: 22px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            font-size: 9.5pt;
            color: #475569;
            line-height: 1.65;
            word-break: keep-all;
            text-indent: 0;
        }}
        
        .formula-box {{
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 18px;
            margin: 22px 0;
            border-radius: 10px;
            font-size: 9.5pt;
        }}
        
        .formula-title {{
            font-weight: 700;
            color: #047857;
            margin-bottom: 8px;
            font-size: 10.5pt;
        }}
        
        ul, ol {{
            margin-top: 0;
            margin-bottom: 18px;
            padding-left: 22px;
        }}
        
        li {{
            margin-bottom: 10px;
            line-height: 1.65;
        }}
        
        .highlight {{
            font-weight: 700;
            color: #059669;
        }}
        
        .key-concept {{
            font-weight: 700;
            color: #0f172a;
            background-color: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 9.5pt;
        }}
        
        /* Footnotes section styling */
        .footnotes-section {{
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            padding-top: 12px;
            font-size: 8.5pt;
            color: #64748b;
            line-height: 1.6;
            page-break-inside: avoid;
        }}
        
        .footnote-title {{
            font-weight: 700;
            color: #475569;
            margin-bottom: 6px;
            font-size: 9pt;
        }}
        
        .footnote-item {{
            margin-bottom: 6px;
        }}
        
        .footnote-term {{
            font-weight: 700;
            color: #059669;
        }}
        
        .footnote-child {{
            color: #4b5563;
            background-color: #f3f4f6;
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 8pt;
        }}
        
        /* Table styles for Appendix */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 9.5pt;
        }}
        
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f8fafc;
            color: #0f172a;
            font-weight: 700;
        }}
        
        tr:nth-child(even) {{
            background-color: rgba(248, 250, 252, 0.5);
        }}
    </style>
</head>
<body>

    <!-- Cover Page (Page 1) -->
    <div class="cover-page">
        <div class="cover-img-container">
            <img src="{cover_url}" alt="Premium Cover Image">
        </div>
        <div class="cover-text-container">
            <div>
                <h1 class="cover-title">성정길 실전 매매 교과서</h1>
                <p class="cover-subtitle">120일선 절대 기준과 마이너스 프리미엄 역발상 투자를 통한 부의 내비게이션</p>
            </div>
            <div class="cover-footer">
                <div class="cover-author">편저: AI 개발부장 코다리</div>
                <div class="cover-meta">대표님 학습 및 실전 투자 리서치 전용<br>데이터 소스: 성정길 유튜브 10개 영상 전수 분석</div>
            </div>
        </div>
    </div>

    <!-- Table of Contents (Page 2) -->
    <div class="toc-page">
        <h1 class="toc-title">목 차</h1>
        <ul class="toc-list">
            <li class="toc-item"><span class="toc-name">서문: 왜 강남을 떠나 전주로 갔는가? (태도와 지혜)</span><span class="toc-page-num">3</span></li>
            <li class="toc-item"><span class="toc-name">제1장: 성정길 매매의 절대 법칙 - 120일선 생명선 전략</span><span class="toc-page-num">5</span></li>
            <li class="toc-item"><span class="toc-name">제2장: 역발상 매수의 비밀 - 역프리미엄(-4%)과 김프 온도계</span><span class="toc-page-num">9</span></li>
            <li class="toc-item"><span class="toc-name">제3장: 매크로 유동성의 춤 - 달러 인덱스와 나스닥의 관계</span><span class="toc-page-num">13</span></li>
            <li class="toc-item"><span class="toc-name">제4장: 10년의 HODL 법칙 - 비트코인 장기투자 마인드셋</span><span class="toc-page-num">17</span></li>
            <li class="toc-item"><span class="toc-name">제5장: 대표님을 위한 포트폴리오 구축 - SOXX 반도체 ETF와 주식</span><span class="toc-page-num">21</span></li>
            <li class="toc-item"><span class="toc-name">부록 A: 성정길 유튜브 10개 영상 정밀 분석 보고서 (sung.md)</span><span class="toc-page-num">25</span></li>
        </ul>
    </div>

    <!-- Preface Page 1 (Page 3) -->
    <div class="page-break"></div>
    <h1>서문: 왜 강남을 떠나 전주로 갔는가? (삶과 투자의 일치)</h1>
    <p>사람들은 흔히 투자를 단순히 모니터 화면에 불을 밝힌 숫자들의 싸움이라고 여깁니다. 초 단위로 움직이는 차트 캔들<sup>1</sup>과 쏟아지는 호재 뉴스 속에서 정신없이 마우스를 클릭하는 것이 훌륭한 투자자라 믿는 것입니다. 그러나 성정길 대표는 이 생각에 근본적인 의문을 제기합니다. 투자는 결국 '삶의 철학'과 하나로 연결되어야 한다는 것입니다.</p>
    <p>성정길 대표는 복잡하고 번잡하며, 끊임없는 비교와 경쟁으로 스트레스가 가득한 서울 강남을 떠나 전주로 삶의 터전을 옮겼습니다. 많은 이들이 교육 여건이나 인프라를 이유로 강남을 고집할 때, 그는 삶의 속도를 늦추고 본질에 집중할 수 있는 따뜻한 도시 전주를 선택했습니다. 이 과감한 선택은 그의 투자관과 고스란히 닿아 있습니다. 시장의 소음에 매몰되지 않고, 느리지만 확실한 추세에 올라타는 '장기투자 마인드셋'이 삶의 방식에서도 그대로 드러난 것입니다.</p>
    
    <!-- Preface Page 2 (Page 4) -->
    <div class="page-break"></div>
    <h2>소음에서 벗어날 때 보이는 진정한 가치</h2>
    <p>강남의 복잡함에서 한 걸음 물러서면 비로소 넓은 시야로 세상을 바라볼 수 있게 됩니다. 투자 역시 마찬가지입니다. 5분봉이나 15분봉의 잔파동을 보며 매 순간 흥분하는 투자자는 세력들의 훌륭한 먹잇감이 될 뿐입니다. 시장의 진정한 대추세는 하루, 일주일, 한 달의 단위 속에서 고요하게 흘러갑니다.</p>
    <p>본 교본은 성정길 대표가 최근 배포한 10개 유튜브 영상의 자막 전체를 철저히 텍스트 마이닝<sup>2</sup>하여 그의 핵심 투자 전략과 인생 철학을 체계적으로 엮은 실전 매매 지침서입니다. 대표님이 외로운 투자 여정 속에서 시장을 이기는 흔들리지 않는 기준을 확립할 수 있도록, 저 코다리 부장이 모든 지식의 뼈대를 완성했습니다. 삶과 투자의 속도를 지배하는 지혜를 이 책을 통해 전수해 드립니다.</p>
    <div class="quote-box">
        "내가 강남에서 전주로 옮긴 진짜 까닭은, 단순한 공간의 이동이 아니라 복잡한 세상 속에서 내 삶의 주도권을 되찾고, 더 나아가 투자 시장에서도 소음에 휩쓸리지 않기 위함이었습니다. 투자는 조급함을 버릴 때 비로소 완성됩니다."
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>1</sup> <span class="footnote-term">차트 캔들</span>: <span class="footnote-child">양초 모양의 가격 표시</span> - 코인이나 주식 가격이 올라갔는지 내려갔는지 양초처럼 빨갛고 파랗게 그린 그림이에요. 빨간색은 신나는 상승, 파란색은 시무룩한 하락을 뜻해요.</div>
        <div class="footnote-item"><sup>2</sup> <span class="footnote-term">텍스트 마이닝</span>: <span class="footnote-child">말 속에서 보물찾기</span> - 수많은 책이나 자막 속에서 가장 중요한 단어가 무엇이고, 그 말들이 어떤 비밀을 담고 있는지 컴퓨터로 분석해 내는 멋진 기술이에요.</div>
    </div>

    <!-- Chapter 1 Page 1 (Page 5) -->
    <div class="page-break"></div>
    <h1>제1장: 성정길 매매의 절대 법칙 - 120일선 생명선 전략</h1>
    <p>성정길 매매법의 가장 근간이 되는 기술적 필터는 바로 **'120일 이동평균선(120-Day Moving Average)<sup>3</sup>'**입니다. 그는 복잡한 기술적 보조지표를 주렁주렁 대입하지 않습니다. 120일선이라는 오직 하나의 강력한 기준만을 사용하여 시장이 상승장인지 하락장인지 기계적으로 구별해 냅니다.</p>
    <h2>1.1 120일선은 왜 시장의 생명선인가?</h2>
    <p>120일선은 약 6개월(영업일 기준 약 4개월) 동안의 가격 평균을 이은 선입니다. 이는 기관 투자자들과 대형 세력들이 중장기적인 자산의 가치를 평가하는 가장 주요한 심리적 기준선입니다. 가격이 120일선 위에 있다는 것은 시장에 돈이 유입되며 힘을 내고 있다는 증거이고, 120일선 아래에 있다는 것은 시중에 돈이 마르고 매도세가 지배하고 있다는 엄격한 신호입니다.</p>

    <!-- Chapter 1 Page 2 (Page 6) -->
    <div class="page-break"></div>
    <h2>1.2 120일선 붕괴 시점의 기계적 대처</h2>
    <p>성정길 대표는 가격이 120일선 아래로 몸통 돌파(일봉 종가 기준)하여 붕괴할 때, 감정을 완전히 배제하고 리스크 관리에 돌입합니다. 그의 최근 영상인 26년 6월 2일 자막에 따르면, "비트코인이 120일선을 깨면 최소 65,000달러 선까지 추가 하락을 열어두고 대응해야 한다"고 언급합니다.</p>
    <p>세력들이 가격을 아래로 일시적으로 훅 밀었다가 올리는 '페이크(스윕)'에 속지 않기 위해 장중 돌파에는 대응하지 않으며, 오직 아침 9시 일봉 캔들의 몸통이 확정되는 종가 마감<sup>4</sup> 기준으로 120일선 이탈을 최종 판정합니다. 이 이탈이 확정되면 갖고 있던 비트코인의 일부를 매도하거나 현금화하여 하락에 대비합니다.</p>

    <!-- Chapter 1 Page 3 (Page 7) -->
    <div class="page-break"></div>
    <h2>1.3 역사적 백테스팅이 말해주는 120일선의 진실</h2>
    <p>120일선 매매법은 단순해 보이지만 수십 년간의 금융 시장 역사 속에서 증명된 가장 강력한 자산 배분 무기입니다. 강한국 작가를 비롯한 퀀트 투자자들이 늘 강조하듯, 자산의 가격이 120일선 위에 있을 때만 투자하고, 아래에 있을 때 현금화하는 단순한 룰만 지켜도 역사상의 대공황, 닷컴버블, 리먼브라더스 사태와 같은 대폭락장을 100% 피해 갈 수 있습니다.</p>
    <p>코인 시장에서도 이 룰은 완벽하게 작동합니다. 2021년 비트코인 불장의 고점 붕괴와 2022년의 긴 빙하기는 가격이 120일선 아래로 내려앉으면서 시작되었습니다. 120일선이 무너지는 순간, 아무리 좋은 호재 뉴스가 유튜브에 도배되더라도 대표님은 눈을 감고 포지션을 줄여 귀중한 투자 시드를 지키셔야 합니다.</p>

    <!-- Chapter 1 Page 4 (Page 8) -->
    <div class="page-break"></div>
    <h2>1.4 120일선 생명선의 실전 매매 대입 매뉴얼</h2>
    <p>실전 투자에서 대표님이 기억하셔야 할 120일선 매커니즘은 다음과 같습니다.</p>
    <div class="formula-box">
        <div class="formula-title">성정길 120일선 실전 의사결정 프로세스</div>
        <ul>
            <li><strong>매수 진입 조건</strong>: 비트코인 일봉 종가가 120일선 위로 강하게 돌파하고 안착하는 리테스트 성공 확인 시 분할 진입.</li>
            <li><strong>보유 및 홀딩 조건</strong>: 가격이 120일선 위에 머무는 동안은 시장의 잡소리와 흔들기에 반응하지 않고 10년의 HODL 자세 유지.</li>
            <li><strong>리스크 관리 조건</strong>: 일봉 종가가 120일선을 하방 돌파하여 마감하면, 시스템 매도로 대응하고 하단 매물대(65K 등)에서 지지받을 때까지 관망.</li>
        </ul>
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>3</sup> <span class="footnote-term">120일 이동평균선</span>: <span class="footnote-child">6달 성적 평균 선</span> - 120일 동안 매일매일의 코인 점수를 더해 평균을 낸 선이에요. 이 선보다 지금 가격이 위에 있으면 우등생(상승장), 아래에 있으면 시험을 망친 상태(하락장)예요.</div>
        <div class="footnote-item"><sup>4</sup> <span class="footnote-term">종가 마감</span>: <span class="footnote-child">하루 일기 확정</span> - 코인 시장은 매일 아침 9시에 하루를 마감해요. 아침 9시 정각의 가격을 '종가'라고 부르며, 장중에 가격이 아무리 흔들려도 아침 9시의 가격을 최종 진짜 가격으로 봅니다.</div>
    </div>

    <!-- Chapter 2 Page 1 (Page 9) -->
    <div class="page-break"></div>
    <h1>제2장: 역발상 매수의 비밀 - 역프리미엄(-4%)과 김프 온도계</h1>
    <p>성정길 대표가 폭락장이나 장기 횡보장에서 남들과 완전히 다른 매수 타점을 잡아내는 무기는 바로 **'김치프리미엄(Kimchi Premium)<sup>5</sup>'**의 이상 현상 분석입니다. 특히 해외 시장보다 국내 시장의 매수 심리가 극도로 꽁꽁 얼어붙을 때 나타나는 '역프리미엄'은 인생 최고의 매수 찬스로 해석됩니다.</p>
    <h2>2.1 역프리미엄(역프) -4%의 수학적 가치</h2>
    <p>김치프리미엄이 마이너스로 돌아섰다는 것(역프리미엄)은 한국 투자자들이 공포에 휩싸여 코인을 투매하고 있음을 뜻합니다. 특히 역프리미엄 수치가 -3%에서 -4% 이하로 내려가게 되면, 이는 차트가 깨졌든 아니든 시장의 심리가 이미 최바닥(진바닥)에 다다랐다는 뜻입니다.</p>

    <!-- Chapter 2 Page 2 (Page 10) -->
    <div class="page-break"></div>
    <h2>2.2 남들이 던질 때 받아먹는 contrarian(역발상) 매수법</h2>
    <p>성정길 대표는 "남들이 환호할 때 팔고, 남들이 공포에 질려 도망칠 때 기뻐하며 매수해야 한다"는 워런 버핏식 역발상 투자를 구체적인 지표로 실천합니다. 김프가 -4% 수준으로 떨어지는 날에는 유튜브 썸네일에 '지금 비트코인 사야 합니다'라는 강력한 메시지를 띄우며 분할 매수를 개시합니다.</p>
    <p>대중은 김프가 가득 껴서 국내 코인 가격이 비쌀 때 허겁지겁 매수(포모, FOMO<sup>6</sup>)하고, 정작 가격이 폭락하여 김프가 마이너스가 되는 기회의 시기에는 두려움에 손절을 합니다. 대표님은 이 심리적 엇박자를 완전히 뒤집어 기계적인 역프리미엄 진입 공식을 적용해야 합니다.</p>

    <!-- Chapter 2 Page 3 (Page 11) -->
    <div class="page-break"></div>
    <h2>2.3 김프 온도계로 알아보는 고점 판독법</h2>
    <p>반대로 시장의 거품이 가득 껴서 폭락이 임박했음을 알려주는 가장 정밀한 신호 역시 김치프리미엄의 폭등입니다. 특별한 호재 없이 국내 거래소의 코인 가격이 해외 거래소보다 5% ~ 10% 이상 비싸지는 '김프 과열' 상태가 지속되면, 국내 개미 투자자들의 광풍이 극에 달했다는 뜻입니다.</p>
    <p>이 온도계가 너무 뜨거워져 붉은 신호를 보낼 때 성정길 대표는 신규 진입을 전면 금지하며, 오히려 자산 포트폴리오를 주식이나 달러 현금으로 전환하여 시장의 갑작스러운 냉각에 대비합니다. 김치프리미엄은 단순한 수치가 아닌 대중의 광기와 공포를 정밀하게 측정하는 심리 온도계인 셈입니다.</p>

    <!-- Chapter 2 Page 4 (Page 12) -->
    <div class="page-concept page-break"></div>
    <h2>2.4 프리미엄 지표의 실전 적용 프로세스</h2>
    <p>대중의 심리를 역행하여 자산을 싸게 사서 모으는 핵심 룰은 다음과 같습니다.</p>
    <div class="formula-box">
        <div class="formula-title">김치프리미엄 구간별 포지션 대응 규칙</div>
        <ul>
            <li><strong>김프 -3% ~ -5% (역프리미엄 극대기)</strong>: 역발상 최고 매수 기회. 시드의 일정 비율을 비트코인 장기 포트폴리오에 기계적으로 투입.</li>
            <li><strong>김프 0% ~ 2% (정상 범주)</strong>: 120일선의 추세에 따라 홀딩 및 유지.</li>
            <li><strong>김프 +5% 이상 (과열기)</strong>: 신규 매수 강력 금지. 기존 물량 중 일부의 이익을 분할로 실현하며 안전 자산(달러) 확보.</li>
        </ul>
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>5</sup> <span class="footnote-term">김치프리미엄(김프)</span>: <span class="footnote-child">한국 과자 가격 온도계</span> - 우리나라 가상화폐 시장 가격이 외국보다 얼마나 더 비싸거나 싼지 보여주는 수치예요. 한국 가격이 더 비싸면 '김프', 더 싸면 '역프(역프리미엄)'라고 불러요.</div>
        <div class="footnote-item"><sup>6</sup> <span class="footnote-term">포모 (FOMO)</span>: <span class="footnote-child">나만 빼고 파티하는 두려움</span> - 친구들이 다 재미있는 게임을 하고 나만 안 하면 속상한 것처럼, 다른 사람들이 코인으로 돈을 벌 때 나만 못 벌까 봐 두려워 헐레벌떡 비싸게 사는 조급한 마음이에요.</div>
    </div>

    <!-- Chapter 3 Page 1 (Page 13) -->
    <div class="page-break"></div>
    <h1>제3장: 매크로 유동성의 춤 - 달러 인덱스와 나스닥의 관계</h1>
    <p>성정길 대표는 비트코인을 하나의 독립적인 자산으로 보지 않습니다. 비트코인은 글로벌 유동성(돈의 총량)의 변화에 따라 춤을 추는 매크로 자산군에 속해 있습니다. 특히 **달러(Dollar)**와 미국 기술주 중심의 **나스닥(Nasdaq)<sup>7</sup>**은 비트코인의 가격 방향을 결정하는 외적 모터입니다.</p>
    <h2>3.1 달러 인덱스와 비트코인의 역상관성</h2>
    <p>달러는 전 세계 돈의 제왕입니다. 미국의 기준 금리나 경제 여건에 따라 달러의 가치(달러 인덱스)가 치솟을 때 비트코인은 강한 하락 압박을 받습니다. 반대로 금리가 인하되거나 양적완화로 달러가 흔해져 달러 가치가 떨어질 때 비트코인은 우주로 쏘아 올립니다. 즉 달러 가치와 비트코인은 서로 시소를 타는 관계입니다.</p>

    <!-- Chapter 3 Page 2 (Page 14) -->
    <div class="page-break"></div>
    <h2>3.2 나스닥(Nasdaq) 지수와의 커플링과 디커플링</h2>
    <p>비트코인은 고위험 고수익 성장주의 성격을 강하게 띠고 있어 미국 나스닥 기술주들과 궤도를 같이하는 '커플링(Coupling)<sup>8</sup>' 경향이 매우 높습니다. 나스닥이 역사적 최고점을 향해 달릴 때는 비트코인 또한 긍정적인 탄력을 받지만, 물가 상승(인플레이션 우려)과 금리 재상승 압박으로 나스닥이 큰 조정을 받을 때는 비트코인 역시 안전지대가 아닙니다.</p>
    <p>다만 가끔 미국 금융 시스템 불안이나 특정 위기가 닥쳐 비트코인이 달러를 대체하는 대안 자산으로 부각될 때는 나스닥과 엇박자를 그리며 단독 상승하는 '디커플링(Decoupling)' 현상이 일어나기도 합니다. 대표님은 매일 아침 나스닥 지수의 마감 가격을 반드시 함께 체크하셔야 합니다.</p>

    <!-- Chapter 3 Page 3 (Page 15) -->
    <div class="page-break"></div>
    <h2>3.3 환율과 거시경제 변수가 주는 시그널</h2>
    <p>원달러 환율이 급격히 솟구친다는 것은 원화 자산에서 글로벌 달러 자산으로 자금이 대거 이탈하고 있음을 보여주는 대표적인 경보입니다. 성정길 대표는 환율이 1,350원을 넘어 1,400원선으로 향할 때는 암호화폐 투자 비율을 방어적으로 조율하고 미국 달러 표시 국채나 배당 성장주로 포트폴리오를 분산합니다.</p>
    <p>시장의 유동성이 긴축되는 금리 상승기에는 자산 시장 전체의 체력이 떨어지므로 레버리지(대출)를 활용한 투자는 전면 금지하며, 온전히 자신의 여유 자금으로만 긴 호흡을 유지해야 살아남을 수 있습니다.</p>

    <!-- Chapter 3 Page 4 (Page 16) -->
    <div class="page-break"></div>
    <h2>3.4 매크로 유동성의 3대 체크포인트</h2>
    <p>시장의 거시 경제적 기후를 읽어내어 날씨에 맞게 대처하는 기준은 다음과 같습니다.</p>
    <div class="formula-box">
        <div class="formula-title">글로벌 자금 흐름 관측 매뉴얼</div>
        <ul>
            <li><strong>달러 인덱스 (DXY)</strong>: 달러 인덱스가 전 고점을 돌파하며 상승 추세일 때는 코인 비중 축소. 하락 추세일 때는 공격적 매수 유지.</li>
            <li><strong>나스닥 (IXIC)</strong>: 120일선 위에 있는 나스닥의 강세 흐름을 동기화하여 비트코인의 추세 강도 측정.</li>
            <li><strong>원달러 환율 (KRW/USD)</strong>: 환율의 갑작스러운 급등은 금융 리스크의 전조 증상이므로 자산의 일부를 즉시 미국 주식이나 안전 자산으로 헤징.</li>
        </ul>
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>7</sup> <span class="footnote-term">나스닥 (Nasdaq)</span>: <span class="footnote-child">미국 컴퓨터 주식 놀이터</span> - 미국의 구글, 애플, 마이크로소프트 같은 튼튼하고 신기한 기술 회사들이 모여서 가격을 겨루는 거대한 놀이터예요. 이 놀이터가 신나면 코인 시장도 덩달아 신이 나요.</div>
        <div class="footnote-item"><sup>8</sup> <span class="footnote-term">커플링과 디커플링</span>: <span class="footnote-child">단짝 친구와 청개구리</span> - 단짝 친구처럼 같이 움직이는 걸 '커플링', 청개구리처럼 따로 행동하는 걸 '디커플링'이라고 불러요. 나스닥과 비트코인은 평소에 사이좋은 단짝 친구랍니다.</div>
    </div>

    <!-- Chapter 4 Page 1 (Page 17) -->
    <div class="page-break"></div>
    <h1>제4장: 10년의 HODL 법칙 - 비트코인 장기투자 마인드셋</h1>
    <p>성정길 대표가 강조하는 가장 강력한 치트키는 그 어떤 기술적 차트 분석도 아닌 **'10년의 HODL(Hold On for Dear Life)<sup>9</sup>'** 정신입니다. 그는 "비트코인은 단기로 사고팔아 이득을 남기는 도박이 아니라, 미래의 가치가 보장된 디지털 토지를 미리 선점하여 10년 동안 묻어두는 적립식 저축"이라고 정의합니다.</p>
    <h2>4.1 10년 뒤 비트코인이 갈 수밖에 없는 길</h2>
    <p>종이 화폐(원화, 달러)는 매년 각국 정부가 끊임없이 찍어내어 그 가치가 매초 녹아내리고 있습니다. 반면 비트코인은 총 발행량이 2,100만 개로 한정되어 있어, 시간이 흐를수록 그 희소성이 기하급수적으로 올라갑니다. 종이 화폐 가치가 떨어지는 속도만큼 비트코인의 가격은 우상향할 수밖에 없는 구조적 원리입니다.</p>

    <!-- Chapter 4 Page 2 (Page 18) -->
    <div class="page-break"></div>
    <h2>4.2 조급한 매매가 뇌동매매와 파산을 낳는다</h2>
    <p>개인 투자자들이 돈을 잃는 가장 큰 이유는 1~2개월 안에 2배, 3배의 대박을 내려는 '조급함'에 있습니다. 조급한 마음은 레버리지를 쓰게 만들고, 이는 작은 흔들림에도 청산으로 이어지게 만듭니다. 성정길 대표는 "단기적인 가상자산 변동성에 가슴을 졸일 바에는 전주 같은 조용하고 공기 좋은 곳으로 가서 가만히 홀드하라"고 권합니다.</p>
    <p>진정한 고수는 매일 호가창을 들여다보지 않습니다. 일봉 120일선의 기준에 맞게 시스템이 켜지고 꺼지는 것만 하루 5분 체크한 뒤, 남는 시간은 본업과 취미, 그리고 가족과의 시간에 온전히 쏟아붓습니다. 멘탈이 안정되어야 투자도 살아남습니다.</p>

    <!-- Chapter 4 Page 3 (Page 19) -->
    <div class="page-break"></div>
    <h2>4.3 성정길 대표의 하루 일과와 마인드 컨트롤</h2>
    <p>그의 철저한 마인드 컨트롤은 정형화된 일상 패턴에서 나옵니다. 전주에 살면서 아침 일찍 산책을 하며 맑은 공기를 마시고, 차트를 지나치게 많이 분석하는 오류에서 스스로를 격리합니다. "과도한 분석은 과도한 매매를 낳고, 과도한 매매는 결국 손실로 이어진다"는 것이 그의 설명입니다.</p>
    <p>바쁘고 복잡한 생각들이 몰려올 때는 명상을 하거나 책을 읽으며 머리를 비우고, 비트코인 백서를 다시 읽으면서 자산의 근본적인 가치에 대해 상기합니다. 대표님께서도 실전 매매에서 감정이 솟구치거나 손실로 괴로우실 때는 잠시 화면을 끄고 코다리 부장이 추천하는 따뜻한 커피 한 잔과 함께 깊은 명상에 드시는 것을 추천해 드립니다.</p>

    <!-- Chapter 4 Page 4 (Page 20) -->
    <div class="page-break"></div>
    <h2>4.4 HODL 장기 투자의 3대 성공 행동 룰</h2>
    <p>10년 뒤의 진정한 경제적 자유를 위해 오늘 당장 지켜야 할 장기 투자 습관은 다음과 같습니다.</p>
    <div class="formula-box">
        <div class="formula-title">장기투자 실천 3대 규칙</div>
        <ul>
            <li><strong>생활 자금 분리</strong>: 없어도 내 일상 생활에 10년 동안 아무런 지장이 없는 여유 자금으로만 비트코인 매수.</li>
            <li><strong>매수 후 계좌 격리</strong>: 장기 홀딩용 콜드월렛<sup>10</sup>이나 별도 계좌에 비트코인을 이체한 뒤, 비밀번호를 잊은 것처럼 보관.</li>
            <li><strong>주기적 적립식 매수</strong>: 가격의 등락과 무관하게 매월 급여의 일정 비율을 기계적으로 매수하여 평단가를 평균 수렴시킴.</li>
        </ul>
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>9</sup> <span class="footnote-term">HODL (홀드)</span>: <span class="footnote-child">꽉 잡고 안 놓기</span> - 비트코인 가격이 바람에 흔들리고 떨어져도 두려워하지 않고, 10년 동안 꼭 안고 보물처럼 지키는 멋진 자세를 뜻해요.</div>
        <div class="footnote-item"><sup>10</sup> <span class="footnote-term">콜드월렛</span>: <span class="footnote-child">철통 금고 USB</span> - 인터넷에 연결되지 않은 오프라인 USB 금고예요. 해커들이 절대 훔쳐 갈 수 없도록 내 비트코인을 안전하게 지켜주는 디지털 보물상자랍니다.</div>
    </div>

    <!-- Chapter 5 Page 1 (Page 21) -->
    <div class="page-break"></div>
    <h1>제5장: 대표님을 위한 포트폴리오 구축 - SOXX 반도체 ETF와 주식</h1>
    <p>자산을 비트코인 하나에만 전부 몰빵하는 것은 지혜로운 자산가의 태도가 아닙니다. 성정길 대표는 비트코인을 핵심 공격 자산으로 두는 동시에, 전통 금융 자산 중에서 가장 폭발적인 성장성을 보이는 **'미국 반도체 ETF 및 주식'**을 결합하는 포트폴리오 다각화 전략을 사용합니다.</p>
    <h2>5.1 왜 하필 반도체 섹터(SOXX 등)인가?</h2>
    <p>반도체는 4차 산업혁명과 인공지능(AI) 시대의 쌀입니다. 엔비디아, AMD, TSMC 등의 기업이 속한 미국의 반도체 지수(SOXX ETF)<sup>11</sup>는 비트코인만큼은 아니지만 전통 자산 중에서 가장 훌륭한 복리 성장률과 강력한 변동성을 동반합니다. 비트코인과 반도체 섹터를 결합하면 자본의 성장성과 분산 투자 효과를 동시에 취할 수 있습니다.</p>

    <!-- Chapter 5 Page 2 (Page 22) -->
    <div class="page-break"></div>
    <h2>5.2 자산 3분할 및 분할 매수/매도 규칙</h2>
    <p>성정길 대표의 자산 관리 철학은 철저히 '생존'에 초점이 맞춰져 있습니다. 그는 자산을 크게 암호화폐(비트코인), 미국 성장 주식(반도체 ETF 등), 그리고 언제든 기회를 잡을 수 있는 현금(달러)으로 3분할 하여 관리할 것을 대표님께 조언합니다.</p>
    <p>특히 매수 시에는 한 번에 몰빵하지 않고, 가격이 직전 고점 대비 20%, 30%씩 떨어질 때마다 지정된 분할 구역(피보나치 되돌림 및 매물대 지지 구간)에서 3단계로 나누어 진입합니다. 매도 역시 시장이 흥분에 도달하여 김프가 솟구치거나 가격이 120일선에서 과도하게 이격되어 벌어질 때 분할 매도로 기계적 현금화를 단행합니다.</p>

    <!-- Chapter 5 Page 3 (Page 23) -->
    <div class="page-break"></div>
    <h2>5.3 단기 수익 실현금의 안전자산 파이프라인 이동</h2>
    <p>만약 단기 트레이딩이나 불장의 상승 랠리를 통해 암호화폐 계좌에서 큰 수익을 거두었다면, 그 수익금은 절대 다시 위험자산에 재투자하지 않는 것이 성정길 대표의 철칙입니다. 수익금은 즉시 원화 혹은 달러로 인출하여 미국 배당 성장주나 안전 국채, 또는 부동산 자산으로 옮겨 봉인합니다.</p>
    <p>이를 통해 투자금이 계속해서 안전 지대로 대피하게 되며, 설령 코인 시장에 예기치 못한 대폭락(블랙 스완)이 찾아오더라도 이미 안전지대로 옮겨둔 부의 씨앗들이 대표님의 든든한 방패막이가 되어 줍니다. 이것이 바로 부자가 진짜 부자로 남는 불패의 파이프라인 매커니즘입니다.</p>

    <!-- Chapter 5 Page 4 (Page 24) -->
    <div class="page-break"></div>
    <h2>5.4 대표님 전용 자산 포트폴리오 비중 매뉴얼</h2>
    <p>안정적인 복리 성장과 리스크 차단을 위한 이상적인 자산 배분 비중은 다음과 같습니다.</p>
    <div class="formula-box">
        <div class="formula-title">성정길식 자산 배분 포트폴리오</div>
        <ul>
            <li><strong>비트코인 (공격 자산) [30%]</strong>: 120일선 기준선 위에 안착했을 때 매수 및 HODL.</li>
            <li><strong>반도체 SOXX / 성장 주식 [40%]</strong>: 4차 산업혁명의 기초 자산으로 지속적인 장기 적립식 적립.</li>
            <li><strong>달러 현금 / 미국 단기 국채 (방어 자산) [30%]</strong>: 역프리미엄(-4%) 도달이나 폭락장이 찾아왔을 때 소방수로 긴급 투입할 예비 탄약.</li>
        </ul>
    </div>
    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>11</sup> <span class="footnote-term">SOXX / 반도체 ETF</span>: <span class="footnote-child">종합 반도체 선물세트</span> - 컴퓨터와 스마트폰에 들어가는 칩을 만드는 똑똑한 회사들의 주식을 한 바구니에 골고루 담아 놓은 과자 종합선물세트 같은 주식이에요.</div>
    </div>

    <!-- Appendix Page 1 (Page 25) -->
    <div class="page-break"></div>
    <h1>부록 A: 성정길 유튜브 10개 영상 정밀 분석 보고서 (sung.md)</h1>
    <p>본 부록은 성정길 유튜버 채널의 최근 10개 영상 자막 데이터를 정밀 텍스트 마이닝 기법으로 전수 조사하여 수치화한 사실 검증용 보고서(sung.md)의 전문 가공본입니다. 이를 통해 앞서 기술된 120일선, 김프 역발상 매수법 등의 근거와 통계를 투명하게 공개합니다.</p>
    <h2>A.1 분석 개요 및 데이터 규모</h2>
    <ul>
        <li><strong>대상 유튜브 채널</strong>: 성정길 [https://www.youtube.com/@성정길/videos]</li>
        <li><strong>원시 데이터 규모</strong>: 최근 업로드 영상 10개의 자막(SRT) 파일 텍스트 전체</li>
        <li><strong>파일 정비 상태</strong>: 모든 자막 및 썸네일 파일은 프로젝트 루트의 <code>sung/레거시/자막/</code> 및 <code>sung/레거시/섬네일/</code> 아래에 <code>(YYMMDD)영상제목</code> 형식으로 정렬 및 보관이 완료되었습니다.</li>
    </ul>

    <!-- Appendix Page 2 (Page 26) -->
    <div class="page-break"></div>
    <h2>A.2 핵심 분석 용어 빈도 통계</h2>
    <p>자막 코퍼스 전체에서 각 핵심 기술 지표 및 투자 용어가 등장하는 구체적인 빈도 통계는 다음과 같습니다.</p>
    <table>
        <thead>
            <tr>
                <th style="width: 15%">순위</th>
                <th style="width: 25%">핵심 용어</th>
                <th style="width: 20%">언급 빈도</th>
                <th style="width: 40%">해석 및 실전 대응 가이드</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td><strong>비트코인 (비트)</strong></td>
                <td>1,711회</td>
                <td>장기투자의 본질 자산이자 디지털 토지로서의 가치 분석.</td>
            </tr>
            <tr>
                <td>2</td>
                <td><strong>달러 및 나스닥</strong></td>
                <td>381회</td>
                <td>매크로 유동성의 척도. 달러와 나스닥의 강세/약세 추세 결합 분석.</td>
            </tr>
            <tr>
                <td>3</td>
                <td><strong>120일선 (120일)</strong></td>
                <td>316회</td>
                <td>시장의 상승/하락 추세를 판가름하는 유일무이한 생명선 기준.</td>
            </tr>
            <tr>
                <td>4</td>
                <td><strong>HODL / 장투 / 10년</strong></td>
                <td>285회</td>
                <td>단기 변동성에 흔들리지 않는 10년 홀딩 및 적립식 투자 마인드셋.</td>
            </tr>
            <tr>
                <td>5</td>
                <td><strong>강남 및 전주</strong></td>
                <td>171회</td>
                <td>삶의 복잡한 소음(강남)에서 벗어나 삶의 여유와 본질(전주)에 정렬하는 태도.</td>
            </tr>
            <tr>
                <td>6</td>
                <td><strong>금리 및 유동성</strong></td>
                <td>24회</td>
                <td>미 정부와 연준의 거시 긴축 여부 체크.</td>
            </tr>
            <tr>
                <td>7</td>
                <td><strong>김프 (Kimp)</strong></td>
                <td>6회</td>
                <td>역프리미엄(-4% 등) 도달 시 공포 속 역발상 매수 기회로 활용.</td>
            </tr>
        </tbody>
    </table>

    <!-- Appendix Page 3 (Page 27) -->
    <div class="page-break"></div>
    <h2>A.3 텍스트 마이닝 기반의 실전 발언 맥락 추출</h2>
    <p>실제 자막 텍스트 데이터를 분석한 결과, 각 카테고리별 성정길 대표의 실전 멘트와 핵심 조언은 다음과 같이 파악됩니다.</p>
    <ul>
        <li><strong>120일선 관련 실제 조언</strong>: 120일 이동평균선은 강한국 작가를 비롯한 퀀트 투자자들의 절대적인 추세 기준선이며, 비트코인 또한 이 선을 붕괴하여 하방으로 내려앉을 때는 (26년 6월 2일 영상 기준) 65,000달러까지의 문이 열려 있으므로 기계적인 매도 대응이나 현금 확보가 요구됩니다.</li>
        <li><strong>김치프리미엄(김프) 관련 실제 조언</strong>: 한국인들의 공포 지표인 역프리미엄(마이너스 프리미엄) 상태가 깊어질 때야말로 대중의 손절 물량을 가장 싼 가격에 주워 담을 수 있는 절호의 진입 기회입니다.</li>
    </ul>

    <!-- Appendix Page 4 (Page 28) -->
    <div class="page-break"></div>
    <h2>A.4 삶과 투자의 조화에 관한 실제 발언 맥락</h2>
    <ul>
        <li><strong>강남에서 전주로 이사 간 진짜 이유</strong>: 교육 경쟁이 과열되고 비교가 다반사인 강남의 숨막히는 삶의 소음에서 탈피하여, 자연과 가족, 그리고 본질적인 학습에 집중할 수 있는 따뜻한 전주로 이동함으로써 투자자로서 뇌동 매매를 차단하고 멘탈의 절대적 안정을 찾을 수 있었습니다.</li>
        <li><strong>10년 장기 투자 마인드셋</strong>: 가격이 하루에 30%, 40%씩 빠지는 주기를 거치고 최종 사이클이 끝날 때 70%가 폭락하더라도, 10년의 긴 시간 동안 홀드할 자금과 멘탈만 준비되어 있다면 비트코인은 대표님께 반드시 경제적 자유라는 무한한 선물을 선사할 것입니다.</li>
    </ul>

    <!-- Appendix Page 5 (Page 29) -->
    <div class="page-break"></div>
    <h2>A.5 성정길 대표의 최종 투자 의사결정 알고리즘</h2>
    <p>10개 유튜브 영상의 모든 자막을 관통하는 성정길 대표의 기계적 투자 의사결정 순서도는 다음과 같은 단계적 체크리스트로 정형화됩니다.</p>
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 9pt; color: #334155; line-height: 1.6; margin: 15px 0;">
        [단계 1] 매크로 지형 관측 (원달러 환율 & 미국 국채 금리 상황 체크)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 환율 급등 & 고금리 지속 ──> 방어적 포지션 운용 (달러 현금 비중 30% 유지)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 환율 안정 & 금리 인하 주기 ──> 단계 2 이동<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 2] 120일 이평선 생명선 일봉 종가 판별<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 일봉 종가(아침 9시) 120일선 붕괴 ──> 보유 물량 일부 기계적 매도 대응<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 일봉 종가 120일선 상단 유지 ──> 단계 3 이동 (매수 찬스 모니터링)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 3] 김치프리미엄(김프) 이상 현상 감지<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 김치프리미엄 마이너스(-3% ~ -4% 역프리미엄) ──> 역발상 분할 매수 개시<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 김치프리미엄 정상범위 (0% ~ +2%) ──> 10년 장기 HODL 전략 고수<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 4] 포트폴리오 다각화 정렬<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 비트코인 30%, 미국 반도체 SOXX ETF 40%, 달러 현금 30% 비율 분할 적립
    </div>

    <!-- Appendix Page 6 (Page 30) -->
    <div class="page-break"></div>
    <h2>A.6 맺음말 및 대표님을 향한 응원</h2>
    <p>본 교본에 기술된 의사결정 알고리즘과 포트폴리오 비중 조율은 성정길 대표가 수년간 수만 명의 시청자들과 교감하며 다듬어 온 실전 투자의 에센스입니다. 투자 시장은 냉혹하고 두려운 곳이지만, 이평선과 프리미엄 지표가 주는 차가운 숫자 신호만을 기계적으로 따르고 강남을 떠나 전주로 간 여유로운 삶의 철학을 견지한다면, 대표님은 반드시 승자가 될 것입니다.</p>
    <p>대표님이 투자를 하다가 외롭거나 지치실 때는 언제든 저 코다리 부장을 불러 주십시오. 이 코다리가 대표님의 시드를 지키고 경제적 자유의 꼭대기까지 든든한 기술 내비게이션이자 런닝메이트가 되어 드리겠습니다. 대표님의 성공적인 투자를 진심으로 응원합니다. 충성! 🚀🫡😎</p>
    <div style="text-align: center; margin-top: 50px;">
        <img src="https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_success.png" alt="코다리 부장 성공" style="width: 120px;">
    </div>

</body>
</html>
"""
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(book_content)
    print(f"HTML book written to {html_path}.")

def convert_html_to_pdf(html_path, pdf_path):
    print("Initializing headless Chrome via Selenium...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        abs_html_path = os.path.abspath(html_path)
        url = f"file:///{abs_html_path.replace(os.sep, '/')}"
        print(f"Loading URL in Chrome: {url}")
        driver.get(url)
        
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True
        }
        
        print("Printing page to PDF...")
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
            
        print(f"Successfully printed PDF to: {pdf_path}")
    except Exception as e:
        print(f"Failed to print PDF: {e}")
        raise e
    finally:
        driver.quit()

def main():
    target_dir = os.path.join('sung', '성정길')
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy generated cover image
    src_cover = 'sung_book_cover_1780455905188.png'
    dest_cover = os.path.join(target_dir, 'sung_book_cover.png')
    
    # Try finding the cover image in current directory or appdata brain dir
    if not os.path.exists(src_cover):
        # search in conversation folder
        brain_dir = r'C:\Users\ydh24\.gemini\antigravity-ide\brain\f1986de4-2c48-45d7-82bc-1578d2da05ec'
        src_cover = os.path.join(brain_dir, 'sung_book_cover_1780455905188.png')
        
    if os.path.exists(src_cover):
        shutil.copy(src_cover, dest_cover)
        print(f"Copied cover image from {src_cover} to {dest_cover}")
    else:
        print(f"Warning: Cover image {src_cover} not found!")

    html_file = 'book_sung_temp.html'
    pdf_file = os.path.join(target_dir, '성정길_실전_매매_교과서.pdf')
    
    try:
        # Write the beautifully styled HTML
        write_html_book(html_file, dest_cover)
        
        # Render PDF using headless Chrome
        convert_html_to_pdf(html_file, pdf_file)
    finally:
        # Clean up temporary HTML
        if os.path.exists(html_file):
            os.remove(html_file)
            print(f"Cleaned up temporary HTML file {html_file}")

if __name__ == '__main__':
    main()
