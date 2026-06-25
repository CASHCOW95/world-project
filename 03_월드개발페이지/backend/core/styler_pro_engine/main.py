import os
import sys
import json
import argparse
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import serp_analyzer
import content_builder
import cta_engine
import image_factory
import image_generator
import html_block_engine
import revenue_score_engine
import seo_engine
import export_engine
import db
import publisher
import cluster_engine
import randomizer_engine
import research_engine
import internal_link_engine
import telegram_bot
import content_qa

def normalize_keyword(keyword):
    if not keyword:
        return ""
    words = keyword.split()
    normalized = []
    for w in words:
        if not normalized or normalized[-1] != w:
            normalized.append(w)
    return " ".join(normalized)

def run_v2_pipeline(args):
    keyword = normalize_keyword(args.keyword)
    category = args.category
    style = args.style
    cta_style = args.cta_style
    search_volume = args.search_volume
    competition = args.competition
    cpc = args.cpc
    platform = args.platform
    
    print(f"[STEP-1] '{keyword}' 상위 노출 10개 경쟁사 문서 및 포털 데이터 역분석 (SERP Analyzer)...")
    time.sleep(1)
    serp_data = serp_analyzer.analyze_serp(keyword)
    print(f"-> 분석 결과: 상위 평균 글자수 {serp_data['avg_word_count']}자, 추천 생성 길이: {serp_data['recommended_length']}자")
    
    print(f"[STEP-1.5] 자료 수집 엔진 및 양산형 회피 랜덤화 프로필 가동...")
    time.sleep(0.5)
    research_data = research_engine.collect_research_data(keyword)
    rand_profile = randomizer_engine.generate_randomization_profile(forced_style=style)
    style = rand_profile["style"]["id"]
    print(f"-> 자료 수집 완료 (출처 {research_data['total_sources']}건), 랜덤화 스타일: {rand_profile['style']['label']}")

    # Target length selection message
    target_length_desc = f"{args.length}자" if hasattr(args, 'length') else "5000자"
    print(f"[STEP-2] 지정된 글 길이({target_length_desc}) 및 FAQ 설정({args.faq_count}개) 기반 블록 빌드 중...")
    time.sleep(1.2)
    draft_data = content_builder.build_content_blocks(
        keyword=keyword, 
        serp_analysis=serp_data, 
        style=style,
        length=args.length,
        faq_count=args.faq_count,
        img_prompt=args.img_prompt,
        title=args.title if hasattr(args, 'title') else "",
        research_data=research_data,
        randomization_profile=rand_profile,
        category=category
    )
    title = draft_data["title"]
    blocks = draft_data["blocks"]
    print(f"-> 블록 생성 완료: '{title}' (총 {len(blocks)}개 블록)")
    
    print(f"[STEP-3] 키워드 기반 Smart CTA 링크 생성 중 (디자인 스타일: {cta_style})...")
    time.sleep(0.8)
    ctas = cta_engine.generate_ctas(keyword, cta_style)
    print(f"-> CTA 링크 {len(ctas)}개 생성 완료 (목차 아래, 본문 중간, FAQ 위, 결론 아래 배치)")
    
    print(f"[STEP-4] Smart Image Factory 가동: 대표이미지 프롬프트 자동 생성만 진행하며, 본문 이미지 자동 생성은 V2로 분리되어 생략됩니다...")
    time.sleep(0.5)
    images_list = []
    
    # Dynamic SEO loops based on intensity strength
    seo_strength = args.seo_strength if hasattr(args, 'seo_strength') else 'strong'
    if seo_strength == 'normal':
        max_seo_loops = 1
        pass_seo_score = 75
    elif seo_strength == 'extreme':
        max_seo_loops = 5
        pass_seo_score = 90
    else: # strong
        max_seo_loops = 3
        pass_seo_score = 85

    print(f"-> 설정된 SEO 강도: {seo_strength} (최대 개선 루프 {max_seo_loops}회, 통과 기준점 {pass_seo_score}점)")

    # Assembly and SEO audit loop
    current_html = ""
    seo_report = {}
    pass_flag = False
    
    for iteration in range(1, max_seo_loops + 1):
        print(f"[STEP-5] HTML Block Engine 조립 및 SEO/품질 진단 (루프 {iteration}회차)...")
        time.sleep(1)
        
        # Assemble blocks into final styled HTML if not already refined
        if not current_html:
            current_html = html_block_engine.compile_blocks_to_html(keyword, blocks, ctas, images_list)
        
        # SEO Audit
        seo_report = seo_engine.evaluate_seo(keyword, current_html)
        seo_report["pass"] = seo_report["score"] >= pass_seo_score
        
        # Content QA Engine Audit
        print(f"[STEP-5.1] Content QA Engine 품질 정밀 검사 진행 중...")
        qa_report = content_qa.evaluate_qa(keyword, category, title, blocks, current_html, research_data.get("citations", []))
        
        print(f"-> 현재 SEO 종합 점수: {seo_report['score']}점 / 100점 (목표: {pass_seo_score}점)")
        print(f"-> Content QA 품질 검사 결과: {'합격' if qa_report['pass'] else '불합격'}")
        
        pass_flag = seo_report["pass"] and qa_report["pass"]
        
        if pass_flag:
            print(f"-> [합격] SEO 기준점수 및 Content QA 기준을 모두 만족하여 루프를 중단합니다.")
            break
        else:
            combined_feedback = []
            if not seo_report["pass"]:
                combined_feedback.append("[SEO 개선 사항 피드백]:\n" + seo_report["feedback"])
            if not qa_report["pass"]:
                combined_feedback.append("[품질 QA 개선 사항 피드백]:\n" + qa_report["feedback"])
                
            feedback_str = "\n\n".join(combined_feedback)
            print(f"-> [불합격] 검사 기준을 만족하지 못해 피드백을 반영하여 자가개선(Refine)을 지시합니다.")
            print(f"-> [자가개선 피드백 내용]:\n{feedback_str}")
            
            if iteration < max_seo_loops:
                refined = content_builder.refine_content(keyword, current_html, feedback_str, style)
                current_html = refined["html_content"]
                title = refined["title"]
                time.sleep(1.5)
            else:
                print(f"-> 최대 자동 재생성 한도({max_seo_loops}회)를 채워 현재 완성본으로 확정합니다.")

                
    print("[STEP-6] Revenue Score Engine 가동: 광고 단가 및 전환 효율 점수 연산 중...")
    time.sleep(0.8)
    profit_report = revenue_score_engine.evaluate_revenue(keyword, search_volume, cpc, current_html)
    
    # Pack image prompts into profit report breakdown_json to seamlessly save into DB
    profit_report["image_prompts"] = draft_data.get("image_prompts")
    
    print(f"-> 수익성 점수: {profit_report['score']}점, 등급: {profit_report['grade']}, 예상 cpc: {profit_report['cpc_rating']}")
    
    print("[STEP-7] Export Engine 실행: output.html, content.json, seo_report.json, revenue_report.json 및 images/ 폴더 로컬 내보내기...")
    time.sleep(1.2)
    export_result = export_engine.export_assets(
        keyword=keyword,
        title=title,
        blocks=blocks,
        html_content=current_html,
        seo_report=seo_report,
        revenue_report=profit_report,
        images_list=images_list
    )
    print("-> 파일 로컬 내보내기 성공!")
    
    print("[STEP-8] 로컬 SQLite 데이터베이스 5개 테이블 스키마에 세션 실행 정보 백업 기록 중...")
    try:
        keyword_info = {
            "keyword": keyword,
            "category": category,
            "search_volume": search_volume,
            "competition": competition,
            "cpc": cpc,
            "golden_score": args.golden_score if hasattr(args, 'golden_score') and args.golden_score else 80
        }
        content_id = db.save_generation_data(
            keyword_info=keyword_info,
            title=title,
            blocks_json=json.dumps(blocks, ensure_ascii=False),
            assembled_html=current_html,
            images_list=images_list,
            seo_score=seo_report["score"],
            seo_details=seo_report,
            profit_score=profit_report["score"],
            profit_details=profit_report
        )
        print(f"-> DB 기록 완료 (컨텐츠 고유번호: #{content_id})")
    except Exception as e:
        sys.stderr.write(f"SQLite DB save error: {str(e)}\n")
        
    publish_url = ""
    # [STEP-9] 자동 발행 (옵션에 따라 실제 발행 API 기동)
    if hasattr(args, 'publish') and args.publish == "ON":
        print(f"[STEP-9] 지정된 플랫폼 ({platform})으로 원고 자동 발행 실행 중...")
        time.sleep(1.0)
        try:
            if platform == "tistory":
                pub_inst = publisher.TistoryPublisher()
            elif platform == "wordpress":
                pub_inst = publisher.WordpressPublisher()
            elif platform == "blogspot":
                pub_inst = publisher.BloggerPublisher()
            else:
                pub_inst = publisher.TistoryPublisher()
                
            images_list = []
            if args.img_prompt == "ON":
                print(f"-> 이미지 생성 및 본문 삽입 중...")
                current_html, img_filenames = image_generator.embed_images_in_html(
                    keyword=keyword,
                    html_content=current_html,
                    output_dir_relative="output/images"
                )
                for img_fn in img_filenames:
                    images_list.append({
                        "filename": img_fn,
                        "local_path": f"/output/images/{img_fn}",
                        "alt": f"{keyword} 관련 이미지",
                        "title": title
                    })
                    
            local_image_paths = [f"output/images/{img['filename']}" for img in images_list]
            tags_list = draft_data.get("tags", [keyword, category])
            
            pub_url, updated_html = publisher.publish_post_pipeline(
                publisher=pub_inst,
                title=title,
                html_content=current_html,
                tags=tags_list,
                local_image_paths=local_image_paths,
                scheduled_at=getattr(args, 'scheduled_at', None)
            )
            publish_url = pub_url
            current_html = updated_html
            print(f"-> 자동 발행 완료! 외부 URL: {publish_url}")
        except Exception as pe:
            sys.stderr.write(f"Publish error: {str(pe)}\n")
            print(f"⚠️ [경고] 자동 발행 중 에러 발생, 로컬 드래프트 파일만 보존합니다. ({str(pe)})")
            
    final_output = {
        "status": "success",
        "keyword": keyword,
        "title": title,
        "seo_score": seo_report["score"],
        "profit_score": profit_report["score"],
        "profit_grade": profit_report["grade"],
        "estimated_rpm": profit_report["estimated_rpm"],
        "cpc_rating": profit_report["cpc_rating"],
        "images": images_list,
        "html_content": current_html,
        "export_paths": export_result,
        "image_prompts": draft_data.get("image_prompts"),
        "publish_url": publish_url,
        "cpc_dollar": profit_report.get("cpc_dollar", 1.6),
        "estimated_visitors": profit_report.get("estimated_visitors", 0),
        "ctr": profit_report.get("ctr", 3.2),
        "estimated_revenue": profit_report.get("estimated_revenue", 0),
        "affiliate_product": profit_report.get("affiliate_product", "추천 제휴상품 연동 대기"),
        "ai_badge": profit_report.get("ai_badge", "🔵 작성 추천"),
        "blue_ocean_score": profit_report.get("blue_ocean_score", 50),
        "blue_ocean_recommend": profit_report.get("blue_ocean_recommend", "보통")
    }
    
    print("[SUCCESS] Styler Pro X v2.0 파이프라인 콘텐츠 생산 공정이 성황리에 완료되었습니다.")
    print("---JSON_START---")
    print(json.dumps(final_output, ensure_ascii=False))
    print("---JSON_END---")


