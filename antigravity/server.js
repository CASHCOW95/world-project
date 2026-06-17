import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GoogleGenerativeAI } from '@google/generative-ai';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import fs from 'fs';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// 포털 메인 및 빌드된 리액트 워크스페이스 정적 웹 호스팅 서비스 추가
app.use('/workspace', express.static(path.join(__dirname, '../web_dashboard/workspace')));
app.use('/output', express.static(path.join(__dirname, '../web_dashboard/output')));
app.use(express.static(path.join(__dirname, '../web_dashboard')));

// Model 1: Simulated SaaS Credit Database in memory
let userCredits = 5;

// Clean technical jargon helper
const jargonMap = {
  "포스팅": "블로그 글 쓰기",
  "백링크": "추천 링크 연결",
  "트래픽": "방문자 유입",
  "아웃라인": "글의 목차 구조",
  "H2/H3": "대주제와 소주제",
  "API": "연동 도구",
  "파이프라인": "자동화 순서",
  "파싱": "내용 추출",
  "빌드": "만들기 / 구축",
  "데이터베이스": "저장소"
};

function cleanJargon(text) {
  let cleaned = text;
  for (const [eng, kor] of Object.entries(jargonMap)) {
    const regex = new RegExp(eng, 'gi');
    cleaned = cleaned.replace(regex, kor);
  }
  return cleaned;
}

// Endpoint to check current credits
app.get('/api/credits', (req, res) => {
  res.json({ credits: userCredits });
});

// Endpoint to reset credits for demo
app.post('/api/credits/reset', (req, res) => {
  userCredits = 5;
  res.json({ credits: userCredits });
});

