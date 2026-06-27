import sys
import json

# CTA Rules by trigger terms
CTA_RULES = [
    {
        "triggers": ["여권", "발급", "신분증", "travel"],
        "labels": ["📌 신청 바로가기", "📌 수수료 확인", "📌 발급기관 조회", "📌 공식 사이트 확인"]
    },
    {
        "triggers": ["지원금", "보조금", "소상공인", "청년"],
        "labels": ["📌 신청하기", "📌 지급대상 조회", "📌 지원금 확인", "📌 공식 홈페이지"]
    },
    {
        "triggers": ["절약", "아끼는", "난방비", "가스비", "전기세"],
        "labels": ["📌 절약 계산기 바로가기", "📌 할인 혜택 조회", "📌 지원 제도 확인", "📌 공식 감면 센터"]
    },
    {
        "triggers": ["당뇨", "고혈압", "고지혈증", "위염", "탈모", "치료"],
        "labels": ["📌 전문의 무료 상담", "📌 증상별 치료 팁", "📌 권장 영양 가이드", "📌 수치 계산기 바로가기"]
    }
]

DEFAULT_LABELS = ["📌 자세히 알아보기", "📌 혜택 한도 조회", "📌 신청 안내 가이드", "📌 공식 홈페이지 바로가기"]

def get_cta_labels(keyword):
    for rule in CTA_RULES:
        if any(t in keyword for t in rule["triggers"]):
            return rule["labels"]
    return DEFAULT_LABELS

def render_cta_html(label, design_style="card"):
    """
    Renders gorgeous premium CTA layouts using inline CSS.
    Styles: 'card' (gradient box), 'button' (neon button), 'banner' (highlight band).
    """
    href = "#sec-1" # Anchor link for pre-API phase
    
    if design_style == "button":
        return f"""
<div class="cta-block-btn" style="text-align: center; margin: 25px 0; font-family: sans-serif;">
  <a href="{href}" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; border-radius: 50px; padding: 14px 35px; font-weight: 800; display: inline-block; text-decoration: none; font-size: 14px; box-shadow: 0 10px 20px rgba(79,70,229,0.2); transition: all 0.2s; border: 1px solid #7c3aed;">
    {label}
  </a>
</div>
        """.strip()
        
    elif design_style == "banner":
        return f"""
<div class="cta-block-banner" style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-left: 5px solid #4f46e5; padding: 18px 25px; border-radius: 12px; margin: 25px 0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.03); font-family: sans-serif;">
  <span style="color: #1e293b; font-size: 13.5px; font-weight: 700;">💡 한정 기간 내 실시간 혜택 대상자 특별 선별</span>
  <a href="{href}" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; border-radius: 8px; padding: 8px 18px; font-weight: 800; text-decoration: none; font-size: 12px; box-shadow: 0 4px 12px rgba(79,70,229,0.2);">
    {label}
  </a>
</div>
        """.strip()
        
    else: # 'card' default
        return f"""
<div class="cta-block-card" style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 20px; padding: 22px; margin: 25px 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); font-family: sans-serif;">
  <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 800; color: #4f46e5;">⚡ 대상자 실시간 선별 지원 안내</h4>
  <p style="margin: 0 0 16px 0; font-size: 12.5px; color: #475569; opacity: 0.95;">놓치면 나만 손해 보는 필수 정보 및 수혜 내용을 아래 링크에서 바로 조회하십시오.</p>
  <a href="{href}" style="background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%); color: white; border-radius: 50px; padding: 10px 24px; font-weight: bold; display: inline-block; text-decoration: none; font-size: 13px; box-shadow: 0 4px 12px rgba(236,72,153,0.25);">
    {label}
  </a>
</div>
        """.strip()

def generate_ctas(keyword, design_style="card"):
    labels = get_cta_labels(keyword)
    return [render_cta_html(label, design_style) for label in labels]

if __name__ == "__main__":
    ctas = generate_ctas("미성년자 여권", "banner")
    print(ctas[0])
