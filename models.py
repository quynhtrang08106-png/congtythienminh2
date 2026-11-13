"""
Data models for Thien Minh AI Agent RFP Quotation Evaluation System.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class RFPItem:
    item_id: str
    name: str
    category: str  # Switch, Firewall, Access Point, Cabling, Service, etc.
    quantity: int
    mandatory_specs: Dict[str, Any] = field(default_factory=dict)
    preferred_brand: Optional[str] = None
    raw_text: str = ""

@dataclass
class RFPDecomposition:
    rfp_id: str
    project_title: str
    client_name: str
    submission_deadline: Optional[str] = None
    golive_deadline: Optional[str] = None
    budget_vnd: Optional[float] = None
    items: List[RFPItem] = field(default_factory=list)
    cabling_nodes: int = 0
    mandatory_conditions: List[str] = field(default_factory=list)
    sla_requirement: str = "8x5xNBD"
    penalty_terms: Optional[str] = None
    commercial_terms: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""

@dataclass
class CompletenessAssessment:
    is_complete: bool
    missing_fields: List[str] = field(default_factory=list)
    clarification_email_draft: Optional[str] = None
    confidence_score: float = 1.0

@dataclass
class CatalogMatchResult:
    item_id: str
    item_name: str
    matched_catalog_id: Optional[str]
    matched_product_name: Optional[str]
    status: str  # "EXACT_MATCH", "EQUIVALENT_MATCH", "OUT_OF_CATALOG", "UNDER_SPEC"
    is_compliant: bool
    spec_checks: Dict[str, bool] = field(default_factory=dict)
    unit_cost_vnd: float = 0.0
    unit_price_vnd: float = 0.0
    quantity: int = 1
    total_price_vnd: float = 0.0
    total_cost_vnd: float = 0.0
    lead_time_days: int = 0
    notes: str = ""

@dataclass
class ScheduleFeasibility:
    is_feasible: bool
    max_lead_time_days: int
    deployment_man_days: float
    earliest_start_date: str
    estimated_finish_date: str
    customer_deadline: Optional[str]
    buffer_days: int
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    assigned_senior_engineer: Optional[str] = None
    assigned_deployment_engineer: Optional[str] = None
    bottlenecks: List[str] = field(default_factory=list)

@dataclass
class PricingProposal:
    hardware_standard_total: float = 0.0
    hardware_cost_total: float = 0.0
    services_standard_total: float = 0.0
    services_cost_total: float = 0.0
    maintenance_standard_total: float = 0.0
    maintenance_cost_total: float = 0.0
    total_list_price: float = 0.0
    total_cost: float = 0.0
    requested_discount_rate: float = 0.0
    discount_amount: float = 0.0
    final_quoted_price: float = 0.0
    gross_margin_amount: float = 0.0
    gross_margin_rate: float = 0.0

@dataclass
class EscalationAssessment:
    requires_escalation: bool
    approver_role: str  # "SALES_REP", "SALES_MANAGER", "BOARD_OF_DIRECTORS"
    approver_name: str
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    action_required: str = ""
    mitigation_suggestions: List[str] = field(default_factory=list)

@dataclass
class ComplianceMatrixRow:
    criteria_id: str
    category: str
    client_requirement: str
    thien_minh_solution: str
    compliance_status: str  # "Đáp ứng (Complied)", "Vượt yêu cầu (Exceeded)", "Không đáp ứng (Deviation)", "Cần thẩm định"
    technical_proof: str

@dataclass
class ProposalPackage:
    rfp_id: str
    project_title: str
    client_name: str
    date_created: str
    completeness: CompletenessAssessment
    catalog_matches: List[CatalogMatchResult] = field(default_factory=list)
    schedule_feasibility: Optional[ScheduleFeasibility] = None
    pricing: Optional[PricingProposal] = None
    escalation: Optional[EscalationAssessment] = None
    compliance_matrix: List[ComplianceMatrixRow] = field(default_factory=list)
    current_status: str = "INITIAL"  # INITIAL, CLARIFICATION_NEEDED, ESCALATION_PENDING, HITL_REVIEW, APPROVED, REJECTED
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

