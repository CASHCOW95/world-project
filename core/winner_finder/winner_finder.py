import os
import sys
import glob
import re
import traceback
import pandas as pd

# [원칙 3] 실행 경로 고정
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

def normalize(value):
    if value is None or pd.isna(value): return ""
    return str(value).lower().strip().replace("@", "")

def run_checker():
    try:
        profile_file = "내프로필.xlsx"
        if not os.path.exists(profile_file):
            print(f"❌ 파일 없음: {profile_file}"); return

        print("📂 내 프로필 분석 중...")
        # 프로필은 안전하게 calamine 엔진으로 로드
        p_df = pd.read_excel(profile_file, engine='calamine')
        exact_ids = set()
        wallet_list = set()

        for col in p_df.columns:
            for val in p_df[col]:
                raw = normalize(val)
                if not raw: continue
                if raw.startswith('0x') or (raw.isdigit() and len(raw) >= 10) or len(raw) >= 25:
                    wallet_list.add(raw.replace("-", "").replace(" ", ""))
                else:
                    exact_ids.add(raw)

        print(f"✅ 프로필 완료 (아이디:{len(exact_ids)} / 지갑:{len(wallet_list)})")

        target_files = [f for f in glob.glob("*.xlsx") if f != profile_file and not f.startswith("[")]

        for target_file in target_files:
            print(f"\n🔍 '{target_file}' 분석 시작 (초강력 모드)...")
            
            try:
                # [필살기] openpyxl을 아예 안 쓰고 calamine 엔진으로 데이터만 뜯어옴
                # 이 방식은 스타일 에러(NamedCellStyle)의 영향을 전혀 받지 않아.
                df_dict = pd.read_excel(target_file, sheet_name=None, engine='calamine')
            except Exception as e:
                print(f"❌ 이 파일은 물리적으로 손상된 것 같아: {e}"); continue

            total_found = 0
            winner_log = []
            clean_name = target_file.replace('.xlsx', '')
            temp_output = f"TEMP_{clean_name}.xlsx"
            
            with pd.ExcelWriter(temp_output, engine='xlsxwriter') as writer:
                for sheet_name, df in df_dict.items():
                    results = []
                    sheet_found = 0
                    
                    # 모든 열(A, B...)을 싹 다 뒤지기
                    for _, row in df.iterrows():
                        is_match = False
                        match_val = ""
                        
                        for val in row:
                            win_val = normalize(val)
                            if not win_val: continue
                            
                            # 1. 마스킹 대응
                            if "*" in win_val:
                                clean_win = win_val.replace("-", "").replace(" ", "")
                                parts = clean_win.split('*')
                                prefix, suffix = (parts[0][:6] if parts[0] else ""), (parts[-1][-4:] if parts[-1] else "")
                                if prefix and suffix:
                                    for my_w in wallet_list:
                                        if prefix in my_w and suffix in my_w:
                                            is_match = True; match_val = win_val; break
                            # 2. 풀네임/아이디 대응
                            else:
                                clean_win = win_val.replace("-", "").replace(" ", "")
                                if win_val in exact_ids or clean_win in wallet_list:
                                    is_match = True; match_val = win_val; break
                            if is_match: break
                        
                        row_list = list(row)
                        row_list.insert(0, "★당첨★" if is_match else "")
                        if is_match:
                            sheet_found += 1
                            winner_log.append(str(match_val))
                        results.append(row_list)

                    # 결과 데이터 생성 및 정렬
                    new_cols = ["결과"] + list(df.columns)
                    res_df = pd.DataFrame(results, columns=new_cols)
                    res_df = res_df.sort_values(by="결과", ascending=False)
                    
                    # 저장 및 서식 적용
                    res_df.to_excel(writer, sheet_name=sheet_name[:30], index=False)
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name[:30]]
                    yellow_fmt = workbook.add_format({'bg_color': 'FFFF00'})
                    
                    for r_idx, v in enumerate(res_df["결과"]):
                        if v == "★당첨★":
                            worksheet.set_row(r_idx + 1, None, yellow_fmt)

                    total_found += sheet_found

            final_name = f"[{total_found}명당첨!({clean_name})].xlsx"
            if os.path.exists(final_name): os.remove(final_name)
            os.rename(temp_output, final_name)
            
            if total_found > 0:
                print(f"🎯 발견: {', '.join(winner_log[:5])}...")
            print(f"✅ 생성 완료: {final_name}")

    except Exception:
        print("\n❌ 진짜 미안, 또 에러야:")
        traceback.print_exc()

if __name__ == "__main__":
    run_checker()
    print("\n👋 댕댕이가 이번엔 진짜 사활을 걸었어. 확인해봐!")
    input("엔터 누르면 종료...")