"""
Agent 1: Trích xuất & Phân rã yêu cầu (RFP/RFQ Extractor & Completeness Validator)
"""
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.models import RFPDecomposition, RFPItem, CompletenessAssessment

class RequirementExtractionAgent:
    def __init__(self):
        pass

    def extract_and_decompose(self, text: str, rfp_id_hint: Optional[str] = None) -> RFPDecomposition:
        text_clean = text.strip()
        lines = [l.strip() for l in text_clean.split("\n") if l.strip()]

        # 1. Mã hồ sơ & Tên dự án
        rfp_id = rfp_id_hint or "RFP-AUTO-" + datetime.now().strftime("%Y%m%d-%H%M")
        m_rfp_id = re.search(r"(?:Mã\s*(?:hồ\s*sơ|dự\s*án)|RFP\s*Code)[:\s]*([A-Za-z0-9\-_]+)", text, re.IGNORECASE)
        if m_rfp_id:
            rfp_id = m_rfp_id.group(1).strip()

        project_title = "Dự án Cung cấp & Triển khai Hạ tầng Mạng"
        m_proj = re.search(r"^\s*(?:Dự\s*án|Tên\s*gói\s*thầu)[:\s]+([^\n]+)", text, re.MULTILINE | re.IGNORECASE)
        if m_proj:
            project_title = m_proj.group(1).strip()
        else:
            # Fallback if first line has project info
            for line in lines[:4]:
                if any(w in line.lower() for w in ["dự án", "hệ thống", "hạ tầng"]):
                    project_title = line.split(":")[-1].strip()
                    break

        client_name = "Khách hàng Doanh nghiệp"
        m_client = re.search(r"^\s*(?:Khách\s*hàng|Chủ\s*đầu\s*tư)[:\s]+([^\n]+)", text, re.MULTILINE | re.IGNORECASE)
        if m_client:
            client_name = m_client.group(1).strip()
        elif "Kính gửi Công ty Thiên Minh" in text and len(lines) > 1:
            for line in lines[:5]:
                if "khách hàng" in line.lower() or "công ty" in line.lower():
                    client_name = line.split(":")[-1].strip()
                    break

        # 2. Hạn nộp thầu & Hạn hoàn thành bàn giao (Go-live)
        submission_deadline = None
        m_sub = re.search(r"(?:Hạn\s*(?:chót\s*)?nộp\s*(?:hồ\s*sơ|chào\s*giá|thầu))[:\s]*([^\n]+)", text, re.IGNORECASE)
        if m_sub:
            submission_deadline = m_sub.group(1).strip()

        golive_deadline = None
        m_golive = re.search(r"(?:Thời\s*hạn\s*hoàn\s*thành|Bàn\s*giao\s*nghiệm\s*thu|Go-live|Trước\s*ngày|Deadline\s*Bắt\s*buộc)[:\s]*([^\n]+)", text, re.IGNORECASE)
        if m_golive:
            golive_deadline = m_golive.group(1).strip()

        # 3. Ngân sách
        budget_vnd = None
        m_budget = re.search(r"(?:Ngân\s*sách|Dự\s*toán)[:\s]*([0-9\.\,]+)\s*(?:VNĐ|VND|đồng|tỷ|triệu)?", text, re.IGNORECASE)
        if m_budget:
            raw_b = m_budget.group(1).replace(".", "").replace(",", "")
            try:
                val = float(raw_b)
                if val < 10000 and "tỷ" in m_budget.group(0).lower():
                    val = val * 1000000000
                elif val < 10000 and "triệu" in m_budget.group(0).lower():
                    val = val * 1000000
                budget_vnd = val
            except ValueError:
                budget_vnd = None

        # 4. Trích xuất Hạng mục thiết bị (BoQ)
        # Tách riêng phần thiết bị (Section I) nếu có
        sec_hw = text
        m_sec = re.search(r"(?:II\.|PHẦN\s*II)[\s\:\.\-]+(?:HẠNG\s*MỤC\s*DỊCH\s*VỤ|DỊCH\s*VỤ|ĐIỀU\s*KIỆN)", text, re.IGNORECASE)
        if m_sec:
            sec_hw = text[:m_sec.start()]

        items: List[RFPItem] = []
        item_counter = 1

        # Trích xuất dạng số thứ tự (1. Tường lửa ... 2. Switch ...)
        numbered_pattern = re.finditer(
            r"^\s*(\d+)\.\s*(.+?)(?:\s*[\-\:]\s*(?:Số\s*lượng|Qty)?[:\s]*(\d+)\s*(?:thiết\s*bị|bộ|cái)?)?$",
            sec_hw,
            re.MULTILINE | re.IGNORECASE
        )
        for m in numbered_pattern:
            title = m.group(2).strip()
            qty = int(m.group(3)) if m.group(3) else 1

            cat = None
            if any(w in title.lower() for w in ["switch", "chuyển mạch"]):
                cat = "Switch"
            elif any(w in title.lower() for w in ["firewall", "tường lửa", "ngfw"]):
                cat = "Firewall"
            elif any(w in title.lower() for w in ["access point", "wifi", "wi-fi", "bộ phát"]):
                cat = "Access Point"
            elif any(w in title.lower() for w in ["router", "định tuyến"]):
                cat = "Router"

            if cat:
                mandatory_specs = {}
                preferred_brand = None

                if cat == "Switch":
                    if any(w in text.lower() for w in ["layer 3", "l3", "ospf"]):
                        mandatory_specs["layer"] = "L3"
                    if "poe" in text.lower():
                        mandatory_specs["poe"] = True
                        m_watt = re.search(r"(\d+)\s*W", text, re.IGNORECASE)
                        if m_watt:
                            mandatory_specs["min_poe_watt"] = int(m_watt.group(1))
                    if any(w in text.lower() for w in ["10g", "sfp+"]):
                        mandatory_specs["uplink_10g"] = True
                    if "cisco" in text.lower():
                        preferred_brand = "Cisco"
                    elif "aruba" in text.lower():
                        preferred_brand = "Aruba"
                    elif "ruijie" in text.lower():
                        preferred_brand = "Ruijie"

                elif cat == "Firewall":
                    if any(w in text.lower() for w in ["threat protection", "utp", "ips"]):
                        mandatory_specs["threat_protection"] = True
                    if "palo alto" in text.lower():
                        preferred_brand = "Palo Alto"
                    elif "fortinet" in text.lower() or "fortigate" in text.lower():
                        preferred_brand = "Fortinet"

                elif cat == "Access Point":
                    if any(w in text.lower() for w in ["wi-fi 6", "wifi 6", "802.11ax"]):
                        mandatory_specs["standard"] = "WiFi 6 (802.11ax)"
                    if "aruba" in text.lower():
                        preferred_brand = "Aruba"
                    elif "ruijie" in text.lower():
                        preferred_brand = "Ruijie"

                items.append(RFPItem(
                    item_id=f"ITEM-{item_counter:02d}",
                    name=title,
                    category=cat,
                    quantity=qty,
                    mandatory_specs=mandatory_specs,
                    preferred_brand=preferred_brand,
                    raw_text=title
                ))
                item_counter += 1

        # Nếu không có định dạng số thứ tự, tìm dạng gạch đầu dòng (- 02 cái Switch ...)
        if not items:
            bullet_pattern = re.finditer(r"[\-\*\•]\s*(?:(\d+)\s*(?:cái|bộ|thiết\s*bị)?\s*)?([^\n]+)", sec_hw)
            for m in bullet_pattern:
                line = m.group(2).strip()
                qty = int(m.group(1)) if m.group(1) else 1
                cat = None
                if any(w in line.lower() for w in ["switch", "chuyển mạch"]):
                    cat = "Switch"
                elif any(w in line.lower() for w in ["firewall", "tường lửa", "ngfw"]):
                    cat = "Firewall"
                elif any(w in line.lower() for w in ["access point", "wifi", "wi-fi", "bộ phát"]):
                    cat = "Access Point"

                if cat:
                    mandatory_specs = {}
                    if "poe" in line.lower():
                        mandatory_specs["poe"] = True
                    if "wifi 6" in line.lower():
                        mandatory_specs["standard"] = "WiFi 6 (802.11ax)"

                    items.append(RFPItem(
                        item_id=f"ITEM-{item_counter:02d}",
                        name=line,
                        category=cat,
                        quantity=qty,
                        mandatory_specs=mandatory_specs,
                        raw_text=line
                    ))
                    item_counter += 1

        # Cáp mạng nodes
        cabling_nodes = 0
        m_cab = re.search(r"(\d+)\s*(?:nút\s*mạng|node\s*mạng|node|điểm\s*mạng)", text, re.IGNORECASE)
        if m_cab:
            cabling_nodes = int(m_cab.group(1))

        # SLA
        sla_requirement = "8x5xNBD"
        if "24/7/2h" in text.lower() or "24x7x2h" in text.lower() or "2 giờ" in text.lower():
            sla_requirement = "24x7x2H"
        elif "24/7" in text.lower() or "24x7x4h" in text.lower() or "4 giờ" in text.lower():
            sla_requirement = "24x7x4H"

        # Phạt tiến độ
        penalty_terms = None
        m_pen = re.search(r"(?:phạt\s*(?:tiến\s*độ|vi\s*phạm))[:\s]*([^\n\.;]+)", text, re.IGNORECASE)
        if m_pen:
            penalty_terms = m_pen.group(0).strip()

        # Chiết khấu thương mại yêu cầu
        commercial_terms = {}
        m_disc = re.search(r"(?:chiết\s*khấu)[:\s]*([0-9]+(?:\.[0-9]+)?)\s*%", text, re.IGNORECASE)
        if m_disc:
            commercial_terms["requested_discount_rate"] = float(m_disc.group(1)) / 100.0

        # Điều kiện kỹ thuật bắt buộc
        mandatory_conditions = []
        if "ospf" in text.lower():
            mandatory_conditions.append("Giao thức định tuyến động OSPF trên Switch Layer 3")
        if "poe+" in text.lower() or "802.3at" in text.lower():
            mandatory_conditions.append("Cấp nguồn chuẩn PoE+ 802.3at cho toàn bộ camera & AP")
        if "threat protection" in text.lower() or "utp" in text.lower():
            mandatory_conditions.append("Bản quyền bảo mật Threat Protection / UTP chính hãng")
        if "fluke" in text.lower() or "đo kiểm" in text.lower():
            mandatory_conditions.append("Đo kiểm thông mạch cáp mạng Fluke Networks và bàn giao UAT")

        return RFPDecomposition(
            rfp_id=rfp_id,
            project_title=project_title,
            client_name=client_name,
            submission_deadline=submission_deadline,
            golive_deadline=golive_deadline,
            budget_vnd=budget_vnd,
            items=items,
            cabling_nodes=cabling_nodes,
            mandatory_conditions=mandatory_conditions,
            sla_requirement=sla_requirement,
            penalty_terms=penalty_terms,
            commercial_terms=commercial_terms,
            raw_content=text
        )

    def evaluate_completeness(self, decomp: RFPDecomposition) -> CompletenessAssessment:
        missing = []

        if not decomp.golive_deadline and not decomp.submission_deadline:
            missing.append("Thời hạn nộp thầu / Thời hạn yêu cầu hoàn thành bàn giao (Go-live deadline)")

        if not decomp.items and decomp.cabling_nodes == 0:
            missing.append("Danh mục thiết bị và số lượng cụ thể (BoQ)")

        for item in decomp.items:
            if item.category == "Switch":
                if "48 cổng" in item.raw_text.lower() or "24 cổng" in item.raw_text.lower():
                    if "poe" not in item.raw_text.lower() and not item.mandatory_specs.get("poe"):
                        missing.append(f"Yêu cầu cấp nguồn PoE cho thiết bị {item.name} (Có cần cấp nguồn cho Camera/AP không?)")
            elif item.category == "Access Point":
                if not item.mandatory_specs.get("standard"):
                    missing.append(f"Tiêu chuẩn công nghệ WiFi (WiFi 5 AC hay WiFi 6 AX, số lượng kết nối đồng thời)")

        if decomp.sla_requirement == "8x5xNBD" and "bảo hành" not in decomp.raw_content.lower() and "sla" not in decomp.raw_content.lower():
            missing.append("Yêu cầu về gói dịch vụ bảo hành & thời gian phản hồi kỹ thuật tại chỗ (SLA Onsite)")

        is_complete = (len(missing) == 0)
        clarification_draft = None

        if not is_complete:
            clarification_draft = self._generate_clarification_email(decomp, missing)

        return CompletenessAssessment(
            is_complete=is_complete,
            missing_fields=missing,
            clarification_email_draft=clarification_draft,
            confidence_score=1.0 if is_complete else (1.0 - len(missing) * 0.2)
        )

    def _generate_clarification_email(self, decomp: RFPDecomposition, missing_fields: List[str]) -> str:
        bullet_points = "\n".join([f"  {i+1}. {field}" for i, field in enumerate(missing_fields)])
        email = f"""KÍNH GỬI: {decomp.client_name}
Đồng kính gửi: Ban Quản lý Dự án / Phòng Mua hàng

V/v: Đề nghị làm rõ thông tin kỹ thuật & tiến độ cho hồ sơ: {decomp.project_title}
Mã yêu cầu: {decomp.rfp_id}

Công ty Cổ phần Công nghệ Thiên Minh xin gửi lời chào trân trọng và lời cảm ơn chân thành đến Quý đơn vị đã quan tâm, gửi yêu cầu chào giá dự án đến chúng tôi.

Sau khi tiếp nhận và tiến hành thẩm định sơ bộ hồ sơ yêu cầu chào giá, để đảm bảo Thiên Minh có thể thiết kế giải pháp kỹ thuật tối ưu nhất, đáp ứng chuẩn xác nhu cầu vận hành thực tế và gửi đến Quý đơn vị bảng chào giá cạnh tranh nhất, chúng tôi kính đề nghị Quý đơn vị phối hợp làm rõ một số nội dung sau:

{bullet_points}

Ngay khi nhận được phản hồi làm rõ từ Quý đơn vị, đội ngũ Kỹ thuật & Kinh doanh của Thiên Minh sẽ hoàn thiện ngay Hồ sơ đề xuất giải pháp kỹ thuật, Ma trận đáp ứng và Báo giá thương mại chi tiết trong vòng 24 giờ làm việc.

Mọi thông tin phản hồi xin vui lòng gửi về:
- Bộ phận Giải pháp Khách hàng Doanh nghiệp - Công ty Thiên Minh
- Email: enterprise.solutions@thienminhtech.vn
- Hotline hỗ trợ kỹ thuật 24/7: (024) 3888 xxxx

Trân trọng kính chào!
---
BỘ PHẬN KINH DOANH & GIẢI PHÁP DOANH NGHIỆP - THIÊN MINH COMPANY"""
        return email