// Endpoint for Styler Pro text generation
app.post('/api/generate', async (req, res) => {
  const { keyword, style, length, platform } = req.body;

  if (!keyword) {
    return res.status(400).json({ error: '키워드를 입력해 주십시오.' });
  }

  // Model 1 credit check
  if (userCredits <= 0) {
    return res.status(402).json({ 
      error: '보유하신 크레딧이 부족합니다. (SaaS 요금제 결제 또는 크레딧 충전이 필요합니다.)' 
    });
  }

  // Decrement credit for this generation
  userCredits -= 1;

  const apiKey = process.env.GEMINI_API_KEY;
  
  // FALLBACK: If API key is missing, generate a beautiful mock Styler Pro article
  if (!apiKey || apiKey.trim() === '') {
    console.warn("GEMINI_API_KEY is missing. Generating high-quality mock article as fallback.");
    
    // Simulate generation delay
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    const mockTitle = `[안내] ${keyword} 실전 가이드 & 마스터 바이블`;
    const mockContent = `
<div style="background-color: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 20px; margin-bottom: 25px;">
  <strong>💡 안내메시지:</strong> 현재 환경설정파일(.env)에 API 키가 설정되지 않아, 데모 버전의 가상 템플릿 글을 보여드립니다. API 키를 등록하시면 실제 인공지능이 생성한 무제한 글 쓰기가 수행됩니다.
</div>

<div class="article_header" style="margin-bottom: 25px; border-bottom: 2px solid #334155; padding-bottom: 15px;">
  <span style="font-size: 11px; background-color: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 8px;">산업분석</span>
  <span style="color: #64748b; font-size: 11px;">작성일: 2026-06-13</span>
</div>

<p>안녕하세요! 오늘 소개해 드릴 주제는 바로 최근 디지털 비즈니스 영역에서 가장 뜨거운 관심을 받고 있는 <strong>${keyword}</strong>랍니다. 비전공자나 일반 독자분들도 한눈에 이해하실 수 있도록 풍부한 기업 사례와 구체적인 미래 전망을 엮어 입체적으로 분석해 보았어요. 끝까지 천천히 읽어보시면 분명 새로운 통찰력을 얻어가실 수 있을 것이라 기대돼요 🚀</p>

<!-- 1. 목차 디자인 -->
<div class="toc-container" style="background-color:#F8E8EE; border:2px solid #000; border-radius:8px; max-width:85%; margin:20px auto; padding: 20px; box-shadow:0 0 15px rgba(255,105,180,0.8); transition:0.3s;">
  <strong style="font-size: 1.1em; display: block; margin-bottom: 10px; color: #000;">📋 목차</strong>
  <ul style="list-style-type: none; padding-left: 0; margin-bottom: 0; line-height: 1.8;">
    <li><a href="#section-1" style="color: #000; text-decoration: none; font-weight: bold;">🎯 1. 개요 및 ${keyword}의 정의</a></li>
    <li><a href="#section-2" style="color: #000; text-decoration: none; font-weight: bold;">🏭 2. 주요 산업별 영향 분석</a></li>
    <li><a href="#section-3" style="color: #000; text-decoration: none; font-weight: bold;">📊 3. 시장 변화 트렌드 및 기회 요인</a></li>
    <li><a href="#section-4" style="color: #000; text-decoration: none; font-weight: bold;">💻 4. 디지털 영향 및 핵심 비즈니스 모델</a></li>
    <li><a href="#section-5" style="color: #000; text-decoration: none; font-weight: bold;">📈 5. 전망 및 주요 기업 대응 사례</a></li>
    <li><a href="#section-6" style="color: #000; text-decoration: none; font-weight: bold;">💰 6. 수혜 산업군 심층 비교</a></li>
    <li><a href="#section-7" style="color: #000; text-decoration: none; font-weight: bold;">🔮 7. 미래 예측 (1년~10년 스케줄)</a></li>
    <li><a href="#section-8" style="color: #000; text-decoration: none; font-weight: bold;">❓ 8. 가장 자주 묻는 FAQ 모음</a></li>
  </ul>
</div>

<!-- 2. H2 개요 및 본문 -->
<h2 id="section-1" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">🎯 1. 개요 및 ${keyword}의 정의</h2>
<p>개인적으로는 ${keyword} 현상을 관찰할 때마다 기술의 대중화 속도에 정말 감탄하게 된답니다. 실제로 네이버나 카카오 같은 국내 대형 테크 기업들은 물론이고, 구글과 오픈AI 같은 글로벌 플랫폼들도 이 방향을 매우 주목하고 있어요. 생각보다 영향이 크기 때문에, 초기 진입 전략을 어떻게 짜는지가 매우 중요해요 ✨</p>
<p>과거에는 전문 개발 지식을 가진 집단이 기술을 독점했다면, 이제는 비전공자 일반인들도 쉽게 자동화 도구를 엮어 비즈니스를 개척하는 시대가 도래했답니다. 이러한 변화 흐름 속에서 기회를 잡는 리더만이 장기적으로 큰 수익을 낼 수 있을 전망이에요 🌟</p>

<!-- Table 1 -->
<h3 style="margin-top:15px; font-weight:bold; color:#1e293b;">📊 표 1. 단기 / 중기 / 장기 관점 변화</h3>
<table class="apple-table" style="width:100%; border-collapse:collapse; text-align:center; margin:15px 0;">
  <thead>
    <tr style="background-color:#a7eecf;">
      <th style="border:1px solid #000; padding:8px;">시기</th>
      <th style="border:1px solid #000; padding:8px;">예상 시장 규모</th>
      <th style="border:1px solid #000; padding:8px;">주요 트렌드</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">단기 (1년 이내)</td>
      <td style="border:1px solid #000; padding:8px;">소폭 상승</td>
      <td style="border:1px solid #000; padding:8px;">기초 지식 습득 및 템플릿 검증 위주</td>
    </tr>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">중기 (3년 이내)</td>
      <td style="border:1px solid #000; padding:8px;">대폭 성장</td>
      <td style="border:1px solid #000; padding:8px;">대규모 무인 자동 발행 시스템 대중화</td>
    </tr>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">장기 (5년 이상)</td>
      <td style="border:1px solid #000; padding:8px;">시장의 안정기</td>
      <td style="border:1px solid #000; padding:8px;">인간의 개입이 최소화된 완전 무인화 안착</td>
    </tr>
  </tbody>
</table>

<h2 id="section-2" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">🏭 2. 주요 산업별 영향 분석</h2>
<p>흥미로운 부분은 쿠팡이나 배달의민족 같은 리테일 플랫폼들이 ${keyword}를 통해 마케팅 비용을 엄청나게 절감하고 있다는 점이랍니다. 상품 노출을 사람이 직접 타이핑하지 않고 인공지능이 키워드를 정밀 타격하여 대량으로 발행하고 있어요. 눈여겨볼 점은 이러한 기술적 변화가 특정 집단의 이익이 아니라 시장 전반의 파이를 키우고 있다는 점이에요 ✨</p>

<!-- Table 2 -->
<h3 style="margin-top:15px; font-weight:bold; color:#1e293b;">🏭 표 2. 산업별 영향 및 기업 대응 전략</h3>
<table class="apple-table" style="width:100%; border-collapse:collapse; text-align:center; margin:15px 0;">
  <thead>
    <tr style="background-color:#a7eecf;">
      <th style="border:1px solid #000; padding:8px;">산업 분야</th>
      <th style="border:1px solid #000; padding:8px;">영향 범위</th>
      <th style="border:1px solid #000; padding:8px;">대응 방안</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">이커머스</td>
      <td style="border:1px solid #000; padding:8px;">광고 소재 무한 생성</td>
      <td style="border:1px solid #000; padding:8px;">추천 링크 연결(백링크) 자동 배포</td>
    </tr>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">미디어</td>
      <td style="border:1px solid #000; padding:8px;">기사 요약 및 재생성</td>
      <td style="border:1px solid #000; padding:8px;">다국어 자동 실시간 번역 발행</td>
    </tr>
  </tbody>
</table>

<h2 id="section-3" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">📊 3. 시장 변화 트렌드 및 기회 요인</h2>
<p>제 생각에는 향후 개인화 검색 노출 영역이 구글이나 네이버에서 가장 중요한 승부처가 될 것 같아요. 실제로 장기적으로 보면 정교한 검색엔진 최적화(SEO) 구조를 가진 글들이 계속해서 상위를 독점하게 된답니다. 체류시간을 오래 묶어두는 양질의 콘텐츠만이 수익형 블로그의 근원적인 자산이 될 전망이에요 🌟</p>

<!-- Table 3 -->
<h3 style="margin-top:15px; font-weight:bold; color:#1e293b;">📊 표 3. 시장 구분별 기회 및 위험요소</h3>
<table class="apple-table" style="width:100%; border-collapse:collapse; text-align:center; margin:15px 0;">
  <thead>
    <tr style="background-color:#a7eecf;">
      <th style="border:1px solid #000; padding:8px;">구분</th>
      <th style="border:1px solid #000; padding:8px;">기회 (Opportunity)</th>
      <th style="border:1px solid #000; padding:8px;">위험 (Threat)</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">신규 진입자</td>
      <td style="border:1px solid #000; padding:8px;">초기 비용 없이 대량 유입 채널 확보</td>
      <td style="border:1px solid #000; padding:8px;">유사 사이트 과열로 인한 클릭 단가 하락</td>
    </tr>
  </tbody>
</table>

<h2 id="section-4" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">💻 4. 디지털 영향 및 핵심 비즈니스 모델</h2>
<p>실제로 업계에서는 이미 다수의 1인 지식 창업자들이 코딩 없이 노코드로 웹 앱을 만들고 있어요. 넷플릭스나 메타가 유저 맞춤형으로 콘텐츠 피드를 다듬어주는 것과 동일한 원리로, 우리도 블로그 방문자의 동선을 제어하여 CTR(클릭율)을 극대화할 수 있답니다. 이것이 수익 자동화를 만드는 핵심 비즈니스 모델이에요 🚀</p>

<!-- Table 4 -->
<h3 style="margin-top:15px; font-weight:bold; color:#1e293b;">💻 표 4. 애드센스 적용 방식 및 효과</h3>
<table class="apple-table" style="width:100%; border-collapse:collapse; text-align:center; margin:15px 0;">
  <thead>
    <tr style="background-color:#a7eecf;">
      <th style="border:1px solid #000; padding:8px;">비즈니스 요소</th>
      <th style="border:1px solid #000; padding:8px;">적용 모델</th>
      <th style="border:1px solid #000; padding:8px;">기대 효과</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">애드센스 연동</td>
      <td style="border:1px solid #000; padding:8px;">전면 및 일치하는 광고 동적 배치</td>
      <td style="border:1px solid #000; padding:8px;">페이지뷰당 단가(RPM) 상승</td>
    </tr>
  </tbody>
</table>

<h2 id="section-5" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">📈 5. 전망 및 주요 기업 대응 사례</h2>
<p>삼성과 LG 등 전통 제조 대기업들도 최근 사내 인프라에 독자적인 초거대 인공지능 구축을 추진 중이랍니다. 회사 내부 문서 보안 문제도 있고, 업무 생산성 도구로 바로바로 메일이나 제안서를 쓰기 위함이에요. 우리 1인 기업가들도 똑같아요. 우리만의 스타일러 프로 무인 집필 엔진을 구축해서 앞서가는 전략이 절대적으로 중요해요 ✨</p>

<!-- Table 5 -->
<h3 style="margin-top:15px; font-weight:bold; color:#1e293b;">📈 표 5. 주요 빅테크 기업 대응 및 시사점</h3>
<table class="apple-table" style="width:100%; border-collapse:collapse; text-align:center; margin:15px 0;">
  <thead>
    <tr style="background-color:#a7eecf;">
      <th style="border:1px solid #000; padding:8px;">주요 대기업</th>
      <th style="border:1px solid #000; padding:8px;">대응 방향성</th>
      <th style="border:1px solid #000; padding:8px;">시사점</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#e0f8e8;">
      <td style="border:1px solid #000; padding:8px; font-weight:bold;">네이버/카카오</td>
      <td style="border:1px solid #000; padding:8px;">한국어 특화 생성 모델 고도화</td>
      <td style="border:1px solid #000; padding:8px;">검색 상위 노출 기준 충족 용이</td>
    </tr>
  </tbody>
</table>

<h2 id="section-6" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">💰 6. 수혜 산업군 심층 비교</h2>
<p>지속 가능한 블로그 성장을 위해서는 추천 링크(백링크) 품질 관리가 절대적으로 요구된답니다. 지식인 답변이나 타 사이트의 연관 키워드에 내 블로그의 유익한 글 링크를 걸어주면 양질의 방문자 유입이 늘어나요. 긍정적인 사이클이 돌면서 사이트 지수가 올라가고 더 많은 키워드들이 동시에 상위 노출에 포진하게 될 기회가 기대돼요 🚀</p>

<h2 id="section-7" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">🔮 7. 미래 예측 (1년~10년 스케줄)</h2>
<p>미래 타임라인별로 이 분야의 변천사를 예측해 보면 아래와 같이 정리할 수 있어요.</p>
<ul>
  <li><strong>향후 1년 이내</strong>: 검색 엔진이 생성 인공지능 글에 대해 엄격한 기준을 들이대지만, 용어 순화 필터를 탑재한 스텔스 스타일 원고는 여전히 안정적인 수익을 거둡니다.</li>
  <li><strong>향후 3년 이내</strong>: 고도화된 멀티모달 기술이 적용되어, 단 한 번의 클릭만으로 이미지, 영상, 오디오까지 포함된 완벽한 블로그 글이 알아서 포스팅됩니다.</li>
  <li><strong>향후 5년 이내</strong>: 개인 맞춤형 인공지능 에이전트 비서들이 사용자를 대신해 인터넷 검색을 하고 정보를 모으므로, 블로그 유입 경로가 에이전트 추천형으로 개편될 전망이에요.</li>
  <li><strong>향후 10년 이내</strong>: 메타버스와 가상 현실 내에서 개인 블로그 정보들이 홀로그램 데이터베이스로 작동하며 지식 생태계가 완전 무인화에 안착할 것으로 보여요.</li>
</ul>

<h2 id="section-8" style="color:#000000; font-size:20px; font-weight:bold; background-color:#ffd8a8; padding:10px; border-radius:5px; margin-top: 25px;">❓ 8. 가장 자주 묻는 FAQ 모음</h2>
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin: 15px 0;">
  <p><b>Q1. ${keyword} 수익자동화 구축에 초기 비용이 많이 드나요?</b><br>
  A1. 처음에는 구글 개발자 센터에서 주는 무료 사용 한도 범위만 써도 한 푼도 내지 않고 무제한으로 테스트해 보실 수 있답니다.</p>
  <p><b>Q2. 상위 노출을 위해 가장 중요한 것은 무엇인가요?</b><br>
  A2. 방문자가 내 글에 오래 머물러 읽을 수 있도록 풍부한 표와 정교한 FAQ, 목차 등의 구조를 적용해 가독성을 높이는 것이 핵심이에요.</p>
  <p><b>Q3. 인공지능이 생성한 글인 것이 검색엔진에 걸려 불이익을 받지 않나요?</b><br>
  A3. 보고서체나 신문체 같은 딱딱한 툴 냄새를 걷어내고, "제 생각에는"처럼 자연스러운 일상적 어투를 섞어 용어를 완벽히 순화해 주면 회피가 가능해요.</p>
  <p><b>Q4. 플랫폼마다 작성 양식을 다르게 해야 하나요?</b><br>
  A4. 네, 카카오 티스토리와 워드프레스 등 각 플랫폼에 맞는 맞춤형 HTML 코드로 최적화해서 적용하는 것이 상위 노출에 매우 중요해요.</p>
  <p><b>Q5. 추천 링크(백링크)는 어떻게 만들어가나요?</b><br>
  A5. 외부 카페나 커뮤니티, 지식인 등에 방문자들이 정말 궁금해하는 문제를 해결해 주고 내 글의 단축 주소를 정돈해 첨부하면 자연스럽게 쌓여가요.</p>
  <p><b>Q6. 애드센스 승인 신청용으로 사용해도 되나요?</b><br>
  A6. 네, 본문의 길이(최소 1,500자 이상)와 풍부한 텍스트 깊이를 확보하여 승인 규격에 맞춰 대량 발행하면 승인 난이도를 크게 대폭 낮출 수 있어요.</p>
  <p><b>Q7. 초장문(5,000자 이상) 글이 왜 상위 노출에 유리한가요?</b><br>
  A7. 정보의 밀도가 높으면 검색 엔진 봇이 글의 완성도를 높게 보기도 하고, 방문자가 목차를 보고 클릭하며 스크롤하므로 체류 시간이 엄청 길어지기 때문이에요.</p>
  <p><b>Q8. 일반인 비전공자도 당장 바로 시작할 수 있을까요?</b><br>
  A8. 그럼요! 복잡한 개발 기술이나 서버 연동은 스타일러 프로 중계 시스템이 뒷단에서 전부 대행해 주므로 대표님은 클릭 한 번으로 시작하실 수 있어요.</p>
</div>

<!-- 면책 조항 -->
<div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; font-size: 14px; color: #666; margin: 20px 0; line-height: 1.6;">
  <strong>💡 면책 조항 (Disclaimer):</strong> 본 블로그 글은 특정 종목 추천이나 투자 유도 목적이 아니며, 최신 시장 트렌드 데이터와 사용자의 키워드 정보를 기반으로 자동 작성된 분석형 요약 정보 자료입니다. 실제 실행 및 적용에 따른 모든 최종적 판단과 책임은 사용자 본인에게 있습니다.
</div>

<!-- CTA 배너 -->
<div class="cta-banner" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; text-align: center; color: white; margin-top: 30px; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);">
  <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: bold; color: white;">🎯 지금 바로 더 상세한 혜택을 확인해보세요!</h3>
  <p style="margin: 0 0 15px 0; font-size: 13px; opacity: 0.9;">${keyword} 관련 무료 분석 계산기 및 정부 지원 정책 신청 바로가기 링크를 제공해 드립니다. 놓치면 평생 손해!</p>
  <a href="#toc-container" style="background: white; color: #764ba2; border-radius: 50px; padding: 10px 25px; font-weight: bold; display: inline-block; text-decoration: none; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transition: 0.2s;">👉 수혜주 분석 및 지원금 바로 확인하기</a>
</div>
    `.trim();

    return res.json({
      title: mockTitle,
      html_content: mockContent,
      tags: [keyword, "수익자동화", "실전가이드", "기초마스터"],
      credits_left: userCredits,
      demo: true
    });
  }

  // Real LLM flow using Gemini SDK
  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    // Use gemini-1.5-flash for speed and low cost
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    // Tone and style specifications
    let styleInstruction = "";
    if (style === "friendly") {
      styleInstruction = "친근하고 상냥한 대화체(해요체)로, 독자에게 바로 옆에서 이야기하듯 구체적인 조언을 섞어서 글을 쓰십시오.";
    } else if (style === "professional") {
      styleInstruction = "신뢰감 있고 논리 정연하며 품격 있는 문체(하십시오체)로 작성하며, 사실 관계를 명확히 짚고 분석적인 관점을 제시하십시오.";
    } else {
      styleInstruction = "정보 제공에 집중하여 간결하고 가독성 높은 리스트와 요약 문장들을 고르게 사용하여 깔끔하게 정리해 주십시오.";
    }

    // Length specifications
    let lengthInstruction = "";
    if (length === "short") {
      lengthInstruction = "약 1,500자 분량";
    } else if (length === "long") {
      lengthInstruction = "약 3,000자 분량의 장문";
    } else if (length === "extra-long") {
      lengthInstruction = "약 5,000자 분량의 아주 상세하고 깊이 있는 초장문 (각 장마다 구체적이고 바로 적용 가능한 행동 지침과 상세 예시를 충분히 덧붙여서 매우 풍부하게 작성해 주십시오)";
    } else {
      lengthInstruction = "약 1,500자 분량";
    }

    const prompt = `
당신은 구글 상위 노출에 최적화된 국내 최고의 전문 글 집필 전문가(Styler Pro)입니다.
다음 주제에 맞춰 블로그 원고를 완전한 HTML 형식으로 작성해 주십시오.

[주제 키워드]: ${keyword}
[대상 플랫폼]: ${platform === "tistory" ? "카카오 티스토리" : platform === "blogspot" ? "구글 블로그스팟" : "개인 워드프레스"}
[작성 스타일]: ${styleInstruction}
[목표 분량]: ${lengthInstruction}

[반드시 준수해야 할 작성 및 HTML 스타일 가이드라인]
1. 제목: 글의 맨 처음에 어울리는 매혹적인 제목을 한 줄 작성하고, 이를 JSON의 "title" 키값에 담으십시오. 본문 HTML 안에는 H1 태그를 포함하지 마십시오.
2. 용어 순화 (기술 외래어 및 전문 용어 금지):
   - '포스팅'이라는 단어는 반드시 '블로그 글 쓰기' 혹은 '글 작성'으로 순화하십시오.
   - '백링크'는 '추천 링크 연결' 혹은 '외부 링크 연결'로 순화하십시오.
   - '트래픽'은 '방문자 유입'으로 순화하십시오.
   - '아웃라인'은 '글의 목차 구조'로 순화하십시오.
   - 'H2/H3'는 '대주제와 소주제'로 순화하십시오.
   - 'API'는 '연동 도구'로 순화하십시오.
   - '파이프라인'은 '자동화 순서'로 순화하십시오.
   - '파싱'은 '내용 추출'로 순화하십시오.
   - '빌드'는 '만들기 / 구축'으로 순화하십시오.
   - '데이터베이스'는 '저장소'로 순화하십시오.
3. 목차 제공: 본문 시작 지점에 이쁜 목차 박스(Table of Contents)를 HTML 코드 링크 형식(<a href="#sec-1"> 등)으로 작성하여 클릭 시 이동할 수 있게 설계하십시오.
4. 제목 태그 구조화: 대주제는 <h2 id="sec-1">, 소주제는 <h3 id="sub-1"> 태그를 활용해 정돈하십시오.
5. 인라인 스타일 적용:
   - 정보 박스: <div style="background-color: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 20px; margin-bottom: 25px;">내용</div>
   - 강조 알림(꿀팁): <div style="background-color: #fffbeb; border-left: 4px solid #d97706; padding: 10px 15px; border-radius: 4px; margin: 10px 0; color: #b45309; font-weight: 600;">내용</div>
   - 파란색 하이라이트 배지: <span style="background-color: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #bfdbfe; font-size: 0.85em; display: inline-block; margin: 2px;">단어</span>
   - 본문 하단 요약 박스 (꿀팁):
     <div style="background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 18px; border-radius: 8px; margin: 25px 0;">
       <strong style="color: #15803d; font-size: 1.1em; display: block; margin-bottom: 10px;">💡 [꿀팁]</strong>
       <span style="color: #166534; font-weight: 500; line-height: 1.7;">
         <strong>🎯 핵심 요약:</strong> 요약내용<br>
         <strong>⚙️ 벤치마킹 적용:</strong> 적용방안<br>
         <strong>🔄 작업 순서:</strong> 작업순서
       </span>
     </div>
6. 태그 추천: 글 하단에 해시태그 형식으로 넣기 좋은 태그 목록 4개를 도출하십시오.

[출력 형식 제한]
반드시 아래와 같은 JSON 구조로만 응답해야 하며, 그 외의 불필요한 설명글이나 백틱(\`\`\`json) 기호 등은 포함하지 말고 순수 JSON 문자열만 반환하십시오.

{
  "title": "SEO 최적화된 글 제목",
  "html_content": "HTML 본문 코드 내용 (마크다운이 아닌 완전한 HTML 코드)",
  "tags": ["태그1", "태그2", "태그3", "태그4"]
}
`.trim();

    const result = await model.generateContent(prompt);
    let rawResponse = result.response.text().trim();
    
    // Strip markdown formatting if AI outputs it
    if (rawResponse.startsWith("```")) {
      rawResponse = rawResponse.replace(/^```json\s*/i, "").replace(/```$/, "").trim();
    }

    const parsed = JSON.parse(rawResponse);
    
    // Safety check & jargon cleaning
    const cleanedTitle = cleanJargon(parsed.title || `[글] ${keyword}`);
    const cleanedHtml = cleanJargon(parsed.html_content || `<p>${keyword} 관련 본문이 생성되지 않았습니다.</p>`);
    const cleanedTags = (parsed.tags || [keyword]).map(t => cleanJargon(t));

    res.json({
      title: cleanedTitle,
      html_content: cleanedHtml,
      tags: cleanedTags,
      credits_left: userCredits,
      demo: false
    });

  } catch (error) {
    console.error("Gemini API call failed:", error);
    res.status(500).json({ 
      error: '인공지능 서비스 요청 처리 중 오류가 발생했습니다.', 
      details: error.message 
    });
  }
});