def run_cluster_pipeline(args):
    """클러스터 파이프라인: 키워드 1개 → 메인글+서브글 순차 생성/발행 → 내부링크 삽입 → 텔레그램 알림."""
    keyword = normalize_keyword(args.keyword)
    category = args.category
    platform = args.platform

    print(f"[CLUSTER-1] '{keyword}' 토픽 클러스터 생성 중...")
    time.sleep(0.5)
    cluster = cluster_engine.generate_cluster(
        keyword=keyword,
        category=category,
        min_subs=int(getattr(args, 'min_subs', 3)),
        max_subs=int(getattr(args, 'max_subs', 10))
    )
    sub_count = len(cluster["subs"])
    print(f"-> 클러스터 생성 완료: 메인글 1 + 서브글 {sub_count}개")

    # DB 저장
    cluster_id = internal_link_engine.save_cluster(keyword, cluster)
    print(f"-> 클러스터 DB 저장 (cluster_id: {cluster_id})")

    # 텔레그램 알림
    telegram_bot.notify_cluster_start(keyword, sub_count)

    print(f"[CLUSTER-2] 자료 수집 엔진 가동...")
    time.sleep(0.5)
    research_data = research_engine.collect_research_data(keyword)
    print(f"-> 수집 완료: 뉴스 {len(research_data['news'])}건, 출처 {research_data['total_sources']}건")

    # 모든 글(메인+서브) 순차 생성
    all_posts = [{"role": "main", "title": cluster["main"]["title"], "keyword": keyword}]
    for sub in cluster["subs"]:
        all_posts.append({"role": "sub", "title": sub["title"], "keyword": sub["title"]})

    success_count = 0
    failed_count = 0
    results = []

    for idx, post_info in enumerate(all_posts):
        post_num = idx + 1
        role_label = "메인글" if post_info["role"] == "main" else f"서브글 {idx}"
        print(f"\n[CLUSTER-3-{post_num}] {role_label} 생성 시작: {post_info['title']}")

        try:
            post_keyword = normalize_keyword(post_info["keyword"])
            # 양산형 회피 프로필 생성
            rand_profile = randomizer_engine.generate_randomization_profile()
            style = rand_profile["style"]["id"]
            print(f"-> 랜덤화 프로필 적용: 문체={rand_profile['style']['label']}, CTA={rand_profile['cta']['style']['label']}")

            # SERP 분석
            serp_data = serp_analyzer.analyze_serp(post_keyword)

            # 콘텐츠 빌드
            draft_data = content_builder.build_content_blocks(
                keyword=post_keyword,
                serp_analysis=serp_data,
                style=style,
                length=args.length,
                faq_count=args.faq_count,
                img_prompt=args.img_prompt,
                title=post_info["title"],
                research_data=research_data,
                randomization_profile=rand_profile,
                category=category
            )
            title = draft_data["title"]
            blocks = draft_data["blocks"]

            # CTA 생성
            ctas = cta_engine.generate_ctas(post_keyword, rand_profile["cta"]["style"]["id"])

            # HTML 조립
            current_html = html_block_engine.compile_blocks_to_html(post_keyword, blocks, ctas, [])

            # 이미지 생성 및 본문 삽입
            images_list = []
            if getattr(args, 'img_prompt', 'OFF') == "ON":
                print(f"-> 이미지 생성 및 본문 삽입 중...")
                current_html, img_filenames = image_generator.embed_images_in_html(
                    keyword=post_keyword,
                    html_content=current_html,
                    output_dir_relative="output/images"
                )
                for img_fn in img_filenames:
                    images_list.append({
                        "filename": img_fn,
                        "local_path": f"/output/images/{img_fn}",
                        "alt": f"{post_keyword} 관련 이미지",
                        "title": post_info["title"]
                    })

            # SEO 진단
            seo_report = seo_engine.evaluate_seo(post_keyword, current_html)
            print(f"-> SEO 점수: {seo_report['score']}점")

            # 수익성 분석
            profit_report = revenue_score_engine.evaluate_revenue(
                post_keyword,
                getattr(args, 'search_volume', 10000),
                getattr(args, 'cpc', '보통'),
                current_html
            )

            # Export
            export_engine.export_assets(
                keyword=post_keyword,
                title=title,
                blocks=blocks,
                html_content=current_html,
                seo_report=seo_report,
                revenue_report=profit_report,
                images_list=images_list
            )

            # DB 저장
            keyword_info = {
                "keyword": post_keyword,
                "category": category,
                "search_volume": getattr(args, 'search_volume', 10000),
                "competition": getattr(args, 'competition', 5000),
                "cpc": getattr(args, 'cpc', '보통'),
                "golden_score": getattr(args, 'golden_score', 80)
            }
            content_id = db.save_generation_data(
                keyword_info=keyword_info,
                title=title,
                blocks_json=json.dumps(blocks, ensure_ascii=False),
                assembled_html=current_html,
                images_list=[],
                seo_score=seo_report["score"],
                seo_details=seo_report,
                profit_score=profit_report["score"],
                profit_details=profit_report
            )

            # 발행 (옵션)
            publish_url = ""
            if getattr(args, 'publish', 'OFF') == 'ON':
                try:
                    if platform == "tistory":
                        pub_inst = publisher.TistoryPublisher()
                    elif platform == "wordpress":
                        pub_inst = publisher.WordpressPublisher()
                    else:
                        pub_inst = publisher.BloggerPublisher()

                    tags_list = draft_data.get("tags", [post_keyword, category])
                    local_image_paths = [f"output/images/{img['filename']}" for img in images_list]
                    pub_url, updated_html = publisher.publish_post_pipeline(
                        publisher=pub_inst, title=title,
                        html_content=current_html, tags=tags_list,
                        local_image_paths=local_image_paths,
                        scheduled_at=getattr(args, 'scheduled_at', None)
                    )
                    publish_url = pub_url
                    current_html = updated_html
                    print(f"-> 발행 완료: {publish_url}")
                    telegram_bot.notify_publish_success(title, publish_url, post_keyword, platform)
                except Exception as pe:
                    print(f"-> 발행 실패: {str(pe)}")
                    telegram_bot.notify_error("발행", post_keyword, str(pe))

            # 발행 URL DB 기록
            post_id = internal_link_engine.save_published_post(
                cluster_id=cluster_id,
                role=post_info["role"],
                keyword=post_keyword,
                title=title,
                url=publish_url or f"local://content/{content_id}",
                platform=platform
            )

            results.append({
                "post_id": post_id,
                "role": post_info["role"],
                "title": title,
                "keyword": post_keyword,
                "seo_score": seo_report["score"],
                "profit_score": profit_report["score"],
                "publish_url": publish_url,
                "html_content": current_html
            })
            success_count += 1
            print(f"-> ✅ {role_label} 완료")

        except Exception as e:
            failed_count += 1
            print(f"-> ❌ {role_label} 실패: {str(e)}")
            telegram_bot.notify_error(f"클러스터 {role_label}", post_info["keyword"], str(e))
            results.append({
                "role": post_info["role"],
                "title": post_info["title"],
                "keyword": post_info["keyword"],
                "error": str(e)
            })

    # [CLUSTER-4] 내부링크 삽입 및 재발행
    link_map = {}
    if getattr(args, 'contextual_links', 'ON') == 'ON':
        if success_count == 0:
            print(f"\n[CLUSTER-4] ❌ 내부링크 구성 실패 (발행 성공 글이 0개이므로 스킵)")
        else:
            print(f"\n[CLUSTER-4] 내부링크 그래프 생성, 삽입 및 재발행 중...")
            link_map = internal_link_engine.build_link_map(cluster_id)
            internal_link_engine.save_link_records(link_map)
            print(f"-> 링크 {len(link_map.get('links', []))}개 생성 및 기록 완료")

        # Initialize publisher for modification if publish is ON
        pub_inst = None
        if getattr(args, 'publish', 'OFF') == 'ON':
            try:
                if platform == "tistory":
                    pub_inst = publisher.TistoryPublisher()
                elif platform == "wordpress":
                    pub_inst = publisher.WordpressPublisher()
                else:
                    pub_inst = publisher.BloggerPublisher()
            except Exception as e:
                sys.stderr.write(f"Failed to initialize publisher for modify: {str(e)}\n")

        # Inject internal links to each successfully generated post
        import sqlite3
        db_path = internal_link_engine.DB_PATH
        
        for item in results:
            # Check if it was generated successfully
            if "error" in item or "html_content" not in item:
                continue
                
            post_id = item["post_id"]
            title = item["title"]
            publish_url = item["publish_url"]
            html_content = item["html_content"]
            
            # Inject links
            updated_html = internal_link_engine.inject_internal_links(html_content, post_id, link_map)
            item["html_content"] = updated_html # Update in memory results
            
            # Update SQLite DB (contents table)
            try:
                conn = sqlite3.connect(str(db_path))
                c = conn.cursor()
                c.execute("""
                    UPDATE contents 
                    SET assembled_html = ? 
                    WHERE keyword = ? AND id = (SELECT max(id) FROM contents WHERE keyword = ?)
                """, (updated_html, item["keyword"], item["keyword"]))
                conn.commit()
                conn.close()
                print(f"-> DB 업데이트 완료: {title}")
            except Exception as dbe:
                sys.stderr.write(f"SQLite DB HTML update error: {str(dbe)}\n")
                
            # Call modify API to update the post on the platform
            if pub_inst and publish_url and not publish_url.startswith("local://"):
                print(f"-> 플랫폼 재발행(PUT/Modify) 실행 중: {title} ({publish_url})")
                try:
                    tags_list = [item["keyword"], category]
                    success = pub_inst.modify(
                        post_id_or_url=publish_url,
                        title=title,
                        html_content=updated_html,
                        tags=tags_list
                    )
                    if success:
                        print(f"-> 재발행 성공: {title}")
                    else:
                        print(f"-> ⚠️ 재발행 실패: {title}")
                except Exception as me:
                    sys.stderr.write(f"Modify API call error for {title}: {str(me)}\n")
    else:
        print(f"\n[CLUSTER-4] 문맥형 내부링크 자동 구성 기능 비활성화 (OFF) -> 삽입 생략")

    # [CLUSTER-5] 텔레그램 최종 알림
    telegram_bot.notify_cluster_complete(keyword, len(all_posts), success_count, failed_count)

    final_output = {
        "status": "success" if success_count > 0 else "failed",
        "mode": "cluster",
        "keyword": keyword,
        "cluster_id": cluster_id,
        "cluster": cluster,
        "total_posts": len(all_posts),
        "success": success_count,
        "failed": failed_count,
        "results": results,
        "link_map": {
            "total_links": len(link_map.get("links", [])),
            "main": link_map.get("main"),
            "subs_count": len(link_map.get("subs", []))
        }
    }

    print("[SUCCESS] 클러스터 파이프라인 전체 완료")
    print("---JSON_START---")
    print(json.dumps(final_output, ensure_ascii=False))
    print("---JSON_END---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Styler Pro X v2.0 Engine")
    parser.add_argument("--keyword", type=str, required=True)
    parser.add_argument("--category", type=str, default="생활")
    parser.add_argument("--style", type=str, default="friendly")
    parser.add_argument("--cta_style", type=str, default="card")
    parser.add_argument("--search_volume", type=int, default=10000)
    parser.add_argument("--competition", type=int, default=5000)
    parser.add_argument("--cpc", type=str, default="보통")
    parser.add_argument("--golden_score", type=int, default=80)
    parser.add_argument("--length", type=str, default="5000")
    parser.add_argument("--faq_count", type=str, default="10")
    parser.add_argument("--img_prompt", type=str, default="OFF")
    parser.add_argument("--title", type=str, default="")
    parser.add_argument("--seo_strength", type=str, default="strong")
    parser.add_argument("--publish", type=str, default="OFF")
    parser.add_argument("--platform", type=str, default="tistory")
    parser.add_argument("--scheduled_at", type=str, default=None,
                        help="예약 발행 시간 (예: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "cluster"],
                        help="single: 단건 생성, cluster: 클러스터 일괄 생성")
    parser.add_argument("--min_subs", type=int, default=3)
    parser.add_argument("--max_subs", type=int, default=10)
    parser.add_argument("--contextual_links", type=str, default="ON", choices=["ON", "OFF"])

    args = parser.parse_args()

    try:
        if args.mode == "cluster":
            run_cluster_pipeline(args)
        else:
            run_v2_pipeline(args)
    except Exception as e:
        import traceback
        sys.stderr.write(f"Pipeline crashed: {str(e)}\n")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
