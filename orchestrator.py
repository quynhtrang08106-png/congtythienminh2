"""
Orchestrator: Điều phối quy trình đánh giá yêu cầu chào giá dự án bằng AI Agent
Công ty Cổ phần Công nghệ Thiên Minh
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional

from core.models import ProposalPackage, RFPDecomposition
from core.extract_agent import RequirementExtractionAgent
from core.feasibility_agent import FeasibilityMatchingAgent
from core.pricing_agent import PricingDiscountAgent
from core.proposal_agent import ProposalGeneratorAgent

class ThienMinhAIWorkflowOrchestrator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        catalog_path = os.path.join(data_dir, "product_catalog.json")
        service_path = os.path.join(data_dir, "service_catalog.json")
        calendar_path = os.path.join(data_dir, "resource_calendar.json")
        policy_path = os.path.join(data_dir, "policy_matrix.json")

        self.extract_agent = RequirementExtractionAgent()
        self.feasibility_agent = FeasibilityMatchingAgent(catalog_path, service_path, calendar_path)
        self.pricing_agent = PricingDiscountAgent(service_path, policy_path)
        self.proposal_agent = ProposalGeneratorAgent()

    def process_rfp(self, rfp_text: str, rfp_id_hint: Optional[str] = None) -> ProposalPackage:
        audit_trail = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # BƯỚC 1: Tiếp nhận yêu cầu chào giá
        audit_trail.append({
            "step": "BẮT ĐẦU: Tiếp nhận RFP/RFQ",
            "timestamp": now_str,
            "status": "SUCCESS",
            "message": f"Đã tiếp nhận văn bản hồ sơ ({len(rfp_text)} ký tự)."
        })

        # BƯỚC 2: [AI AGENT] Trích xuất & Phân rã yêu cầu
        decomp = self.extract_agent.extract_and_decompose(rfp_text, rfp_id_hint)
        audit_trail.append({
            "step": "AI AGENT: Trích xuất & Phân rã yêu cầu",
            "timestamp": now_str,
            "status": "SUCCESS",
            "message": f"Đã phân rã: Dự án '{decomp.project_title}', Khách hàng '{decomp.client_name}', {len(decomp.items)} hạng mục thiết bị, {decomp.cabling_nodes} nodes cáp."
        })

        # BƯỚC 3: Cổng kiểm tra tính đầy đủ: "Có đủ thông tin?"
        completeness = self.extract_agent.evaluate_completeness(decomp)
        if not completeness.is_complete:
            audit_trail.append({
                "step": "CỔNG 1: Kiểm tra tính đầy đủ thông tin",
                "timestamp": now_str,
                "status": "INCOMPLETE",
                "message": f"Hồ sơ thiếu {len(completeness.missing_fields)} thông tin bắt buộc. Chuyển sang luồng Kinh doanh liên hệ KH bổ sung."
            })
            pkg = ProposalPackage(
                rfp_id=decomp.rfp_id,
                project_title=decomp.project_title,
                client_name=decomp.client_name,
                date_created=now_str,
                completeness=completeness,
                current_status="CLARIFICATION_NEEDED",
                audit_trail=audit_trail
            )
            return pkg

        audit_trail.append({
            "step": "CỔNG 1: Kiểm tra tính đầy đủ thông tin",
            "timestamp": now_str,
            "status": "COMPLETE",
            "message": "Hồ sơ đầy đủ thông tin cốt lõi để lập giải pháp và báo giá."
        })

        # BƯỚC 4: [AI AGENT] Đối chiếu giải pháp, năng lực & lịch triển khai
        matches = self.feasibility_agent.match_solutions(decomp)
        schedule = self.feasibility_agent.assess_schedule_feasibility(decomp, matches)
        audit_trail.append({
            "step": "AI AGENT: Đối chiếu giải pháp, năng lực & lịch triển khai",
            "timestamp": now_str,
            "status": "SUCCESS" if schedule.is_feasible else "WARNING",
            "message": f"Đối chiếu {len(matches)} thiết bị. Đánh giá tiến độ: {schedule.risk_level} (Hoàn tất dự kiến {schedule.estimated_finish_date})."
        })

        # BƯỚC 5: [AI AGENT] Tính toán giá đề xuất & áp dụng chính sách chiết khấu
        pricing = self.pricing_agent.calculate_pricing(decomp, matches)
        escalation = self.pricing_agent.evaluate_escalation(decomp, matches, schedule, pricing)
        audit_trail.append({
            "step": "AI AGENT: Tính toán giá đề xuất & chính sách chiết khấu",
            "timestamp": now_str,
            "status": "SUCCESS",
            "message": f"Tổng giá chào trước thuế: {pricing.final_quoted_price:,.0f} VNĐ (Chiết khấu {pricing.requested_discount_rate*100:.1f}%, Biên LN: {pricing.gross_margin_rate*100:.1f}%)."
        })

        # BƯỚC 6: Cổng kiểm duyệt: "Có vượt thẩm quyền / Cần chiết khấu đặc biệt / Thiết bị ngoài danh mục?"
        if escalation.requires_escalation:
            audit_trail.append({
                "step": "CỔNG 2: Kiểm duyệt thẩm quyền & Ngoại lệ",
                "timestamp": now_str,
                "status": "ESCALATION_TRIGGERED",
                "message": f"Kích hoạt {len(escalation.triggers)} cờ cảnh báo rủi ro. Yêu cầu cấp phê duyệt: {escalation.approver_name}."
            })
            current_status = "ESCALATION_PENDING"
        else:
            audit_trail.append({
                "step": "CỔNG 2: Kiểm duyệt thẩm quyền & Ngoại lệ",
                "timestamp": now_str,
                "status": "WITHIN_AUTHORITY",
                "message": "Nằm trong thẩm quyền phê duyệt tiêu chuẩn của Nhân viên Kinh doanh."
            })
            current_status = "HITL_REVIEW"

        # BƯỚC 7: Hợp nhất tài liệu (Tạo hồ sơ đề xuất, ma trận đáp ứng & dự thảo bản chào giá)
        compliance_matrix = self.proposal_agent.build_compliance_matrix(decomp, matches, schedule)
        audit_trail.append({
            "step": "HỢP NHẤT TÀI LIỆU: Sinh Ma trận đáp ứng & Dự thảo chào giá",
            "timestamp": now_str,
            "status": "SUCCESS",
            "message": f"Đã hợp nhất hồ sơ đề xuất gồm {len(compliance_matrix)} tiêu chí ma trận đáp ứng và bảng chào giá hoàn chỉnh."
        })

        return ProposalPackage(
            rfp_id=decomp.rfp_id,
            project_title=decomp.project_title,
            client_name=decomp.client_name,
            date_created=now_str,
            completeness=completeness,
            catalog_matches=matches,
            schedule_feasibility=schedule,
            pricing=pricing,
            escalation=escalation,
            compliance_matrix=compliance_matrix,
            current_status=current_status,
            audit_trail=audit_trail
        )

    def apply_hitl_approval(self, pkg: ProposalPackage, approver: str, approved: bool, feedback: str = "") -> ProposalPackage:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if approved:
            pkg.current_status = "APPROVED"
            pkg.audit_trail.append({
                "step": "HITL: Thẩm định & Kiểm duyệt ranh giới dữ liệu",
                "timestamp": now_str,
                "status": "APPROVED",
                "message": f"Người duyệt ({approver}) đã ĐỒNG Ý xuất bản chào giá. Ghi chú: {feedback or 'Đạt chuẩn'}"
            })
        else:
            pkg.current_status = "REJECTED_NEEDS_REVISION"
            pkg.audit_trail.append({
                "step": "HITL: Thẩm định & Kiểm duyệt ranh giới dữ liệu",
                "timestamp": now_str,
                "status": "NEEDS_REVISION",
                "message": f"Người duyệt ({approver}) yêu cầu CẦN CHỈNH SỬA: {feedback}. Quay lại bước bóc tách & điều chỉnh."
            })
        return pkg