// 0. GET /api/categories
app.get('/api/categories', (req, res) => {
  const categoriesPath = path.join(__dirname, 'core/styler_pro_engine/categories.json');
  try {
    const data = fs.readFileSync(categoriesPath, 'utf8');
    res.json(JSON.parse(data));
  } catch (err) {
    console.error("Failed to read categories.json:", err);
    res.status(500).json({ error: "카테고리 정보를 로드할 수 없습니다." });
  }
});

// 1. GET /api/keywords
app.get('/api/keywords', (req, res) => {
  const { category } = req.query;
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/keyword_finder.py');
  
  const py = spawn(pythonPath, [scriptPath, category || '생활']);
  let stdoutData = '';
  let stderrData = '';
  
  py.stdout.on('data', (data) => {
    stdoutData += data.toString();
  });
  
  py.stderr.on('data', (data) => {
    stderrData += data.toString();
  });
  
  py.on('close', (code) => {
    if (code !== 0) {
      console.error(`Keyword analyzer crashed: ${stderrData}`);
      return res.status(500).json({ error: '키워드 분석기 실행 실패', details: stderrData });
    }
    try {
      const parsed = JSON.parse(stdoutData);
      res.json(parsed);
    } catch (err) {
      res.status(500).json({ error: 'JSON 파싱 실패', details: err.message, raw: stdoutData });
    }
  });
});

