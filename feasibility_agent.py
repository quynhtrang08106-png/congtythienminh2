"""
Agent 2: Đối chiếu giải pháp, năng lực & lịch triển khai (Solution & Schedule Feasibility Matcher)
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from core.models import (
    RFPDecomposition, CatalogMatchResult, ScheduleFeasibility, RFPItem
)

class FeasibilityMatchingAgent:
    def __init__(self, catalog_path: str, service_path: str, calendar_path: str):
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.product_catalog = json.load(f)
        with open(service_path, "r", encoding="utf-8") as f:
            self.service_catalog = json.load(f)
        with open(calendar_path, "r", encoding="utf-8") as f:
            self.resource_calendar = json.load(f)

    def match_solutions(self, decomp: RFPDecomposition) -> List[CatalogMatchResult]:
        results: List[CatalogMatchResult] = []
        for item in decomp.items:
            match_res = self._match_single_item(item, decomp.raw_content)
            results.append(match_res)
        return results

    def _match_single_item(self, item: RFPItem, rfp_context: str) -> CatalogMatchResult:
        # 1. Kiểm tra yêu cầu hãng ngoài danh mục
        if item.preferred_brand and item.preferred_brand.lower() in ["palo alto", "juniper", "checkpoint"]:
            return CatalogMatchResult(
                item_id=item.item_id,
                item_name=item.name,
                matched_catalog_id=None,
                matched_product_name=f"{item.preferred_brand} (Chưa có trong danh mục Thiên Minh)",
                status="OUT_OF_CATALOG",
                is_compliant=False,
                spec_checks={"in_catalog": False},
                unit_cost_vnd=0.0,
                unit_price_vnd=0.0,
                quantity=item.quantity,
                total_price_vnd=0.0,
                total_cost_vnd=0.0,
                lead_time_days=21,
                notes=f"Thiên Minh chưa có thỏa thuận đại lý chính thức với hãng {item.preferred_brand}. Cần thẩm định nguồn hàng ủy quyền hoặc tư vấn thay thế sang Fortinet/Cisco."
            )

        # 2. Lọc danh mục theo category
        candidates = [p for p in self.product_catalog if p["category"].lower() == item.category.lower()]
        if not candidates:
            return CatalogMatchResult(
                item_id=item.item_id,
                item_name=item.name,
                matched_catalog_id=None,
                matched_product_name=None,
                status="OUT_OF_CATALOG",
                is_compliant=False,
                quantity=item.quantity,
                notes=f"Không tìm thấy chủng loại {item.category} trong catalog"
            )

        # 3. Đánh giá tính tuân thủ kỹ thuật của từng candidate
        compliant_candidates = []
        for p in candidates:
            specs = p["specs"]
            is_compliant = True
            spec_checks = {}

            if item.category == "Switch":
                if item.mandatory_specs.get("layer") == "L3":
                    has_l3 = "Layer 3" in specs.get("layer", "") or "OSPF" in specs.get("layer", "")
                    spec_checks["Layer 3 / OSPF Routing"] = has_l3
                    if not has_l3:
                        is_compliant = False

                if item.mandatory_specs.get("poe"):
                    has_poe = specs.get("poe_budget_watt", 0) > 0
                    spec_checks["Cấp nguồn PoE+"] = has_poe
                    if not has_poe:
                        is_compliant = False

                    min_watt = item.mandatory_specs.get("min_poe_watt", 0)
                    if min_watt and specs.get("poe_budget_watt", 0) < min_watt:
                        spec_checks[f"PoE Budget >= {min_watt}W"] = False
                        is_compliant = False
                    elif min_watt:
                        spec_checks[f"PoE Budget >= {min_watt}W"] = True

                if item.mandatory_specs.get("uplink_10g"):
                    has_10g = "10G" in specs.get("uplink", "") or "10GE" in specs.get("uplink", "")
                    spec_checks["Cổng Uplink 10G SFP+"] = has_10g
                    if not has_10g:
                        is_compliant = False

            elif item.category == "Firewall":
                if item.mandatory_specs.get("threat_protection"):
                    tp = specs.get("threat_protection", "")
                    has_tp = "1 Gbps" in tp or "700 Mbps" in tp
                    spec_checks["Threat Protection >= 700 Mbps"] = has_tp
                    if not has_tp:
                        is_compliant = False

            elif item.category == "Access Point":
                if item.mandatory_specs.get("standard") == "WiFi 6 (802.11ax)":
                    is_ax = "WiFi 6" in specs.get("standard", "")
                    spec_checks["Chuẩn Wi-Fi 6 (802.11ax)"] = is_ax
                    if not is_ax:
                        is_compliant = False

            brand_priority = 0
            if item.preferred_brand and p["brand"].lower() == item.preferred_brand.lower():
                brand_priority = 100

            if is_compliant:
                compliant_candidates.append({
                    "product": p,
                    "spec_checks": spec_checks,
                    "score": brand_priority - (p["standard_price_vnd"] / 1000000.0)
                })

        if compliant_candidates:
            compliant_candidates.sort(key=lambda x: x["score"], reverse=True)
            chosen = compliant_candidates[0]["product"]
            spec_checks = compliant_candidates[0]["spec_checks"]

            return CatalogMatchResult(
                item_id=item.item_id,
                item_name=item.name,
                matched_catalog_id=chosen["id"],
                matched_product_name=chosen["name"],
                status="EXACT_MATCH" if chosen["brand"].lower() == (item.preferred_brand or chosen["brand"]).lower() else "EQUIVALENT_MATCH",
                is_compliant=True,
                spec_checks=spec_checks,
                unit_cost_vnd=chosen["cost_price_vnd"],
                unit_price_vnd=chosen["standard_price_vnd"],
                quantity=item.quantity,
                total_price_vnd=chosen["standard_price_vnd"] * item.quantity,
                total_cost_vnd=chosen["cost_price_vnd"] * item.quantity,
                lead_time_days=chosen["lead_time_days"],
                notes=f"Khớp hoàn toàn yêu cầu kỹ thuật. Thời gian giao hàng: {chosen['lead_time_days']} ngày."
            )
        else:
            best_partial = candidates[0]
            return CatalogMatchResult(
                item_id=item.item_id,
                item_name=item.name,
                matched_catalog_id=best_partial["id"],
                matched_product_name=best_partial["name"],
                status="UNDER_SPEC",
                is_compliant=False,
                spec_checks={"mandatory_specs_satisfied": False},
                unit_cost_vnd=best_partial["cost_price_vnd"],
                unit_price_vnd=best_partial["standard_price_vnd"],
                quantity=item.quantity,
                total_price_vnd=best_partial["standard_price_vnd"] * item.quantity,
                total_cost_vnd=best_partial["cost_price_vnd"] * item.quantity,
                lead_time_days=best_partial["lead_time_days"],
                notes=f"CẢNH BÁO: Không có sản phẩm nào trong danh mục thỏa mãn đầy đủ các điều kiện kỹ thuật bắt buộc!"
            )

    def assess_schedule_feasibility(self, decomp: RFPDecomposition, match_results: List[CatalogMatchResult]) -> ScheduleFeasibility:
        current_date_str = self.resource_calendar.get("current_date", "2026-11-13")
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

        max_lead_time = max([m.lead_time_days for m in match_results], default=3)
        tech_days = (decomp.cabling_nodes / 20.0) if decomp.cabling_nodes else 1.0

        fw_count = sum(m.quantity for m in match_results if "firewall" in m.item_name.lower())
        sw_count = sum(m.quantity for m in match_results if "switch" in m.item_name.lower())
        ap_count = sum(m.quantity for m in match_results if "access point" in m.item_name.lower())

        senior_man_days = 2.0
        if fw_count > 0:
            senior_man_days += fw_count * 1.5

        dep_man_days = (sw_count * 0.5) + (1.0 if ap_count > 0 else 0) + 1.0
        total_work_days = max(tech_days, dep_man_days) + senior_man_days
        deployment_calendar_days = int(total_work_days * 1.3) + 2

        engineers = self.resource_calendar.get("engineers", [])
        sr_engineers = [e for e in engineers if "Senior" in e.get("title", "")]

        assigned_sr = None
        earliest_sr_free = None

        for sr in sr_engineers:
            busy_until = datetime.strptime(sr["busy_until"], "%Y-%m-%d")
            free_date = busy_until + timedelta(days=1)
            if earliest_sr_free is None or free_date < earliest_sr_free:
                earliest_sr_free = free_date
                assigned_sr = sr["name"]

        survey_start = max(current_date + timedelta(days=2), earliest_sr_free)
        hardware_ready_date = current_date + timedelta(days=max_lead_time)
        actual_install_start = max(survey_start + timedelta(days=2), hardware_ready_date)
        estimated_finish = actual_install_start + timedelta(days=deployment_calendar_days)

        customer_deadline = None
        bottlenecks = []
        is_feasible = True
        risk_level = "LOW"
        buffer_days = 0

        if decomp.golive_deadline:
            import re
            m_date = re.search(r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})", decomp.golive_deadline)
            if m_date:
                d, m, y = int(m_date.group(1)), int(m_date.group(2)), int(m_date.group(3))
                customer_deadline = datetime(y, m, d)
                diff_days = (customer_deadline - estimated_finish).days
                buffer_days = diff_days

                if diff_days < 0:
                    is_feasible = False
                    risk_level = "CRITICAL"
                    bottlenecks.append(f"Thời gian hoàn thành dự kiến ({estimated_finish.strftime('%d/%m/%Y')}) TRỄ HƠN hạn bàn giao của khách hàng ({customer_deadline.strftime('%d/%m/%Y')}) {abs(diff_days)} ngày.")
                elif diff_days < 5:
                    risk_level = "HIGH"
                    bottlenecks.append(f"Thời gian đệm an toàn quá ngắn ({diff_days} ngày). Rủi ro cao nếu giao hàng hoặc đo kiểm nghiệm thu phát sinh lỗi.")
                elif diff_days < 10:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"

        if customer_deadline and (customer_deadline - current_date).days < max_lead_time + 3:
            is_feasible = False
            risk_level = "CRITICAL"
            bottlenecks.append(f"Thời gian nhập khẩu/cung ứng thiết bị ({max_lead_time} ngày) chiếm gần hết tiến độ của dự án.")

        if customer_deadline and (customer_deadline - earliest_sr_free).days < 5:
            bottlenecks.append(f"Kỹ sư trưởng mạng ({assigned_sr}) chỉ trống lịch từ {earliest_sr_free.strftime('%d/%m/%Y')}, không đủ thời gian thiết kế và cấu hình chuyên sâu.")
            if risk_level != "CRITICAL":
                risk_level = "HIGH"

        return ScheduleFeasibility(
            is_feasible=is_feasible,
            max_lead_time_days=max_lead_time,
            deployment_man_days=round(total_work_days, 1),
            earliest_start_date=actual_install_start.strftime("%Y-%m-%d"),
            estimated_finish_date=estimated_finish.strftime("%Y-%m-%d"),
            customer_deadline=customer_deadline.strftime("%Y-%m-%d") if customer_deadline else decomp.golive_deadline,
            buffer_days=buffer_days,
            risk_level=risk_level,
            assigned_senior_engineer=assigned_sr,
            assigned_deployment_engineer="Lê Văn Cường & Phạm Minh Đức",
            bottlenecks=bottlenecks
        )

