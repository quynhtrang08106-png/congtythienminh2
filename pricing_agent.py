"""
Agent 3: Tính toán giá đề xuất & áp dụng chính sách chiết khấu (Pricing, Margin & Approval Engine)
"""
import json
from typing import List, Dict, Any, Tuple
from core.models import (
    RFPDecomposition, CatalogMatchResult, ScheduleFeasibility,
    PricingProposal, EscalationAssessment
)

class PricingDiscountAgent:
    def __init__(self, service_catalog_path: str, policy_matrix_path: str):
        with open(service_catalog_path, "r", encoding="utf-8") as f:
            self.services = {s["id"]: s for s in json.load(f)}
        with open(policy_matrix_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)

    def calculate_pricing(self, decomp: RFPDecomposition, match_results: List[CatalogMatchResult]) -> PricingProposal:
        hw_standard = sum(m.total_price_vnd for m in match_results)
        hw_cost = sum(m.total_cost_vnd for m in match_results)

        svc_standard = 0.0
        svc_cost = 0.0

        survey = self.services.get("SVC-SURVEY", {})
        svc_standard += survey.get("unit_price_vnd", 5000000)
        svc_cost += survey.get("cost_price_vnd", 2500000)

        if decomp.cabling_nodes > 0:
            cabling = self.services.get("SVC-CABLING-NODE", {})
            svc_standard += decomp.cabling_nodes * cabling.get("unit_price_vnd", 150000)
            svc_cost += decomp.cabling_nodes * cabling.get("cost_price_vnd", 90000)

        sw_count = sum(m.quantity for m in match_results if "switch" in m.item_name.lower())
        if sw_count > 0:
            sw_svc = self.services.get("SVC-CONFIG-SWITCH", {})
            svc_standard += sw_count * sw_svc.get("unit_price_vnd", 2000000)
            svc_cost += sw_count * sw_svc.get("cost_price_vnd", 1000000)

        fw_count = sum(m.quantity for m in match_results if "firewall" in m.item_name.lower())
        if fw_count > 0:
            fw_svc = self.services.get("SVC-CONFIG-FIREWALL", {})
            svc_standard += fw_count * fw_svc.get("unit_price_vnd", 6000000)
            svc_cost += fw_count * fw_svc.get("cost_price_vnd", 3000000)

        ap_count = sum(m.quantity for m in match_results if "access point" in m.item_name.lower())
        if ap_count > 0:
            wifi_svc = self.services.get("SVC-CONFIG-WIFI", {})
            svc_standard += wifi_svc.get("unit_price_vnd", 5000000)
            svc_cost += wifi_svc.get("cost_price_vnd", 2500000)

        uat_svc = self.services.get("SVC-TEST-UAT", {})
        svc_standard += uat_svc.get("unit_price_vnd", 4000000)
        svc_cost += uat_svc.get("cost_price_vnd", 2000000)

        maint_standard = 0.0
        maint_cost = 0.0
        if "24x7" in decomp.sla_requirement.lower() or "2 giờ" in decomp.sla_requirement.lower():
            rate = 0.18
            cost_rate = 0.08
        else:
            rate = 0.10
            cost_rate = 0.04

        maint_standard = hw_standard * rate
        maint_cost = hw_standard * cost_rate

        total_list = hw_standard + svc_standard + maint_standard
        total_cost = hw_cost + svc_cost + maint_cost

        requested_discount = decomp.commercial_terms.get("requested_discount_rate", 0.05)
        discount_amount = total_list * requested_discount
        final_quoted = total_list - discount_amount

        gross_margin_amount = final_quoted - total_cost
        gross_margin_rate = (gross_margin_amount / final_quoted) if final_quoted > 0 else 0.0

        return PricingProposal(
            hardware_standard_total=hw_standard,
            hardware_cost_total=hw_cost,
            services_standard_total=svc_standard,
            services_cost_total=svc_cost,
            maintenance_standard_total=maint_standard,
            maintenance_cost_total=maint_cost,
            total_list_price=total_list,
            total_cost=total_cost,
            requested_discount_rate=requested_discount,
            discount_amount=discount_amount,
            final_quoted_price=final_quoted,
            gross_margin_amount=gross_margin_amount,
            gross_margin_rate=gross_margin_rate
        )

    def evaluate_escalation(
        self,
        decomp: RFPDecomposition,
        match_results: List[CatalogMatchResult],
        schedule: ScheduleFeasibility,
        pricing: PricingProposal
    ) -> EscalationAssessment:
        triggers = []
        mitigation_suggestions = []

        # 1. Kiểm tra Thiết bị ngoài danh mục
        unlisted_items = [m for m in match_results if m.status == "OUT_OF_CATALOG"]
        if unlisted_items:
            names = ", ".join([u.item_name for u in unlisted_items])
            triggers.append({
                "code": "OUT_OF_CATALOG",
                "severity": "CRITICAL",
                "authority_required": "BOARD_OF_DIRECTORS",
                "title": "Thiết bị ngoài Master Catalog",
                "detail": f"Hồ sơ yêu cầu thiết bị chưa có mã sản phẩm trong catalog: {names}."
            })
            mitigation_suggestions.append(f"Tư vấn giải pháp tương đương từ Fortinet/Cisco hoặc liên hệ nhà phân phối nhập khẩu khẩn kèm cam kết bảo hành.")

        # 2. Kiểm tra Thiết bị không đủ cấu hình (UNDER_SPEC)
        underspec_items = [m for m in match_results if m.status == "UNDER_SPEC"]
        if underspec_items:
            names = ", ".join([u.item_name for u in underspec_items])
            triggers.append({
                "code": "UNDER_SPEC_RISK",
                "severity": "CRITICAL",
                "authority_required": "SALES_MANAGER",
                "title": "Nguy cơ cấu hình không đủ tính năng kỹ thuật",
                "detail": f"Hạng mục {names} không thỏa mãn 100% điều kiện kỹ thuật bắt buộc."
            })
            mitigation_suggestions.append("Bắt buộc nâng cấp lên model cao cấp hơn hoặc làm việc lại với khách hàng về giới hạn thông số.")

        # 3. Kiểm tra Lịch triển khai (Schedule Feasibility)
        if not schedule.is_feasible or schedule.risk_level in ["HIGH", "CRITICAL"]:
            triggers.append({
                "code": "SCHEDULE_MISMATCH",
                "severity": "HIGH" if schedule.risk_level == "HIGH" else "CRITICAL",
                "authority_required": "SALES_MANAGER" if schedule.risk_level == "HIGH" else "BOARD_OF_DIRECTORS",
                "title": "Lịch triển khai quá gấp / Xung đột nguồn lực kỹ sư",
                "detail": "; ".join(schedule.bottlenecks)
            })
            mitigation_suggestions.append("Huy động kỹ sư làm việc ngoài giờ (OT), điều chuyển dự án nội bộ hoặc đàm phán kéo dài hạn bàn giao thêm 7-10 ngày.")

        # 4. Kiểm tra Mức chiết khấu
        discount_rate = pricing.requested_discount_rate
        discount_matrix = self.policy.get("discount_matrix", [])
        discount_authority = "SALES_REP"
        for tier in discount_matrix:
            if tier["min_discount"] <= discount_rate <= tier["max_discount"]:
                discount_authority = tier["approver_role"]
                break

        if discount_authority == "SALES_MANAGER":
            triggers.append({
                "code": "DISCOUNT_SALES_MANAGER",
                "severity": "MEDIUM",
                "authority_required": "SALES_MANAGER",
                "title": f"Mức chiết khấu ({discount_rate*100:.1f}%) vượt thẩm quyền Nhân viên Kinh doanh",
                "detail": f"Mức chiết khấu yêu cầu từ 8% đến 12% cần Trưởng phòng Kinh doanh phê duyệt."
            })
        elif discount_authority in ["BOARD_OF_DIRECTORS", "REJECT_OR_SPECIAL_BOARD"]:
            triggers.append({
                "code": "DISCOUNT_BOARD_APPROVAL",
                "severity": "HIGH",
                "authority_required": "BOARD_OF_DIRECTORS",
                "title": f"Mức chiết khấu đặc biệt ({discount_rate*100:.1f}%) vượt thẩm quyền Trưởng phòng",
                "detail": f"Chiết khấu trên 12% ảnh hưởng trực tiếp đến lợi nhuận ròng công ty, bắt buộc Ban Giám đốc phê duyệt."
            })
            mitigation_suggestions.append("Đề xuất giảm mức chiết khấu xuống 10% kết hợp tặng thêm gói dịch vụ bảo trì định kỳ 6 tháng.")

        # 5. Kiểm tra Biên lợi nhuận gộp (Gross Margin)
        min_margin = self.policy.get("governance_rules", {}).get("min_gross_margin_rate", 0.22)
        if pricing.gross_margin_rate < min_margin:
            triggers.append({
                "code": "LOW_GROSS_MARGIN",
                "severity": "HIGH",
                "authority_required": "BOARD_OF_DIRECTORS",
                "title": f"Biên lợi nhuận gộp thấp ({pricing.gross_margin_rate*100:.1f}% < {min_margin*100:.1f}%)",
                "detail": f"Tỷ suất lợi nhuận dự án sau chiết khấu không đạt chỉ tiêu tối thiểu của công ty."
            })

        # 6. Kiểm tra SLA nghiêm ngặt & Phạt hợp đồng
        if "24x7x2h" in decomp.sla_requirement.lower() or "2 giờ" in decomp.sla_requirement.lower():
            triggers.append({
                "code": "HIGH_SLA_RISK",
                "severity": "HIGH",
                "authority_required": "BOARD_OF_DIRECTORS",
                "title": "Cam kết SLA khắc nghiệt (24/7/2h)",
                "detail": "Yêu cầu có mặt trong 2h vào cả ngày lễ/đêm muộn đòi hỏi quỹ dự phòng linh kiện tại chỗ và ca trực chuyên biệt."
            })
            mitigation_suggestions.append("Đề xuất điều chỉnh sang SLA 24/7/4h kèm cam kết hỗ trợ qua điện thoại/remote trong 15 phút.")

        if decomp.penalty_terms and "1.0%" in decomp.penalty_terms:
            triggers.append({
                "code": "HIGH_PENALTY_RISK",
                "severity": "CRITICAL",
                "authority_required": "BOARD_OF_DIRECTORS",
                "title": "Điều khoản phạt chậm tiến độ quá cao (1.0%/ngày)",
                "detail": "Rủi ro tài chính nghiêm trọng nếu xảy ra chậm trễ thông quan hoặc vận chuyển thiết bị."
            })
            mitigation_suggestions.append("Đàm phán hạ mức phạt tiến độ xuống tối đa 0.2%/ngày và tổng mức phạt không vượt quá 8% giá trị hợp đồng.")

        highest_role = "SALES_REP"
        for t in triggers:
            auth = t.get("authority_required")
            if auth == "BOARD_OF_DIRECTORS" or auth == "REJECT_OR_SPECIAL_BOARD":
                highest_role = "BOARD_OF_DIRECTORS"
                break
            elif auth == "SALES_MANAGER":
                highest_role = "SALES_MANAGER"

        requires_escalation = (len(triggers) > 0 and highest_role != "SALES_REP")

        if highest_role == "BOARD_OF_DIRECTORS":
            approver_name = "Ban Giám đốc (CEO / Ban Điều hành) phê duyệt"
            action_req = "Chuyển hồ sơ lên Ban Giám đốc để phê duyệt ngoại lệ về chiết khấu/thiết bị/tiến độ."
        elif highest_role == "SALES_MANAGER":
            approver_name = "Trưởng phòng Kinh doanh phê duyệt"
            action_req = "Chuyển hồ sơ cho Trưởng phòng Kinh doanh kiểm duyệt mức giá và khả năng đáp ứng."
        else:
            approver_name = "Nhân viên Kinh doanh tự quyết (Trong hạn mức)"
            action_req = "Hồ sơ đủ điều kiện xuất dự thảo chào giá mà không cần phê duyệt cấp cao."

        return EscalationAssessment(
            requires_escalation=requires_escalation,
            approver_role=highest_role,
            approver_name=approver_name,
            triggers=triggers,
            action_required=action_req,
            mitigation_suggestions=mitigation_suggestions
        )