// 1.5 POST /api/generate-titles
app.post('/api/generate-titles', (req, res) => {
  const { keyword, category } = req.body;
  if (!keyword) {
    return res.status(400).json({ error: "키워드는 필수 입력값입니다." });
  }
  
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/title_generator.py');
  
  const py = spawn(pythonPath, [scriptPath, '--keyword', keyword, '--category', category || '정부지원금']);
  let stdoutData = '';
  let stderrData = '';
  
  py.stdout.on('data', (data) => {
    stdoutData += data.toString();
  });
  
  py.stderr.on('data', (data) => {
    stderrData += data.toString();
  });
  
  py.on('close', (code) => {
    if (code !== 0) {
      console.error(`Title generator crashed with code ${code}: ${stderrData}`);
      return res.status(500).json({ error: '제목 생성기 작동 중 에러 발생', details: stderrData });
    }
    
    const jsonMatch = stdoutData.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
    if (jsonMatch && jsonMatch[1]) {
      try {
        const parsed = JSON.parse(jsonMatch[1].trim());
        res.json(parsed);
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 오류', details: err.message, raw: stdoutData });
      }
    } else {
      res.status(500).json({ error: '결과 데이터 마커 누락' });
    }
  });
});

// 2. GET /api/history
app.get('/api/history', (req, res) => {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/db.py');
  
  const py = spawn(pythonPath, [scriptPath, '--history']);
  let stdoutData = '';
  let stderrData = '';
  
  py.stdout.on('data', (data) => {
    stdoutData += data.toString();
  });
  
  py.stderr.on('data', (data) => {
    stderrData += data.toString();
  });
  
  py.on('close', (code) => {
    if (code !== 0) {
      console.error(`DB history crashed: ${stderrData}`);
      return res.status(500).json({ error: '발행 이력 로드 실패', details: stderrData });
    }
    try {
      const parsed = JSON.parse(stdoutData);
      res.json(parsed);
    } catch (err) {
      res.status(500).json({ error: 'JSON 파싱 실패', details: err.message });
    }
  });
});

