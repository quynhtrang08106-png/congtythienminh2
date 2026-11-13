"""
Agent 4: Hợp nhất tài liệu (Proposal Synthesis, Compliance Matrix & Quotation Generator)
"""
from datetime import datetime
from typing import List, Dict, Any
from core.models import (
    RFPDecomposition, CatalogMatchResult, ScheduleFeasibility,
    PricingProposal, EscalationAssessment, ComplianceMatrixRow, ProposalPackage
)

class ProposalGeneratorAgent:
    def __init__(self):
        pass

    def build_compliance_matrix(
        self,
        decomp: RFPDecomposition,
        match_results: List[CatalogMatchResult],
        schedule: ScheduleFeasibility
    ) -> List[ComplianceMatrixRow]:
        matrix: List[ComplianceMatrixRow] = []
        idx = 1

        for match in match_results:
            status = "Đáp ứng (Complied)"
            proof = f"Sản phẩm {match.matched_product_name or match.item_name} đạt 100% thông số kỹ thuật datasheet."

            if match.status == "OUT_OF_CATALOG":
                status = "Cần thẩm định / Ngoài danh mục"
                proof = f"Thiết bị hãng {match.item_name} chưa có hợp đồng phân phối sẵn. Đề xuất chuyển đổi model tương đương hoặc nhập ủy thác."
            elif match.status == "UNDER_SPEC":
                status = "Không đáp ứng (Deviation)"
                proof = f"Model hiện tại chưa đáp ứng trọn vẹn thông số bắt buộc: {match.notes}"
            elif match.spec_checks.get("Layer 3 / OSPF Routing") and match.spec_checks.get("Cổng Uplink 10G SFP+"):
                status = "Vượt yêu cầu (Exceeded)"
                proof = f"Thiết bị hỗ trợ đầy đủ L3 Routing OSPF, Stacking phần cứng và 4 cổng quang 10G SFP+ tốc độ cao."

            matrix.append(ComplianceMatrixRow(
                criteria_id=f"COMP-{idx:02d}",
                category="Thiết bị phần cứng",
                client_requirement=f"{match.item_name} (SL: {match.quantity})",
                thien_minh_solution=f"{match.matched_product_name or 'Đề xuất hãng tương đương'}",
                compliance_status=status,
                technical_proof=proof
            ))
            idx += 1

        for cond in decomp.mandatory_conditions:
            matrix.append(ComplianceMatrixRow(
                criteria_id=f"COMP-{idx:02d}",
                category="Điều kiện kỹ thuật bắt buộc",
                client_requirement=cond,
                thien_minh_solution="Thiên Minh cam kết thực hiện đầy đủ theo tiêu chuẩn quốc tế và quy trình chuẩn hóa ISO/IEC.",
                compliance_status="Đáp ứng (Complied)",
                technical_proof="Chứng nhận năng lực triển khai từ hãng và thiết bị đo kiểm Fluke DSX-8000 đạt chuẩn hiệu chuẩn."
            ))
            idx += 1

        sched_status = "Đáp ứng (Complied)"
        sched_proof = f"Kế hoạch triển khai hoàn tất ngày {schedule.estimated_finish_date}, trước hạn bàn giao {schedule.customer_deadline}."
        if not schedule.is_feasible or schedule.risk_level in ["HIGH", "CRITICAL"]:
            sched_status = "Cần thẩm định / Rủi ro tiến độ"
            sched_proof = f"Thời gian hoàn tất dự kiến ({schedule.estimated_finish_date}) cần tối ưu thêm do thời gian giao hàng và lịch kỹ sư."

        matrix.append(ComplianceMatrixRow(
            criteria_id=f"COMP-{idx:02d}",
            category="Tiến độ & Bàn giao",
            client_requirement=f"Hoàn thành bàn giao trước {schedule.customer_deadline or decomp.golive_deadline}",
            thien_minh_solution=f"Huy động {schedule.assigned_senior_engineer or 'Kỹ sư Trưởng'} và đội ngũ triển khai theo phương án dự án trọng điểm.",
            compliance_status=sched_status,
            technical_proof=sched_proof
        ))
        idx += 1

        matrix.append(ComplianceMatrixRow(
            criteria_id=f"COMP-{idx:02d}",
            category="Dịch vụ & SLA",
            client_requirement=f"Cam kết dịch vụ {decomp.sla_requirement}",
            thien_minh_solution=f"Cung cấp gói dịch vụ hỗ trợ kỹ thuật chuyên nghiệp Thiên Minh Care ({decomp.sla_requirement}).",
            compliance_status="Đáp ứng (Complied)",
            technical_proof="Tổng đài tiếp nhận sự cố 24/7, mạng lưới kỹ thuật viên tại chỗ sẵn sàng ứng cứu sự cố."
        ))

        return matrix

    def generate_quotation_text(
        self,
        decomp: RFPDecomposition,
        match_results: List[CatalogMatchResult],
        pricing: PricingProposal,
        schedule: ScheduleFeasibility
    ) -> str:
        fmt = lambda val: f"{val:,.0f} VNĐ".replace(",", ".")

        lines = []
        lines.append("=" * 78)
        lines.append(f"CÔNG TY CỔ PHẦN CÔNG NGHỆ THIÊN MINH - THIEN MINH TECHNOLOGY JSC")
        lines.append("Địa chỉ: Tầng 8, Tòa nhà Công nghệ, Cầu Giấy, Hà Nội | Hotline: (024) 3888 xxxx")
        lines.append("=" * 78)
        lines.append(f"BẢN CHÀO GIÁ THƯƠNG MẠI & GIẢI PHÁP KỸ THUẬT")
        lines.append(f"Dự án: {decomp.project_title.upper()}")
        lines.append(f"Kính gửi: {decomp.client_name}")
        lines.append(f"Mã tham chiếu: TM-QUOTE-{decomp.rfp_id}")
        lines.append(f"Ngày lập: {datetime.now().strftime('%d/%m/%Y')} | Hiệu lực chào giá: 30 ngày")
        lines.append("-" * 78)
        lines.append(f"{'STT':<4} | {'HẠNG MỤC SẢN PHẨM / DỊCH VỤ':<38} | {'SL':<4} | {'ĐƠN GIÁ (VNĐ)':<15} | {'THÀNH TIỀN (VNĐ)'}")
        lines.append("-" * 78)

        stt = 1
        lines.append("PHẦN I: THIẾT BỊ PHẦN CỨNG MẠNG & BẢO MẬT")
        for m in match_results:
            p_name = (m.matched_product_name or m.item_name)[:36]
            lines.append(f"{stt:<4} | {p_name:<38} | {m.quantity:<4} | {fmt(m.unit_price_vnd):<15} | {fmt(m.total_price_vnd)}")
            stt += 1

        lines.append("\nPHẦN II: DỊCH VỤ TRIỂN KHAI, ĐO KIỂM & NGHIỆM THU")
        lines.append(f"{stt:<4} | {'Khảo sát & Lập thiết kế thi công (LLD)':<38} | {'1':<4} | {fmt(5000000):<15} | {fmt(5000000)}")
        stt += 1
        if decomp.cabling_nodes > 0:
            lines.append(f"{stt:<4} | {f'Thi công cáp mạng Cat6 ({decomp.cabling_nodes} nodes)':<38} | {decomp.cabling_nodes:<4} | {fmt(150000):<15} | {fmt(decomp.cabling_nodes * 150000)}")
            stt += 1
        lines.append(f"{stt:<4} | {'Cấu hình Core/Distribution Switch, VLAN, OSPF':<38} | {'1':<4} | {fmt(4000000):<15} | {fmt(4000000)}")
        stt += 1
        lines.append(f"{stt:<4} | {'Cấu hình Tường lửa, VPN & Bảo mật mạng':<38} | {'1':<4} | {fmt(6000000):<15} | {fmt(6000000)}")
        stt += 1
        lines.append(f"{stt:<4} | {'Cấu hình & Tối ưu vùng phủ sóng WiFi 6':<38} | {'1':<4} | {fmt(5000000):<15} | {fmt(5000000)}")
        stt += 1
        lines.append(f"{stt:<4} | {'Đo kiểm chuyên sâu Fluke & Bàn giao UAT':<38} | {'1':<4} | {fmt(4000000):<15} | {fmt(4000000)}")
        stt += 1

        lines.append("\nPHẦN III: GÓI BẢO HÀNH & DỊCH VỤ HỖ TRỢ KỸ THUẬT (SLA)")
        lines.append(f"{stt:<4} | {f'Dịch vụ Hỗ trợ kỹ thuật Thiên Minh Care ({decomp.sla_requirement})':<38} | {'1':<4} | {fmt(pricing.maintenance_standard_total):<15} | {fmt(pricing.maintenance_standard_total)}")

        lines.append("=" * 78)
        lines.append(f"TỔNG GIÁ TRỊ THEO ĐƠN GIÁ NIÊM YẾT:         {fmt(pricing.total_list_price):>30}")
        lines.append(f"CHIẾT KHẤU THƯƠNG MẠI ÁP DỤNG ({pricing.requested_discount_rate*100:.1f}%):       - {fmt(pricing.discount_amount):>28}")
        lines.append(f"TỔNG GIÁ CHÀO TRƯỚC THUẾ (ĐÃ CHIẾT KHẤU):   {fmt(pricing.final_quoted_price):>30}")
        vat = pricing.final_quoted_price * 0.10
        lines.append(f"THUẾ VAT (10%):                             {fmt(vat):>30}")
        lines.append(f"TỔNG CỘNG THANH TOÁN (ĐÃ BAO GỒM VAT):      {fmt(pricing.final_quoted_price + vat):>30}")
        lines.append("=" * 78)
        lines.append(f"Cam kết tiến độ: Bàn giao hoàn tất dự kiến ngày: {schedule.estimated_finish_date}")
        lines.append(f"Kỹ sư phụ trách kỹ thuật: {schedule.assigned_senior_engineer or 'Phòng Kỹ thuật Thiên Minh'}")
        lines.append("=" * 78)
        return "\n".join(lines)

