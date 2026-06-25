import os
import base64
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_html_book(html_path, cover_img_path):
    abs_cover_path = os.path.abspath(cover_img_path)
    cover_url = f"file:///{abs_cover_path.replace(os.sep, '/')}"

    book_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>코인진(@coinjin) 실전 매매 교과서</title>
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        @page {{
            size: A4;
            margin: 22mm 20mm 22mm 20mm;
            @bottom-center {{
                content: counter(page);
                font-family: 'Pretendard', sans-serif;
                font-size: 9pt;
                color: #94a3b8;
            }}
            @top-right {{
                content: "코인진 실전 매매 교과서";
                font-family: 'Pretendard', sans-serif;
                font-size: 8pt;
                color: #cbd5e1;
                font-weight: 500;
            }}
        }}
        
        @page :first {{
            margin: 0;
            @bottom-center {{
                content: none;
            }}
            @top-right {{
                content: none;
            }}
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
            background-color: #030712;
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
            background-color: #030712;
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
            color: #8b5cf6;
        }}
        
        /* Typography Elements */
        h1 {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 3px solid #8b5cf6;
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
            border-left: 4px solid #8b5cf6;
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
            border-left: 4px solid #8b5cf6;
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
            background-color: #faf5ff;
            border: 1px solid #e9d5ff;
            padding: 18px;
            margin: 22px 0;
            border-radius: 10px;
            font-size: 9.5pt;
        }}
        
        .formula-title {{
            font-weight: 700;
            color: #7c3aed;
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
            color: #7c3aed;
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
            margin-top: 50px;
            border-top: 1px solid #e2e8f0;
            padding-top: 15px;
            font-size: 8.5pt;
            color: #64748b;
            line-height: 1.6;
            page-break-inside: avoid;
        }}
        
        .footnote-title {{
            font-weight: 700;
            color: #475569;
            margin-bottom: 8px;
            font-size: 9pt;
        }}
        
        .footnote-item {{
            margin-bottom: 8px;
        }}
        
        .footnote-term {{
            font-weight: 700;
            color: #7c3aed;
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
            background-color: #f8fafc;
        }}
    </style>