// 3. POST /api/publish-pipeline (Streaming log via chunked SSE)
app.post('/api/publish-pipeline', (req, res) => {
  const { keyword, platform, style, search_volume, competition, cpc, category, cta_style, golden_score, length, faq_count, img_prompt, title, seo_strength, publish } = req.body;
  
  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });

  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/main.py');
  
  const args = [
    scriptPath,
    '--keyword', keyword,
    '--platform', platform || 'tistory',
    '--style', style || 'friendly',
    '--search_volume', String(search_volume || 10000),
    '--competition', String(competition || 5000),
    '--cpc', cpc || '보통',
    '--category', category || '생활',
    '--cta_style', cta_style || 'card',
    '--golden_score', String(golden_score || 80),
    '--length', String(length || '5000'),
    '--faq_count', String(faq_count || '10'),
    '--img_prompt', String(img_prompt || 'OFF'),
    '--title', title || '',
    '--seo_strength', seo_strength || 'strong',
    '--publish', publish ? 'ON' : 'OFF'
  ];



  const py = spawn(pythonPath, args);
  let stdoutData = '';
  
  py.stdout.on('data', (data) => {
    const chunk = data.toString();
    stdoutData += chunk;
    
    const lines = chunk.split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        res.write(`data: ${JSON.stringify({ log: line.trim() })}\n\n`);
      }
    });
  });

  py.stderr.on('data', (data) => {
    const errLine = data.toString().trim();
    console.error(`[Python Engine Error] ${errLine}`);
    res.write(`data: ${JSON.stringify({ log: `⚠️ [에러] ${errLine}` })}\n\n`);
  });

  py.on('close', (code) => {
    if (code !== 0) {
      res.write(`data: ${JSON.stringify({ error: '파이프라인 프로세스 비정상 종료' })}\n\n`);
      res.end();
      return;
    }
    
    const jsonMatch = stdoutData.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
    if (jsonMatch && jsonMatch[1]) {
      try {
        const finalJson = JSON.parse(jsonMatch[1].trim());
        res.write(`data: ${JSON.stringify({ success: true, result: finalJson })}\n\n`);
      } catch (err) {
        res.write(`data: ${JSON.stringify({ error: '최종 결과 데이터 파싱 오류', raw: jsonMatch[1] })}\n\n`);
      }
    } else {
      res.write(`data: ${JSON.stringify({ error: '최종 결과 데이터 마커 누락' })}\n\n`);
    }
    res.end();
  });
});

