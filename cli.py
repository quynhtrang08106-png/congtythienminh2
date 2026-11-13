"""
CLI Runner for Thien Minh AI Agent RFP Quotation Evaluation System
"""
import sys
import os
import argparse
from core.orchestrator import ThienMinhAIWorkflowOrchestrator
from core.proposal_agent import ProposalGeneratorAgent
from core.extract_agent import RequirementExtractionAgent

def print_banner():
    print("""
================================================================================
   THIÊN MINH TECHNOLOGY JSC - HỆ THỐNG AI AGENT ĐÁNH GIÁ YÊU CẦU CHÀO GIÁ
                   Quy trình tự động hóa RFP/RFQ thông minh
================================================================================
""")

def run_single(filepath: str, orchestrator: ThienMinhAIWorkflowOrchestrator):
    filename = os.path.basename(filepath)
    print(f"\n>>> ĐANG XỬ LÝ HỒ SƠ: {filename}")
    print("-" * 80)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pkg = orchestrator.process_rfp(content)

    print(f"[*] Mã RFP: {pkg.rfp_id}")
    print(f"[*] Dự án: {pkg.project_title}")
    print(f"[*] Khách hàng: {pkg.client_name}")
    print(f"[*] Trạng thái quy trình: {pkg.current_status}")

    # Check Gate 1
    if not pkg.completeness.is_complete:
        print("\n[!] CỔNG 1 (CÓ ĐỦ THÔNG TIN?): KHÔNG ĐẠT")
        print("    Các mục thông tin còn thiếu:")
        for idx, item in enumerate(pkg.completeness.missing_fields, 1):
            print(f"    {idx}. {item}")
        print("\n[--> HÀNH ĐỘNG] Kinh doanh liên hệ KH yêu cầu bổ sung thông tin.")
        print("    Dự thảo email đã được AI tự động tạo:")
        print("." * 60)
        print(pkg.completeness.clarification_email_draft[:400] + "\n    ... [Xem toàn văn trong báo cáo]")
        print("." * 60)
        return pkg

    print("\n[✓] CỔNG 1 (CÓ ĐỦ THÔNG TIN?): ĐẠT ĐẦY ĐỦ")

    # Step 4: Feasibility & Matching
    print("\n[+] ĐỐI CHIẾU THIẾT BỊ VÀ THÔNG SỐ (CATALOG MATCHING):")
    for m in pkg.catalog_matches:
        status_icon = "✓" if m.is_compliant else "✗"
        print(f"    [{status_icon}] {m.item_name} -> {m.matched_product_name or 'CHƯA CÓ TRONG CATALOG'}")
        print(f"        Trạng thái: {m.status} | Đơn giá: {m.unit_price_vnd:,.0f} đ | SL: {m.quantity}")
        for k, v in m.spec_checks.items():
            print(f"        - {k}: {'ĐẠT' if v else 'KHÔNG ĐẠT'}")

    # Schedule Feasibility
    sched = pkg.schedule_feasibility
    print("\n[+] ĐỐI CHIẾU NĂNG LỰC & LỊCH TRIỂN KHAI:")
    print(f"    Khả thi tiến độ: {'CÓ' if sched.is_feasible else 'KHÔNG'} (Mức rủi ro: {sched.risk_level})")
    print(f"    Lead time thiết bị: {sched.max_lead_time_days} ngày | Khối lượng: {sched.deployment_man_days} man-days")
    print(f"    Hoàn tất dự kiến: {sched.estimated_finish_date} | Hạn bàn giao KH: {sched.customer_deadline}")
    if sched.bottlenecks:
        for b in sched.bottlenecks:
            print(f"    [CẢNH BÁO TIẾN ĐỘ] {b}")

    # Step 5 & Gate 2: Pricing & Escalation
    pricing = pkg.pricing
    esc = pkg.escalation
    fmt = lambda val: f"{val:,.0f} đ".replace(",", ".")
    print("\n[+] TÍNH TOÁN GIÁ & CHÍNH SÁCH CHIẾT KHẤU:")
    print(f"    Tổng giá niêm yết:   {fmt(pricing.total_list_price)}")
    print(f"    Chiết khấu ({pricing.requested_discount_rate*100:.1f}%):   - {fmt(pricing.discount_amount)}")
    print(f"    Giá chào trước thuế: {fmt(pricing.final_quoted_price)}")
    print(f"    Tổng giá vốn (COGS): {fmt(pricing.total_cost)}")
    print(f"    Biên lợi nhuận gộp:  {pricing.gross_margin_rate*100:.1f}% ({fmt(pricing.gross_margin_amount)})")

    print("\n[!] CỔNG 2 (CÓ VƯỢT THẨM QUYỀN / CHIẾT KHẤU ĐẶC BIỆT / NGOÀI CATALOG?):")
    if esc.requires_escalation:
        print(f"    KẾT QUẢ: CÓ ({len(esc.triggers)} CỜ BÁO ĐỘNG)")
        print(f"    CẤP PHÊ DUYỆT BẮT BUỘC: {esc.approver_name}")
        for t in esc.triggers:
            print(f"    [!] [{t['severity']}] {t['title']}: {t['detail']}")
        print(f"    Gợi ý giải pháp giảm thiểu:")
        for mit in esc.mitigation_suggestions:
            print(f"    - {mit}")
    else:
        print(f"    KẾT QUẢ: KHÔNG (Nằm trong thẩm quyền tiêu chuẩn của {esc.approver_name})")

    # Step 7: Proposal & Compliance Matrix
    print(f"\n[+] HỢP NHẤT HỒ SƠ ĐỀ XUẤT:")
    print(f"    Đã tạo Ma trận đáp ứng kỹ thuật với {len(pkg.compliance_matrix)} tiêu chí:")
    for row in pkg.compliance_matrix[:3]:
        print(f"    - {row.client_requirement[:35]} | {row.compliance_status} | {row.thien_minh_solution[:30]}")
    if len(pkg.compliance_matrix) > 3:
        print(f"    ... và {len(pkg.compliance_matrix) - 3} tiêu chí khác.")

    return pkg

def main():
    parser = argparse.ArgumentParser(description="Thien Minh AI Agent RFP System")
    parser.add_argument("--sample", type=str, help="Tên file RFP trong thư mục samples/")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ 3 kịch bản mẫu")
    args = parser.parse_args()

    print_banner()
    orchestrator = ThienMinhAIWorkflowOrchestrator()

    if args.all or not args.sample:
        samples = [
            "samples/rfp_01_thieu_thong_tin.txt",
            "samples/rfp_02_chuan_hop_le.txt",
            "samples/rfp_03_vuot_tham_quyen_va_rui_ro.txt"
        ]
        for s in samples:
            run_single(s, orchestrator)
            print("=" * 80)
    else:
        filepath = os.path.join("samples", args.sample) if not os.path.exists(args.sample) else args.sample
        run_single(filepath, orchestrator)

if __name__ == "__main__":
    main()