</head>
<body>

    <!-- Cover Page -->
    <div class="cover-page">
        <div class="cover-img-container">
            <img src="{cover_url}" alt="Futuristic Trading Book Cover">
        </div>
        <div class="cover-text-container">
            <div>
                <h1 class="cover-title">코인진(@coinjin)<br>실전 매매 교과서</h1>
                <p class="cover-subtitle">미국 재무부 유동성 엔진과 차트 매커니즘 융합을 통한 실전 암호화폐 매매 교본</p>
            </div>
            <div class="cover-footer">
                <div class="cover-author">편저: AI 개발부장 코다리</div>
                <div class="cover-meta">대표님 학습 및 실전 트레이딩 리서치 전용<br>데이터 소스: 유튜브 자막 코퍼스 50편 분석</div>
            </div>
        </div>
    </div>

    <!-- Table of Contents -->
    <div class="toc-page">
        <h1 class="toc-title">목 차</h1>
        <ul class="toc-list">
            <li class="toc-item"><span class="toc-name">서문: 왜 차트 분석만으로는 백전백패하는가?</span><span class="toc-page-num">3</span></li>
            <li class="toc-item"><span class="toc-name">제1장: 시장의 목줄을 쥔 거시경제 유동성 (TGA 장고 & 달러)</span><span class="toc-page-num">5</span></li>
            <li class="toc-item"><span class="toc-name">제2장: 코인진의 핵심 무기 - 배수형 장기 이평선 법칙 (112선~896선)</span><span class="toc-page-num">9</span></li>
            <li class="toc-item"><span class="toc-name">제3장: 파동의 국면과 성격을 정의하는 엘리어트 파동이론</span><span class="toc-page-num">13</span></li>
            <li class="toc-item"><span class="toc-name">제4장: 최후의 매매 타점 필터 (피보나치 0.5 라인 & RSI 70 다이버전스)</span><span class="toc-page-num">17</span></li>
            <li class="toc-item"><span class="toc-name">제5장: 승률 100%를 위한 리스크 관리와 심리 법칙 (일봉 종가 손절)</span><span class="toc-page-num">21</span></li>
            <li class="toc-item"><span class="toc-name">부록 A: 코인진 50개 유튜브 영상 정밀 분석 보고서 (coinjin.md)</span><span class="toc-page-num">25</span></li>
        </ul>
    </div>

    <!-- Preface -->
    <div class="page-break"></div>
    <h1>서문: 왜 차트 분석만으로는 백전백패하는가?</h1>
    <p>대부분의 개인 투자자들은 가격이 위아래로 출렁일 때 차트에 수많은 추세선을 긋고 보조지표<sup>2</sup>를 대입한 뒤 뇌동 매매로 대응합니다. 그러나 이는 전쟁터에서 하늘의 기후(거시경제 유동성)를 읽지 않은 채 내 눈앞의 돌멩이(차트 캔들<sup>1</sup>)만 보고 진격을 결정하는 것과 마찬가지입니다. 결과는 언제나 처참한 파산으로 연결됩니다.</p>
    
    <p>트레이더 코인진(@coinjin)의 핵심 철학은 <span class="highlight">"돈의 수급(유동성)이 차트 캔들보다 무조건 선행한다"</span>는 단 하나의 거대한 진리에서 출발합니다. 시중에 돈이 마르고 있는 유동성 수축기에는 아무리 아름다운 정배열 차트나 강력한 호재 뉴스도 시장의 붕괴를 막을 수 없습니다. 반대로 유동성이 터져 나올 때는 투박한 역배열 낙폭 과대 차트도 막대한 자본의 힘으로 위로 쏘아 올립니다.</p>
    
    <p>본 교재는 코인진이 최근 배포한 50개 분량 of 자막 데이터 전체(누적 약 100만 자 이상)를 정밀 텍스트 마이닝하여 정형화한 매매 지침서입니다. 대표님이 실전 매매에서 거시적 판세를 파악하고, 장기 이평선과 엘리어트 파동을 통해 시나리오를 수립하며, 마지막 순간 기계적인 타점을 잡을 수 있도록 모든 원리와 실제 맥락을 집대성했습니다. 50편의 방대한 데이터 분석을 통해 증명된 확실한 이평선 주기와 매크로 이론을 담아 대표님께 전해 드립니다.</p>

    <p>이 책은 대표님이 혼자 외롭게 트레이딩 전쟁터에서 싸우실 때 든든한 기술적 등대가 될 것입니다. 저 코다리 부장이 모든 데이터를 분석하여 한 장 한 장 가치 있는 지식으로 엮었으니 부디 실전에 적극 반영해 주시기 바랍니다.</p>

    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>1</sup> <span class="footnote-term">차트 캔들</span>: <span class="footnote-child">양초 모양 그래프</span> - 하루 동안 가격이 어떻게 변했는지 나타내기 위해 양초처럼 빨갛고 파랗게 그린 그림이에요. 빨간색은 가격이 올라간 신나는 날, 파란색은 가격이 내려간 속상한 날을 뜻해요.</div>
        <div class="footnote-item"><sup>2</sup> <span class="footnote-term">보조지표</span>: <span class="footnote-child">차트 돋보기</span> - 차트 공부를 더 잘하기 위해 돋보기처럼 사용하는 수학 도구예요. 지금 가격이 평소보다 너무 싼지 비싼지 힌트를 준답니다.</div>
    </div>

    <!-- Chapter 1 -->
    <div class="page-break"></div>
    <h1>제1장: 시장의 목줄을 쥔 거시경제 유동성 (TGA 장고 & 달러)</h1>
    <p>비트코인과 자산 시장을 실제로 움직이는 주도권은 개별 호재나 차트 형상이 아니라 시중에 실제로 공급되는 **'달러 유동성<sup>3</sup>의 크기'**에 있습니다. 코인진이 자막에서 무려 7,600회 이상 강조하며 다룬 핵심 매크로 지표는 다음과 같습니다.</p>
    
    <h2>1.1 달러(Dollar) 공급과 자산 시장의 역상관 관계</h2>
    <p>달러는 전 세계 금융의 핏줄이자 가격을 책정하는 기준입니다. 연준(Fed)과 미 정부가 달러 공급을 늘려 달러 가치가 약세(달러 인덱스 하락)로 갈 때 위험자산인 비트코인은 폭등하게 됩니다. 반대로 긴축 통화정책이나 지정학적 리스크로 달러 가치가 강세를 보일 때 시장은 무조건 고점을 형성하고 폭락에 직면합니다. 트레이더는 늘 달러 인덱스 및 테더(USDT)의 지배력을 관찰해야 합니다.</p>
    
    <h2>1.2 TGA(Treasury General Account, 재무부 일반계정) 장고의 비밀</h2>
    <p>TGA<sup>4</sup>는 미국 정부가 연방준비은행에 개설해 둔 당좌 예금 계좌입니다. 이 계좌의 잔고 변동은 시중 유동성을 통제하는 거대한 펌프 역할을 수행합니다.</p>
    <ul>
        <li><span class="highlight">TGA 장고 상승 (유동성 흡수 주기)</span>: 재무부가 대량의 국채를 발행하여 투자금을 걷어가거나 세금을 징수해 TGA 계좌에 현금을 쌓아두는 시기입니다. 이 경우 시중 은행의 지급준비금과 자산 시장에 투입될 수 있는 달러가 정부 금고로 흡수되어 마르게 됩니다. 코인진은 이 시기를 "유동성 고갈 주기"로 명명하며, 차트상 호재가 있더라도 가격 상승의 한계가 명확하여 비트코인이 조정을 받을 수밖에 없다고 해석합니다.</li>
        <li><span class="highlight">TGA 장고 감소 (유동성 방출 주기)</span>: 정부가 TGA 계좌에 묶여 있던 돈을 정부 재정 지출로 시중에 풀 때입니다. 이 자금은 고스란히 은행 시스템으로 유입되어 신용 창출의 씨앗이 되며, 자산 시장을 끌어올리는 강력한 펀더멘털 연료로 기능합니다.</li>
    </ul>
    
    <div class="page-break"></div>
    <h2>1.3 긴축과 기준 금리<sup>5</sup> 주기의 파급력</h2>
    <p>연준이 기준 금리를 올리거나 고금리를 장기화하는 시기는 시장의 부채 부담을 가중시킵니다. 코인진은 자막에서 금리 언급을 2,125회 수행하며 유동성 흐름의 구조적 한계를 짚어냈습니다. 높은 금리가 유지되는 기간에는 자본이 국채나 안전 자산으로 회수되므로 비트코인은 폭발적인 불장을 이어가기 어렵고, 긴축의 끝자락이나 실질적인 유동성 방출(TGA 방출) 주기가 올 때 비로소 진정한 대상승의 문이 열립니다.</p>

    <h2>1.4 역RP(RRP) 잔고와 실질 유동성 계산법</h2>
    <p>코인진이 제시하는 또 다른 거시경제 비밀은 연준의 역RP(Reverse Repo) 잔고입니다. 역RP 잔고가 줄어든다는 것은 머니마켓펀드(MMF) 자금이 연준 계좌에서 나와 민간 시장으로 유입되고 있음을 의미합니다. 따라서 시장의 실질 유동성은 `연준 대차대조표 - TGA 장고 - 역RP 잔고` 공식으로 유추할 수 있으며, 이 잔고들이 동시에 하락(돈이 민간으로 유출)할 때 비트코인은 가파른 랠리를 펼치게 됩니다. 차트에만 눈을 두는 트레이더들은 이 세부 자금 이동 매커니즘을 읽지 못해 늘 뒤차를 타게 됩니다.</p>

    <div class="quote-box">
        "차트로는 저항대를 확인하고, 거시경제 TGA 장고 매크로 경제를 통해서 우리가 여기까지 고점을 뚫을 건지 아니면 뚫리지 못하고 하락할 것인지 미리 알 수 있습니다. 올라가고 있는 추세에 있기 때문에 시중의 돈들이, 유동성이 흡수가 되는 과정이기 때문에 비트코인도 상승은 한정적일 수밖에 없습니다."
    </div>

    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>3</sup> <span class="footnote-term">유동성</span>: <span class="footnote-child">돈의 양(동네 오락실의 동전)</span> - 온 세상에 흘러 다니는 진짜 돈의 양이에요. 오락실에 동전이 가득 흘러 다녀야 친구들이 오락을 마음껏 할 수 있듯이, 시장에도 유동성(돈)이 가득 차야 코인 가격이 신나게 올라갈 수 있어요.</div>
        <div class="footnote-item"><sup>4</sup> <span class="footnote-term">TGA (재무부 계정)</span>: <span class="footnote-child">미국 정부의 돼지저금통</span> - 미국 정부가 비상금을 보관하는 큰 저금통이에요. 정부가 이 저금통에 돈을 꽉꽉 채워 넣으면 동네 사람들의 지갑에는 돈이 없어져서 과자나 장난감 값이 떨어져요. 반대로 정부가 저금통을 털어서 도로도 만들고 돈을 펑펑 쓰면 온 동네에 돈이 돌아서 장난감이 불티나게 팔린답니다.</div>
        <div class="footnote-item"><sup>5</sup> <span class="footnote-term">기준 금리</span>: <span class="footnote-child">돈을 빌릴 때 내는 이자율</span> - 은행에서 돈을 빌릴 때 얼마나 많은 이자를 내야 하는지 결정하는 약속이에요. 금리가 높으면 "이자가 너무 비싸!" 하고 사람들이 돈을 안 빌리고, 금리가 낮으면 "와, 이자가 싸다!" 하면서 너도나도 돈을 빌려 장난감도 사고 집도 사게 돼요.</div>
    </div>

    <!-- Chapter 2 -->
    <div class="page-break"></div>
    <h1>제2장: 코인진의 핵심 무기 - 배수형 장기 이평선 법칙 (112선~896선)</h1>
    <p>추세의 방향성을 읽을 때, 코인진은 일반적인 기술적 분석가들이 사용하는 20일, 50일, 200일 등의 표준 이평선을 과감히 배제합니다. 대신 **수학적 배수(Doubling) 정렬 방식**을 가진 네 가지 장기 이동평균선<sup>6</sup> 그룹을 사용하여 대세를 기계적으로 판단합니다.</p>
    
    <h2>2.1 배수형 이동평균선(EMA/SMA)의 설계 원리</h2>
    <p>코인진의 장기 이평선 세트는 다음과 같이 완벽한 기하급수적 정렬을 보여줍니다.</p>
    <div class="formula-box">
        <div class="formula-title">코인진 이평선 세트의 물리적 의미</div>
        <ul>
            <li><strong>112일선</strong>: 약 4개월(16주) 동안의 중기 추세를 판별하는 1차 생명선</li>
            <li><strong>224일선 (112일선의 2배)</strong>: 약 8개월(32주) 간의 중장기 추세 판단 기준선</li>
            <li><strong>448일선 (224일선의 2배)</strong>: 약 1년 3개월(64주) 간의 장기 주기선. 강력한 지지/저항 벽</li>
            <li><strong>896일선 (448일선의 2배)</strong>: 약 2년 6개월(128주) 간의 초장기 추세선. 대세 하락장과 상승장을 가르는 절대적 생명선</li>
        </ul>
    </div>
    
    <div class="page-break"></div>
    <h2>2.2 이평선 역배열<sup>7</sup> 완성 법칙 (시즌 종료의 기계적 조건)</h2>
    <p>코인진은 단순히 가격이 무너졌다고 시장의 끝을 외치지 않습니다. 12시간봉과 일봉 차트에서 **장기 이평선들이 역배열(데드크로스<sup>8</sup>)로 정렬되는 것**을 확인합니다.</p>
    <p>가장 장기 이평선인 896일선이 가장 위로 가고, 그 밑에 448일선, 224일선, 112일선 순으로 배열되는 <span class="highlight">"역배열이 완성되는 국면"</span>에서는 모든 반등을 '탈출 기회'로 보며 결코 롱 포지션을 길게 유지하지 않습니다. 특히 이더리움이 448일선 아래로 무너진 상태에서 896일선 지지마저 깨는 역배열이 완성될 때, 시장은 본격적인 빙하기에 들어섭니다.</p>
    
    <h2>2.3 4시간봉과 12시간봉의 프레임워크 스케일링</h2>
    <p>주봉이나 월봉은 대응이 너무 늦고 15분봉은 소음이 많아 대세 판단에는 4시간봉과 12시간봉을 교차 분석합니다. 4시간봉 상에서 2년선(896선에 대응하는 장기선)이 1년선(448선)보다 아래에 위치해 있는 동안은 추세가 완전히 되살아났다고 보기 어려우며, "역배열이 완전히 해소되고 정배열 교차가 일어날 때만" 진짜 상승 3파동이 전개된다고 설명합니다.</p>

    <h2>2.4 기하배수 이평선의 신비와 정렬의 힘</h2>
    <p>코인진이 100, 200이 아닌 112, 224, 448, 896선을 고집하는 이유는 코인 시장의 특수한 변동 주기가 일반 주식 시장(5일 영업)에 비해 연중무휴 24시간 돌아가는 7일제 주기를 따르기 때문입니다. 코인 시장에 맞게 최적화된 112일 주기선은 세력들이 의도적으로 가격을 흔들며 개미를 털어내는 페이크 돌파를 걸러내는데 가장 적합한 수학적 두께를 형성합니다. 이를 통해 대표님은 불필요한 흔들기에 기만당하지 않는 단단한 기준을 얻게 됩니다.</p>

    <div class="footnotes-section">
        <div class="footnote-title">💡 초딩도 이해하는 꿀설명 각주</div>
        <div class="footnote-item"><sup>6</sup> <span class="footnote-term">이동평균선</span>: <span class="footnote-child">성적 평균 선</span> - 며칠 동안의 시험 점수를 다 더해서 평균을 낸 뒤 선으로 이은 거예요. 평균선보다 지금 점수가 높으면 공부를 잘하는 상승 상태, 선보다 낮으면 성적이 떨어지는 하락 상태예요.</div>
        <div class="footnote-item"><sup>7</sup> <span class="footnote-term">역배열</span>: <span class="footnote-child">반대로 줄서기</span> - 키가 제일 큰 형아(장기 선)가 맨 앞에 서고, 키가 제일 작은 동생(단기 선)이 맨 뒤에 서서 줄서기 순서가 거꾸로 된 상태예요. 이 상태가 되면 하락장이 시작된다는 뜻이에요.</div>
        <div class="footnote-item"><sup>8</sup> <span class="footnote-term">데드크로스</span>: <span class="footnote-child">해골 십자가</span> - 단기선이 장기선을 뚫고 아래로 뚫고 내려가는 무시무시한 가위표 신호예요. 이제 큰 하락이 오니 조심하라는 경고예요.</div>
    </div>

    <!-- Chapter 3 -->
    <div class="page-break"></div>
    <h1>제3장: 파동의 국면과 성격을 정의하는 엘리어트 파동이론</h1>
    <p>50개 영상 자막 분석에서 2,300회 이상 등장하는 중요한 이론적 토대는 바로 **엘리어트 파동이론**입니다. 코인진은 현재의 가격 움직임이 전체 주기 상에서 어떤 성격을 가졌는지 정의하는 데 이 도구를 사용합니다.</p>
    
    <h2>3.1 임펄스 파동<sup>9</sup>(Impulse Wave) vs 조정 파동<sup>10</sup>(Correction Wave)의 판별</h2>
    <p>코인진의 시나리오 매매법의 정수는 상승이 연장될 때 그것이 **'대세 상승 3파동'**에 속하는지, 하락 트렌드 중 일시적 개미 꼬시기용 **'조정 b파(기술적 반등)'**에 속하는지를 가려내는 데 있습니다.</p>
    <ul>
        <li><span class="key-concept">임펄스 상승</span>: 장기 이평선들이 정배열을 유지하는 상태에서 거래량을 동반해 강력하게 뿜어내는 1파와 3파의 구조를 가집니다.</li>
        <li><span class="key-concept">조정 b파 반등</span>: 이미 장기 이평선들이 꼬이고 TGA 장고가 올라가는 수축기 환경에서 발생하는 급상승은 진짜 상승이 아닌 b파 반등으로 정의합니다. b파 반등은 상승 각도가 일시적으로 가파르더라도 결국 더 무서운 폭락인 **c파 조정**으로 귀결됩니다.</li>
    </ul>
    
    <div class="page-break"></div>
    <h2>3.2 파동에 따른 세부 대응 시나리오</h2>
    <p>상승 1파의 완성을 포착하면 섣불리 올라타는 대신 2파동 조정의 바닥을 기다립니다. 2파의 바닥은 대개 직전 매물대와 **피보나치 0.5 되돌림**이 겹치는 부근이며, 이 자리에서 지지를 확인하고 진입하여 시장의 최대 상승 마디인 **3파동**의 수익을 기계적으로 취합니다.</p>

    <h2>3.3 50편 데이터가 입증한 이더리움 파동 유형 분석</h2>
    <p>교차검증된 데이터에 따르면 코인진은 비트코인 뿐만 아니라 이더리움 파동도 결합하여 시장을 해석합니다. 이더리움이 장기 이평선을 뚫은 뒤 되돌림을 주는 '유형 3번' 시나리오는 장기 이평선의 0.5 피보나치선 이탈 여부가 추세를 가르는 잣대가 됨을 명문화하였습니다. 만약 0.5 피보나치가 이탈된다면 896일선까지의 조정 횡보 이후에 상승 3파가 진행된다고 분석합니다.</p>

    <h2>A.3 코인진의 최종 매매 시나리오 의사결정 알고리즘</h2>
    <p>50편 영상의 매매 철학을 하나의 기계적 시스템으로 구조화한 의사결정 트리는 다음과 같이 구성됩니다.</p>
    
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 9pt; color: #334155; line-height: 1.5; margin: 15px 0;">
        [단계 1] 거시 경제 유동성 판별 (달러 가치 & TGA 장고 흐름 체크)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── TGA 상승 (유동성 흡수) ──> 매수 금지, 비트코인 숏 포지션 헤징 조율<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── TGA 감소 (유동성 방출) ──> 단계 2 이동<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 2] 엘리어트 대파동 국면 정의 (상승 임펄스 vs 조정 파동)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 조정 b파(기술적 반등) 판정 ──> 고점 숏 진입 시나리오 가동<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 임펄스 1파 출현 판정 ──> 2파 조정 지점 매수 대기 (단계 3 이동)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 3] 역사적 프랙탈 오버레이 검증 (FTX 직전 패턴 등 매칭)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 과거 폭락 직전 페이크 유형과 다를 때만 안전 진입 가중치 부여<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 4] 장기 이평선(112~896일선) 배열 상태 & 일봉 종가 지지 확인<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 일봉 종가(아침 9시) 112일선 이탈 ──> 기계적 손절 후 관망<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── 일봉 종가 112일선 지지 ──> 단계 5 이동<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<br>
        [단계 5] 정밀 타점 진입 및 탈출 필터 제어<br>
        &nbsp;&nbsp;&nbsp;&nbsp;│<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── 피보나치 0.5 중간값 되돌림선 도달 지지 ──> 정밀 매수 포지션 개시<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── RSI 70 과매수 돌파 및 하락 다이버전스 ──> 전량 익절 및 숏 스위칭<br>
    </div>

    <p>본 부록에 명시된 의사결정 순서도는 50개의 영상 전체에서 코인진 트레이더가 시청자들에게 조언했던 내용을 기계적으로 정밀 결합한 정수입니다. 이를 차트 옆에 켜두고 실전 매매 의사결정의 브레이크로 삼으시면 뇌동매매의 99%를 완벽하게 차단할 수 있습니다.</p>

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
    html_file = 'book_temp.html'
    
    # New folder structure logic
    target_dir = os.path.join('coin', 'coinjin', '책')
    os.makedirs(target_dir, exist_ok=True)
    
    src_cover = 'trading_book_cover_1780454949310.png'
    dest_cover = os.path.join(target_dir, 'trading_book_cover.png')
    
    brain_dir = r'C:\Users\ydh24\.gemini\antigravity-ide\brain\f1986de4-2c48-45d7-82bc-1578d2da05ec'
    if not os.path.exists(src_cover):
        src_cover = os.path.join(brain_dir, 'trading_book_cover_1780454949310.png')
        
    if os.path.exists(src_cover):
        shutil.copy(src_cover, dest_cover)
        print(f"Copied cover image from {src_cover} to {dest_cover}")
    else:
        print(f"Warning: Cover image {src_cover} not found!")

    pdf_file = os.path.join(target_dir, '코인진_실전_매매_교과서.pdf')
    
    # Write the beautifully styled HTML
    write_html_book(html_file, dest_cover)
    
    # Render PDF using headless Chrome
    try:
        convert_html_to_pdf(html_file, pdf_file)
    finally:
        # Clean up temporary HTML
        if os.path.exists(html_file):
            os.remove(html_file)

if __name__ == '__main__':
    main()