// 4. GET /api/export-download (ZIP compression and download of exported assets)
app.get('/api/export-download', (req, res) => {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const outputDir = path.join(__dirname, 'web_dashboard/output');
  const zipPath = path.join(__dirname, 'web_dashboard/styler_pro_export.zip');

  // Python code block to zip the output directory recursively
  const zipCmd = `
import zipfile, os
zip_path = r"${zipPath.replace(/\\/g, '\\\\')}"
output_dir = r"${outputDir.replace(/\\/g, '\\\\')}"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, output_dir)
            zipf.write(file_path, arcname)
`.trim().replace(/\r?\n/g, '; ');

  const py = spawn(pythonPath, ['-c', zipCmd]);

  py.on('close', (code) => {
    if (code !== 0) {
      console.error(`Zip creation failed with exit code ${code}`);
      return res.status(500).json({ error: 'Zip 압축 파일 생성 중 에러가 발생했습니다.' });
    }
    
    res.download(zipPath, 'styler_pro_export.zip', (err) => {
      if (err) {
        console.error('Download error:', err);
      }
      // Clean up the temporary zip file
      try {
        fs.unlinkSync(zipPath);
      } catch (e) {
        console.error('Failed to delete zip file:', e);
      }
    });
  });
});

// ═══════════════════════════════════════════════════════
// V2 API: AI 블로그 운영 에이전트 신규 엔드포인트
// ═══════════════════════════════════════════════════════

