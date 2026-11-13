"""
Vercel Serverless Entrypoint for Thien Minh AI Agent
"""
import os
import sys
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Setup Python paths for Vercel Serverless execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.orchestrator import ThienMinhAIWorkflowOrchestrator

data_dir = os.path.join(BASE_DIR, "data")
orchestrator = ThienMinhAIWorkflowOrchestrator(data_dir=data_dir)

# Load product catalog safely
products_path = os.path.join(data_dir, "product_catalog.json")
if os.path.exists(products_path):
    with open(products_path, "r", encoding="utf-8") as f:
        master_products = json.load(f)
else:
    master_products = []

last_processed_package = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")

        if path in ["/api/products", "/products"]:
            self._send_json(master_products)

        elif path in ["/api/sample", "/sample"]:
            params = urllib.parse.parse_qs(url.query)
            name = params.get("name", ["rfp_02_chuan_hop_le.txt"])[0]
            clean_name = os.path.basename(name)
            filepath = os.path.join(BASE_DIR, "samples", clean_name)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self._send_json({"filename": clean_name, "content": content})
            else:
                self.send_error(404, f"Sample '{clean_name}' not found")

        elif path in ["/api/quotation-text", "/quotation-text"]:
            global last_processed_package
            if last_processed_package and last_processed_package.pricing and last_processed_package.schedule_feasibility:
                decomp = orchestrator.extract_agent.extract_and_decompose(last_processed_package.audit_trail[0]["message"])
                txt = orchestrator.proposal_agent.generate_quotation_text(
                    decomp,
                    last_processed_package.catalog_matches,
                    last_processed_package.pricing,
                    last_processed_package.schedule_feasibility
                )
                self._send_json({"quotation_text": txt})
            else:
                self._send_json({"quotation_text": "Chưa có dữ liệu bảng chào giá."})

        elif path in ["/api/health", "/health", "/api"]:
            self._send_json({
                "status": "healthy",
                "service": "Thien Minh AI Agent API",
                "version": "2.4",
                "platform": "Vercel Serverless"
            })

        else:
            self.send_error(404, f"Path not found: {path}")

    def do_POST(self):
        global last_processed_package
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path in ["/api/process", "/process"]:
            rfp_text = payload.get("rfp_text", "")
            pkg = orchestrator.process_rfp(rfp_text)
            last_processed_package = pkg
            self._send_json(pkg.to_dict())

        elif path in ["/api/approve", "/approve"]:
            approved = payload.get("approved", True)
            approver = payload.get("approver", "Người kiểm duyệt")
            feedback = payload.get("feedback", "")
            if last_processed_package:
                last_processed_package = orchestrator.apply_hitl_approval(last_processed_package, approver, approved, feedback)
                self._send_json(last_processed_package.to_dict())
            else:
                self.send_error(400, "No active proposal package to approve")

        elif path in ["/api/chat-advisor", "/chat-advisor"]:
            msg = payload.get("message", "").lower()
            if any(w in msg for w in ["chính sách", "chiết khấu"]):
                reply = "Chính sách chiết khấu chuẩn của Thiên Minh: Sales Rep tự quyết &le;8%, Trưởng phòng KD duyệt 8.1% - 12%, Ban Giám đốc duyệt &gt;12% hoặc Gross Margin &lt;22%."
            elif any(w in msg for w in ["palo alto", "ngoài catalog"]):
                reply = "Palo Alto hiện nằm ngoài Master Catalog của Thiên Minh. Nếu khách hàng yêu cầu, hệ thống sẽ kích hoạt cờ đỏ chuyển Trưởng phòng Kỹ thuật và Ban Giám đốc phê duyệt."
            elif any(w in msg for w in ["tiến độ", "kỹ sư"]):
                reply = "Thiên Minh hiện có 2 Kỹ sư Trưởng (CCIE/NSE 7) và 4 Kỹ sư triển khai (CCNP/NSE 4). Lead time thiết bị Cisco là 7-10 ngày, Fortinet 5-10 ngày, Aruba 5 ngày."
            else:
                reply = f"Trợ lý AI đã ghi nhận: '{msg}'. Bạn có thể chọn 1 trong 3 kịch bản mẫu ở giao diện để xem AI Agent phân tích tự động!"
            self._send_json({"reply": reply})

        else:
            self.send_error(404, f"API endpoint not found: {path}")

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(body)