// 5. POST /api/cluster-generate — 클러스터 구조 미리보기 생성
app.post('/api/cluster-generate', (req, res) => {
  const { keyword, category, min_subs, max_subs } = req.body;
  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/cluster_engine.py');

  const args = [scriptPath, '--keyword', keyword, '--category', category || '정보형'];
  if (min_subs) args.push('--min-subs', String(min_subs));
  if (max_subs) args.push('--max-subs', String(max_subs));

  const py = spawn(pythonPath, args);
  let stdoutData = '';
  let stderrData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.stderr.on('data', (data) => { stderrData += data.toString(); });

  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: '클러스터 생성 실패', details: stderrData });
    }
    const jsonMatch = stdoutData.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
    if (jsonMatch && jsonMatch[1]) {
      try {
        res.json(JSON.parse(jsonMatch[1].trim()));
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 오류', details: err.message });
      }
    } else {
      res.status(500).json({ error: '결과 데이터 마커 누락' });
    }
  });
});

// 6. POST /api/cluster-publish — 클러스터 전체 순차 발행 (SSE 스트리밍)
app.post('/api/cluster-publish', (req, res) => {
  const { keyword, category, platform, style, length, faq_count, img_prompt,
          seo_strength, publish, min_subs, max_subs, search_volume, competition, cpc } = req.body;

  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });

  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/main.py');

  const args = [
    scriptPath,
    '--mode', 'cluster',
    '--keyword', keyword,
    '--category', category || '정보형',
    '--platform', platform || 'tistory',
    '--style', style || 'friendly',
    '--length', String(length || '5000'),
    '--faq_count', String(faq_count || '10'),
    '--img_prompt', String(img_prompt || 'OFF'),
    '--seo_strength', seo_strength || 'strong',
    '--publish', publish ? 'ON' : 'OFF',
    '--search_volume', String(search_volume || 10000),
    '--competition', String(competition || 5000),
    '--cpc', cpc || '보통',
    '--min_subs', String(min_subs || 3),
    '--max_subs', String(max_subs || 10),
  ];

  const py = spawn(pythonPath, args);
  let stdoutData = '';

  py.stdout.on('data', (data) => {
    const chunk = data.toString();
    stdoutData += chunk;
    const lines = chunk.split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        res.write(`data: ${JSON.stringify({ log: line.trim() })}\n\n`);
      }
    });
  });

  py.stderr.on('data', (data) => {
    const errLine = data.toString().trim();
    console.error(`[Cluster Engine Error] ${errLine}`);
    res.write(`data: ${JSON.stringify({ log: `⚠️ [에러] ${errLine}` })}\n\n`);
  });

  py.on('close', (code) => {
    if (code !== 0) {
      res.write(`data: ${JSON.stringify({ error: '클러스터 파이프라인 비정상 종료' })}\n\n`);
      res.end();
      return;
    }
    const jsonMatch = stdoutData.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
    if (jsonMatch && jsonMatch[1]) {
      try {
        const finalJson = JSON.parse(jsonMatch[1].trim());
        res.write(`data: ${JSON.stringify({ success: true, result: finalJson })}\n\n`);
      } catch (err) {
        res.write(`data: ${JSON.stringify({ error: '결과 파싱 오류' })}\n\n`);
      }
    } else {
      res.write(`data: ${JSON.stringify({ error: '결과 데이터 마커 누락' })}\n\n`);
    }
    res.end();
  });
});

// 7. GET /api/published-posts — 발행 이력 + URL 조회
app.get('/api/published-posts', (req, res) => {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/internal_link_engine.py');

  const py = spawn(pythonPath, [scriptPath, '--posts']);
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', (code) => {
    try {
      res.json(JSON.parse(stdoutData));
    } catch {
      res.json([]);
    }
  });
});

// 8. GET /api/internal-links — 내부링크 그래프 데이터
app.get('/api/internal-links', (req, res) => {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/internal_link_engine.py');

  const py = spawn(pythonPath, [scriptPath, '--graph']);
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', (code) => {
    try {
      res.json(JSON.parse(stdoutData));
    } catch {
      res.json([]);
    }
  });
});

// 8.5 GET /api/dashboard-stats — 운영 대시보드 통계
app.get('/api/dashboard-stats', (req, res) => {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/internal_link_engine.py');

  const py = spawn(pythonPath, [scriptPath, '--stats']);
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', () => {
    try {
      res.json(JSON.parse(stdoutData));
    } catch {
      res.json({ total_published: 0, total_pending: 0, total_failed: 0, total_clusters: 0, total_links: 0, today_published: 0 });
    }
  });
});

// 9. POST /api/telegram-test — 텔레그램 봇 연결 테스트
app.post('/api/telegram-test', (req, res) => {
  const { token, chat_id } = req.body;
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/telegram_bot.py');

  // 환경변수를 임시로 설정하여 테스트
  const env = { ...process.env };
  if (token) env.TELEGRAM_BOT_TOKEN = token;
  if (chat_id) env.TELEGRAM_CHAT_ID = chat_id;

  const py = spawn(pythonPath, [scriptPath, '--test'], { env });
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', () => {
    try {
      res.json(JSON.parse(stdoutData));
    } catch {
      res.json({ ok: false, error: '응답 파싱 실패' });
    }
  });
});

// 10. POST /api/research — 자료 수집
app.post('/api/research', (req, res) => {
  const { keyword, max_news } = req.body;
  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'core/styler_pro_engine/research_engine.py');

  const args = [scriptPath, '--keyword', keyword];
  if (max_news) args.push('--max-news', String(max_news));

  const py = spawn(pythonPath, args);
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', (code) => {
    const jsonMatch = stdoutData.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
    if (jsonMatch && jsonMatch[1]) {
      try {
        res.json(JSON.parse(jsonMatch[1].trim()));
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 오류' });
      }
    } else {
      res.json({ keyword, news: [], official_links: [], total_sources: 0, citations: [] });
    }
  });
});

app.listen(PORT, () => {
  console.log(`AI Blog Agent Backend running on http://localhost:${PORT}`);
});
