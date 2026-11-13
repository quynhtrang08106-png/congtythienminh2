"""
Hệ thống AI Agent Đánh Giá Yêu Cầu Chào Giá Dự Án (RFP/RFQ)
Công ty Cổ phần Công nghệ Thiên Minh - Thien Minh Technology JSC
Giao diện Web Portal Hiện Đại chạy trên Localhost
"""
import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.orchestrator import ThienMinhAIWorkflowOrchestrator

orchestrator = ThienMinhAIWorkflowOrchestrator(data_dir=os.path.join(BASE_DIR, "data"))
current_package = None

with open(os.path.join(BASE_DIR, "data", "product_catalog.json"), "r", encoding="utf-8") as f:
    master_products = json.load(f)

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Thiên Minh AI Agent | Đánh Giá & Chào Giá Dự Án (RFP/RFQ)</title>
  <!-- Tailwind CSS & Fonts -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#f0f9ff',
              100: '#e0f2fe',
              200: '#bae6fd',
              500: '#0284c7',
              600: '#0369a1',
              700: '#075985',
              dark: '#0f172a',
              card: '#1e293b'
            }
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            display: ['"Space Grotesk"', 'sans-serif']
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
    .card-hover { transition: all 0.25s ease; }
    .card-hover:hover { transform: translateY(-3px); box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.08); }
    .step-active { border-color: #0284c7; background-color: #f0f9ff; color: #0369a1; }
    .step-pass { border-color: #10b981; background-color: #ecfdf5; color: #047857; }
    .step-fail { border-color: #f43f5e; background-color: #fff1f2; color: #be123c; }
    .step-warn { border-color: #f59e0b; background-color: #fffbeb; color: #b45309; }
  </style>
</head>
<body class="text-slate-800 antialiased selection:bg-sky-200 selection:text-sky-900">

  <!-- Top Info Strip -->
  <div class="bg-slate-900 text-slate-300 text-xs py-1.5 px-4 border-b border-slate-800">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <span class="inline-flex items-center text-emerald-400 font-semibold">
          <span class="w-2 h-2 mr-1.5 bg-emerald-500 rounded-full animate-ping"></span>
          AI Agent Engine v2.4 Online (Localhost:8080)
        </span>
        <span class="hidden md:inline text-slate-500">|</span>
        <span class="hidden md:inline text-slate-400">Công ty Cổ phần Công nghệ & Dịch vụ Viễn thông Thiên Minh</span>
      </div>
      <div class="flex items-center space-x-4">
        <span>Quy chế Chiết khấu: <strong>Sales &le;8% | TP &le;12% | BGĐ &gt;12%</strong></span>
        <span>Hotline Kỹ thuật: <strong>(024) 3888 xxxx</strong></span>
      </div>
    </div>
  </div>

  <!-- Header -->
  <header class="bg-white/95 backdrop-blur-md sticky top-0 z-40 border-b border-slate-200 shadow-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      
      <!-- Logo -->
      <div class="flex items-center space-x-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-sky-600 to-blue-700 text-white flex items-center justify-center font-black text-xl shadow-md">
          TM
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="font-display font-bold text-xl tracking-tight text-slate-900">THIÊN MINH TECHNOLOGY</h1>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-100 text-sky-800 uppercase tracking-wider">AI AGENT</span>
          </div>
          <p class="text-xs text-slate-500 font-medium">Hệ thống Thẩm định & Tự động Đánh giá Yêu cầu Chào giá (RFP/RFQ)</p>
        </div>
      </div>

      <!-- Nav Links -->
      <nav class="hidden lg:flex items-center space-x-6 text-sm font-semibold text-slate-600">
        <a href="#console" class="text-sky-600 hover:text-sky-700 flex items-center space-x-1.5">
          <i class="fa-solid fa-bolt text-xs"></i>
          <span>Thẩm Định RFP</span>
        </a>
        <a href="#workflow-section" class="hover:text-slate-900">Quy Trình Lưu Đồ</a>
        <a href="#catalog-section" class="hover:text-slate-900">Danh Mục Thiết Bị</a>
        <a href="#policy-section" class="hover:text-slate-900">Ranh Giới Dữ Liệu</a>
      </nav>

      <!-- Action Button -->
      <div class="flex items-center space-x-3">
        <a href="#console" class="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs rounded-xl shadow-md hover:shadow-lg transition flex items-center space-x-2">
          <i class="fa-solid fa-file-circle-check"></i>
          <span>Nạp Hồ Sơ RFP Mới</span>
        </a>
      </div>

    </div>
  </header>

  <!-- Hero Section -->
  <section class="relative overflow-hidden bg-gradient-to-b from-sky-50/60 via-white to-slate-50 pt-10 pb-12 border-b border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        <!-- Left Hero Copy (7 cols) -->
        <div class="lg:col-span-7 space-y-5 text-center lg:text-left">
          
          <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-100 border border-sky-200 text-sky-800 text-xs font-bold">
            <i class="fa-solid fa-microchip-ai text-sky-600"></i>
            <span>TỰ ĐỘNG HÓA 20 BỘ RFP/RFQ MỖI THÁNG</span>
          </div>

          <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 leading-[1.2]">
            Đánh Giá & Chào Giá Dự Án Bằng <span class="text-sky-600">AI Agent</span>
          </h2>

          <p class="text-slate-600 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto lg:mx-0">
            Giải quyết triệt để 4 rủi ro lớn nhất của Thiên Minh: <strong>Bỏ sót điều kiện bắt buộc</strong>, <strong>chọn gói giá thấp thiếu chức năng</strong>, <strong>lịch triển khai không phù hợp</strong> và <strong>chiết khấu / thiết bị ngoài danh mục chưa chuyển duyệt nhất quán</strong>.
          </p>

          <!-- Key Metrics Badges -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-left">
            <div class="p-3 bg-white rounded-xl border border-slate-200 shadow-xs">
              <div class="text-[11px] font-bold uppercase text-slate-400">Thời gian bóc tách</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">&lt; 3 Giây</div>
              <div class="text-[10px] text-emerald-600">Nhanh hơn 95% thủ công</div>
            </div>
            <div class="p-3 bg-white rounded-xl border border-slate-200 shadow-xs">
              <div class="text-[11px] font-bold uppercase text-slate-400">Sai sót kỹ thuật</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">0% Under-spec</div>
              <div class="text-[10px] text-sky-600">Đối chiếu 100% specs</div>
            </div>
            <div class="p-3 bg-white rounded-xl border border-slate-200 shadow-xs">
              <div class="text-[11px] font-bold uppercase text-slate-400">Kiểm soát tiến độ</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">Lead Time + Kỹ sư</div>
              <div class="text-[10px] text-amber-600">Chặn xung đột lịch</div>
            </div>
            <div class="p-3 bg-white rounded-xl border border-slate-200 shadow-xs">
              <div class="text-[11px] font-bold uppercase text-slate-400">Phê duyệt HITL</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">3 Cấp Thẩm Quyền</div>
              <div class="text-[10px] text-slate-500">Sales &bull; TP &bull; Ban GĐ</div>
            </div>
          </div>

        </div>

        <!-- Right Hero Visual Flow Preview (5 cols) -->
        <div class="lg:col-span-5">
          <div class="bg-slate-900 rounded-2xl p-5 text-white shadow-xl border border-slate-800 relative">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-3 text-xs">
              <span class="font-bold text-sky-400 flex items-center">
                <i class="fa-solid fa-code-branch mr-2"></i>Tiến Trình Xử Lý AI Realtime
              </span>
              <span class="text-[11px] text-slate-400">Thien Minh Pipeline</span>
            </div>
            
            <div class="space-y-2.5 text-xs font-mono">
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[1] Tiếp nhận RFP / RFQ</span>
                <span class="text-emerald-400 font-bold">&check; Ingested</span>
              </div>
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[2] AI Agent Trích xuất & Phân rã</span>
                <span class="text-emerald-400 font-bold">&check; Decomposed</span>
              </div>
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[3] Cổng 1: Đủ thông tin?</span>
                <span class="text-amber-400 font-bold">Auto-Validation</span>
              </div>
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[4] AI Đối chiếu Specs & Lịch</span>
                <span class="text-sky-400 font-bold">Matching Matrix</span>
              </div>
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[5] Tính Giá & Cổng 2 Thẩm quyền</span>
                <span class="text-rose-400 font-bold">Escalation Check</span>
              </div>
              <div class="p-2 rounded bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
                <span>[6] Hợp nhất & Phê duyệt HITL</span>
                <span class="text-emerald-400 font-bold">Final Quotation</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- Interactive Workflow Stepper (Mapping 100% Lưu đồ ảnh Thiên Minh) -->
  <section id="workflow-section" class="py-6 bg-white border-b border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center">
          <i class="fa-solid fa-diagram-project mr-2 text-sky-600"></i>Lưu đồ 6 Bước Vận Hành AI Agent (Thiên Minh Company)
        </h3>
        <span class="text-xs text-slate-400 font-medium">Bám sát 100% sơ đồ quy trình nghiệp vụ</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs" id="flow-steps">
        <div id="step-1" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">1. Tiếp nhận</div>
          <div class="text-[10px] text-slate-500 mt-0.5">Văn bản RFP/RFQ</div>
        </div>
        <div id="step-2" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">2. Trích xuất</div>
          <div class="text-[10px] text-slate-500 mt-0.5">[AI Agent 1] BoQ & Đk</div>
        </div>
        <div id="step-3" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">3. Cổng Đủ TT?</div>
          <div class="text-[10px] text-slate-500 mt-0.5">Gate 1: Thiếu thì dừng</div>
        </div>
        <div id="step-4" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">4. Đối chiếu</div>
          <div class="text-[10px] text-slate-500 mt-0.5">[AI Agent 2] Specs & Lịch</div>
        </div>
        <div id="step-5" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">5. Giá & Cấp duyệt</div>
          <div class="text-[10px] text-slate-500 mt-0.5">[AI Agent 3] Gate 2</div>
        </div>
        <div id="step-6" class="p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all">
          <div class="font-bold text-slate-800">6. Hợp nhất & HITL</div>
          <div class="text-[10px] text-slate-500 mt-0.5">Xuất bản chào giá</div>
        </div>
      </div>
    </div>
  </section>

  <!-- MAIN CONSOLE: INTERACTIVE RFP WORKSPACE -->
  <main id="console" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Left Column: Input RFP & Sample Selector (5 cols) -->
      <div class="lg:col-span-5 space-y-5">
        
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 class="font-bold text-slate-900 text-sm flex items-center">
              <i class="fa-solid fa-file-lines text-sky-600 mr-2"></i>Nạp Hồ Sơ Yêu Cầu Chào Giá (RFP)
            </h3>
            <span class="text-[11px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">B2B Enterprise</span>
          </div>

          <!-- 3 Real-world Sample Buttons -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Chọn nhanh 3 kịch bản kiểm thử:</label>
            <div class="space-y-2">
              <button onclick="loadSample('rfp_01_thieu_thong_tin.txt')" class="w-full text-left p-3 rounded-xl border border-amber-200 bg-amber-50/70 hover:bg-amber-100/70 text-amber-950 transition flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold">Kịch bản 1: Hồ sơ Thiếu thông tin cốt lõi</div>
                  <div class="text-[11px] text-amber-700">Chưa có deadline, PoE, SLA &rarr; Chặn báo giá, sinh email KH</div>
                </div>
                <i class="fa-solid fa-triangle-exclamation text-amber-600 text-sm"></i>
              </button>

              <button onclick="loadSample('rfp_02_chuan_hop_le.txt')" class="w-full text-left p-3 rounded-xl border border-emerald-200 bg-emerald-50/70 hover:bg-emerald-100/70 text-emerald-950 transition flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold">Kịch bản 2: Hồ sơ Chuẩn & Khớp Danh mục</div>
                  <div class="text-[11px] text-emerald-700">Ngân hàng Nam Á &bull; Cisco, Fortinet, Aruba &bull; CK 5% &bull; Tự động chào giá</div>
                </div>
                <i class="fa-solid fa-circle-check text-emerald-600 text-sm"></i>
              </button>

              <button onclick="loadSample('rfp_03_vuot_tham_quyen_va_rui_ro.txt')" class="w-full text-left p-3 rounded-xl border border-rose-200 bg-rose-50/70 hover:bg-rose-100/70 text-rose-950 transition flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold">Kịch bản 3: Rủi ro Cao & Vượt Thẩm quyền</div>
                  <div class="text-[11px] text-rose-700">Palo Alto ngoài catalog &bull; Lịch gấp trễ 28d &bull; CK 16% &rarr; Trình Ban GĐ</div>
                </div>
                <i class="fa-solid fa-fire text-rose-600 text-sm"></i>
              </button>
            </div>
          </div>

          <!-- Textarea -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs font-bold text-slate-700 uppercase tracking-wider">Văn bản yêu cầu chào giá:</label>
              <button onclick="clearInput()" class="text-[11px] text-slate-400 hover:text-slate-600">Xóa trắng</button>
            </div>
            <textarea id="rfp-input" rows="11" class="w-full text-xs font-mono p-3.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none leading-relaxed" placeholder="Dán nội dung hồ sơ mời thầu / RFP / RFQ của khách hàng vào đây..."></textarea>
          </div>

          <!-- Action Button -->
          <button onclick="runProcess()" id="btn-run" class="w-full py-3.5 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-xl shadow-md hover:shadow-lg transition flex items-center justify-center space-x-2">
            <i class="fa-solid fa-bolt"></i>
            <span>CHẠY AI AGENT THẨM ĐỊNH & LẬP BÁO GIÁ</span>
          </button>

        </div>

      </div>

      <!-- Right Column: Results & Interactive Reports (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        
        <!-- Placeholder when empty -->
        <div id="results-placeholder" class="bg-white p-12 rounded-2xl border border-slate-200 shadow-xs text-center">
          <div class="w-16 h-16 bg-sky-50 text-sky-600 rounded-2xl flex items-center justify-center mx-auto mb-4 text-2xl shadow-inner">
            <i class="fa-solid fa-microchip-ai"></i>
          </div>
          <h3 class="text-base font-bold text-slate-800 mb-1">Chưa có kết quả thẩm định</h3>
          <p class="text-xs text-slate-500 max-w-sm mx-auto mb-4">
            Vui lòng chọn 1 trong 3 kịch bản mẫu bên trái hoặc dán nội dung RFP thực tế rồi nhấn nút <strong>"Chạy AI Agent Thẩm định"</strong>.
          </p>
        </div>

        <!-- Live Results Container (Initially hidden) -->
        <div id="results-content" class="hidden space-y-5">
          
          <!-- Banner Result Status -->
          <div id="status-banner" class="p-4 rounded-2xl border shadow-xs flex items-start justify-between">
            <div class="space-y-1">
              <div class="flex items-center space-x-2">
                <span id="status-badge" class="px-2.5 py-0.5 rounded-full text-xs font-bold"></span>
                <h3 id="project-title-display" class="font-bold text-slate-900 text-sm"></h3>
              </div>
              <p id="client-name-display" class="text-xs text-slate-600 font-medium"></p>
            </div>
            <div id="action-badge-container"></div>
          </div>

          <!-- Result Tabs -->
          <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            
            <div class="border-b border-slate-200 flex text-xs font-bold bg-slate-50/80 overflow-x-auto" id="tabs-header">
              <button onclick="switchTab('tab-matrix')" id="btn-tab-matrix" class="px-4 py-3 border-b-2 border-sky-600 text-sky-600 bg-white whitespace-nowrap">
                <i class="fa-solid fa-table-list mr-1.5"></i>Ma trận Đáp ứng Kỹ thuật
              </button>
              <button onclick="switchTab('tab-pricing')" id="btn-tab-pricing" class="px-4 py-3 border-b-2 border-transparent text-slate-600 hover:text-slate-900 whitespace-nowrap">
                <i class="fa-solid fa-coins mr-1.5"></i>Báo Giá & Chiết Khấu
              </button>
              <button onclick="switchTab('tab-schedule')" id="btn-tab-schedule" class="px-4 py-3 border-b-2 border-transparent text-slate-600 hover:text-slate-900 whitespace-nowrap">
                <i class="fa-solid fa-calendar-check mr-1.5"></i>Tiến Độ & Kỹ Sư
              </button>
              <button onclick="switchTab('tab-governance')" id="btn-tab-governance" class="px-4 py-3 border-b-2 border-transparent text-slate-600 hover:text-slate-900 whitespace-nowrap">
                <i class="fa-solid fa-shield-halved mr-1.5"></i>Cờ Cảnh Báo & Cấp Duyệt
              </button>
              <button onclick="switchTab('tab-clarification')" id="btn-tab-clarification" class="hidden px-4 py-3 border-b-2 border-amber-500 text-amber-800 bg-amber-50 whitespace-nowrap">
                <i class="fa-solid fa-envelope-open-text mr-1.5"></i>Dự Thảo Email Làm Rõ
              </button>
            </div>

            <div class="p-5 text-xs">
              
              <!-- Tab 1: Compliance Matrix -->
              <div id="tab-matrix" class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="font-bold text-slate-800">Ma trận đối chiếu yêu cầu bắt buộc vs Giải pháp đề xuất:</span>
                  <span class="text-slate-500 text-[11px]" id="matrix-count"></span>
                </div>
                <div class="overflow-x-auto border border-slate-200 rounded-xl">
                  <table class="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr class="bg-slate-100/80 text-slate-700 text-[11px] uppercase border-b border-slate-200">
                        <th class="p-2.5">Yêu cầu Khách hàng</th>
                        <th class="p-2.5">Giải pháp Thiên Minh</th>
                        <th class="p-2.5">Mức độ Tuân thủ</th>
                        <th class="p-2.5">Dẫn chứng Datasheet</th>
                      </tr>
                    </thead>
                    <tbody id="matrix-body" class="divide-y divide-slate-100"></tbody>
                  </table>
                </div>
              </div>

              <!-- Tab 2: Pricing -->
              <div id="tab-pricing" class="hidden space-y-4">
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                    <div class="text-[11px] text-slate-500 font-medium">Giá Niêm Yết (BOM+BOS)</div>
                    <div id="price-list" class="font-bold text-slate-900 text-sm mt-0.5"></div>
                  </div>
                  <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl">
                    <div class="text-[11px] text-amber-700 font-medium">Chiết khấu (<span id="discount-pct"></span>)</div>
                    <div id="price-discount" class="font-bold text-amber-900 text-sm mt-0.5"></div>
                  </div>
                  <div class="p-3 bg-sky-50 border border-sky-200 rounded-xl">
                    <div class="text-[11px] text-sky-700 font-medium">Giá Chào Trước Thuế</div>
                    <div id="price-final" class="font-bold text-sky-900 text-sm mt-0.5"></div>
                  </div>
                  <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                    <div class="text-[11px] text-emerald-700 font-medium">Biên Lợi Nhuận Gộp</div>
                    <div id="price-margin" class="font-bold text-emerald-900 text-sm mt-0.5"></div>
                  </div>
                </div>

                <div>
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-bold text-slate-800">Dự thảo Bản Chào Giá Thương Mại Hoàn Chỉnh:</h4>
                    <button onclick="printQuotation()" class="text-xs text-sky-600 hover:text-sky-800 font-semibold flex items-center space-x-1">
                      <i class="fa-solid fa-print"></i>
                      <span>In / Xuất Bản Chào Giá</span>
                    </button>
                  </div>
                  <pre id="quotation-pre" class="p-4 bg-slate-900 text-emerald-400 font-mono text-[11px] rounded-xl overflow-x-auto max-h-80 leading-relaxed"></pre>
                </div>
              </div>

              <!-- Tab 3: Schedule & Capacity -->
              <div id="tab-schedule" class="hidden space-y-4">
                <div class="grid grid-cols-3 gap-3">
                  <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="text-slate-500 text-[11px]">Hạn bàn giao KH (Go-live):</div>
                    <div id="sched-client-deadline" class="font-bold text-slate-800 text-sm mt-0.5"></div>
                  </div>
                  <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="text-slate-500 text-[11px]">Dự kiến hoàn tất Thiên Minh:</div>
                    <div id="sched-est-finish" class="font-bold text-slate-800 text-sm mt-0.5"></div>
                  </div>
                  <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="text-slate-500 text-[11px]">Đệm an toàn (Buffer):</div>
                    <div id="sched-buffer" class="font-bold text-sm mt-0.5"></div>
                  </div>
                </div>

                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                  <div class="font-bold text-slate-800">Nguồn lực kỹ sư & Cung ứng thiết bị:</div>
                  <div class="text-slate-600">&bull; Kỹ sư Trưởng phụ trách (CCIE/NSE 7): <strong id="sched-sr-engineer"></strong></div>
                  <div class="text-slate-600">&bull; Đội ngũ Triển khai & Đo kiểm UAT: <strong id="sched-dep-engineer"></strong></div>
                  <div class="text-slate-600">&bull; Thời gian cung ứng thiết bị lớn nhất (Max Lead Time): <strong id="sched-lead-time"></strong></div>
                  <div class="text-slate-600">&bull; Tổng khối lượng công việc: <strong id="sched-man-days"></strong></div>
                </div>

                <div id="sched-bottlenecks-box" class="p-3.5 bg-rose-50 border border-rose-200 rounded-xl hidden">
                  <div class="font-bold text-rose-800 mb-1 flex items-center">
                    <i class="fa-solid fa-triangle-exclamation mr-1.5"></i>Phát hiện Xung đột Tiến độ:
                  </div>
                  <ul id="sched-bottlenecks-list" class="list-disc list-inside text-rose-700 space-y-1"></ul>
                </div>
              </div>

              <!-- Tab 4: Governance & Red Flags -->
              <div id="tab-governance" class="hidden space-y-4">
                <div class="p-4 rounded-xl border" id="gov-authority-box">
                  <div class="text-xs text-slate-500 font-medium">Cấp thẩm quyền phê duyệt bắt buộc:</div>
                  <div id="gov-approver-name" class="font-bold text-base mt-0.5"></div>
                  <div id="gov-action-desc" class="text-xs mt-1 text-slate-600"></div>
                </div>

                <div>
                  <h4 class="font-bold text-slate-800 mb-2">Các Cờ Báo Động Kích Hoạt (Escalation Triggers):</h4>
                  <div id="gov-triggers-list" class="space-y-2"></div>
                </div>

                <div class="p-3.5 bg-sky-50 border border-sky-200 rounded-xl">
                  <h4 class="font-bold text-sky-900 mb-1.5">Gợi ý phương án giải quyết cho Người duyệt:</h4>
                  <ul id="gov-mitigations-list" class="list-disc list-inside text-sky-800 space-y-1"></ul>
                </div>
              </div>

              <!-- Tab 5: Clarification Request Draft -->
              <div id="tab-clarification" class="hidden space-y-3">
                <div class="p-3.5 bg-amber-50 border border-amber-200 rounded-xl text-amber-900">
                  <div class="font-bold mb-1 flex items-center">
                    <i class="fa-solid fa-circle-exclamation mr-1.5"></i>Chưa đủ điều kiện báo giá &rarr; Kích hoạt luồng làm rõ!
                  </div>
                  <p class="text-xs">
                    Để không bỏ sót điều kiện bắt buộc, Sales cần gửi văn bản này cho khách hàng để xác minh trước khi chuyển cho Kỹ thuật & Vận hành.
                  </p>
                </div>
                <div>
                  <div class="flex items-center justify-between mb-1.5">
                    <span class="font-bold text-slate-700">Dự thảo công văn / Email làm rõ do AI soạn sẵn:</span>
                    <button onclick="copyClarification()" class="text-sky-600 hover:text-sky-800 font-semibold text-xs">
                      <i class="fa-regular fa-copy mr-1"></i>Sao chép văn bản
                    </button>
                  </div>
                  <textarea id="clarification-textarea" rows="12" class="w-full text-xs font-mono p-3.5 bg-slate-50 border border-slate-300 rounded-xl leading-relaxed"></textarea>
                </div>
              </div>

            </div>

          </div>

          <!-- HITL Approval Bar -->
          <div id="hitl-panel" class="bg-gradient-to-r from-sky-50 to-blue-50 p-4 rounded-2xl border border-sky-200 shadow-xs flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-bold text-sm text-slate-900 flex items-center">
                <i class="fa-solid fa-user-check text-sky-600 mr-2"></i>Thẩm định & Kiểm tra Ranh giới Dữ liệu (HITL)
              </div>
              <div class="text-xs text-slate-500">Phê duyệt chéo giữa 3 bộ phận: Kinh doanh + Kỹ thuật + Vận hành</div>
            </div>
            <div class="flex items-center space-x-2" id="hitl-btn-group">
              <button onclick="submitHITL(false)" class="px-4 py-2 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold rounded-xl text-xs transition">
                <i class="fa-solid fa-rotate-left mr-1"></i>Yêu Cầu Chỉnh Sửa
              </button>
              <button onclick="submitHITL(true)" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow transition">
                <i class="fa-solid fa-check mr-1"></i>Phê Duyệt & Xuất Chào Giá
              </button>
            </div>
          </div>

        </div>

      </div>

    </div>

  </main>

  <!-- MASTER CATALOG SECTION (Trưng bày danh mục giải pháp như mẫu card e-commerce) -->
  <section id="catalog-section" class="py-12 bg-white border-t border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="flex items-end justify-between mb-8">
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-sky-600 mb-1">DANH MỤC THIẾT BỊ MASTER CỦA THIÊN MINH</div>
          <h3 class="font-display text-2xl font-bold text-slate-900">Giải Pháp Thiết Bị Mạng & Tường Lửa Chính Hãng</h3>
        </div>
        <span class="text-xs text-slate-500">Đối tác phân phối ủy quyền: Cisco &bull; Fortinet &bull; Aruba &bull; Ruijie</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" id="catalog-grid">
        <!-- Rendered by JS from master_products -->
      </div>

    </div>
  </section>

  <!-- POLICY & GOVERNANCE SECTION -->
  <section id="policy-section" class="py-12 bg-slate-50 border-t border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="max-w-3xl mx-auto text-center mb-8">
        <h3 class="font-display text-2xl font-bold text-slate-900">Ranh Giới Dữ Liệu & Quy Chế Chuyển Duyệt Thẩm Quyền</h3>
        <p class="text-xs text-slate-600 mt-1">Đảm bảo an toàn tài chính, biên lợi nhuận công ty và cam kết năng lực thực thi</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-5 bg-white rounded-2xl border border-slate-200 shadow-xs">
          <div class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm mb-3">1</div>
          <h4 class="font-bold text-slate-900 text-sm">Nhân Viên Kinh Doanh</h4>
          <p class="text-xs text-slate-600 mt-1">Chiết khấu &le; 8.0%, Gross Margin &ge; 22%, 100% thiết bị trong Master Catalog, lịch an toàn &ge; 10 ngày.</p>
        </div>
        <div class="p-5 bg-white rounded-2xl border border-amber-200 bg-amber-50/30 shadow-xs">
          <div class="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm mb-3">2</div>
          <h4 class="font-bold text-slate-900 text-sm">Trưởng Phòng Kinh Doanh</h4>
          <p class="text-xs text-slate-600 mt-1">Chiết khấu 8.1% - 12.0%, hoặc tư vấn model tương đương, lịch đệm an toàn 5-9 ngày.</p>
        </div>
        <div class="p-5 bg-white rounded-2xl border border-rose-200 bg-rose-50/30 shadow-xs">
          <div class="w-8 h-8 rounded-lg bg-rose-100 text-rose-800 flex items-center justify-center font-bold text-sm mb-3">3</div>
          <h4 class="font-bold text-slate-900 text-sm">Ban Giám Đốc (CEO)</h4>
          <p class="text-xs text-slate-600 mt-1">Chiết khấu &gt; 12.0%, thiết bị ngoài catalog, lịch gấp trễ hạn, SLA 24/7/2h, hoặc lãi gộp &lt; 22%.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-slate-900 text-slate-400 py-10 border-t border-slate-800 text-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
      <div>
        <div class="font-bold text-white text-sm mb-1">CÔNG TY CỔ PHẦN CÔNG NGHỆ THIÊN MINH</div>
        <p class="text-slate-400 text-xs">Tầng 8, Tòa nhà Công nghệ, Cầu Giấy, Hà Nội | Hotline: (024) 3888 xxxx</p>
      </div>
      <div class="text-slate-500 text-[11px] text-center md:text-right">
        &copy; 2026 Thien Minh Technology JSC. All rights reserved.<br>
        Hệ thống AI Agent tự động hóa đánh giá yêu cầu chào giá dự án.
      </div>
    </div>
  </footer>

  <!-- FLOATING AI CHAT WIDGET -->
  <div class="fixed bottom-6 right-6 z-50">
    <button onclick="toggleChat()" class="w-13 h-13 rounded-full bg-sky-600 hover:bg-sky-700 text-white shadow-xl flex items-center justify-center text-xl hover:scale-105 transition duration-200">
      <i class="fa-solid fa-headset"></i>
    </button>
    <div id="ai-chat-box" class="absolute bottom-16 right-0 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-slate-200 hidden flex flex-col overflow-hidden" style="height: 480px;">
      <div class="p-3.5 bg-slate-900 text-white flex items-center justify-between">
        <div class="font-bold text-xs flex items-center">
          <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2"></span>
          Trợ Lý AI Thẩm Định RFP Thiên Minh
        </div>
        <button onclick="toggleChat()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div id="chat-logs" class="flex-1 p-3 overflow-y-auto space-y-2 text-xs bg-slate-50">
        <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-xs text-slate-700">
          Xin chào! Tôi là Trợ lý AI của Thiên Minh. Tôi có thể giải đáp thông số thiết bị, chính sách giá, lịch năng lực kỹ sư hoặc phân tích RFP giúp bạn. Bạn cần hỗ trợ gì?
        </div>
      </div>
      <div class="p-2.5 bg-white border-t border-slate-200 flex items-center space-x-2">
        <input type="text" id="chat-msg" onkeypress="if(event.key==='Enter') sendChat()" placeholder="Hỏi về thiết bị, giá, lead time..." class="flex-1 text-xs px-3 py-2 border rounded-lg outline-none">
        <button onclick="sendChat()" class="px-3 py-2 bg-sky-600 text-white rounded-lg text-xs font-bold"><i class="fa-solid fa-paper-plane"></i></button>
      </div>
    </div>
  </div>

  <script>
    let currentPkg = null;

    async function loadCatalog() {
      const res = await fetch('/api/products');
      const products = await res.json();
      const grid = document.getElementById('catalog-grid');
      grid.innerHTML = '';
      products.forEach(p => {
        const card = document.createElement('div');
        card.className = "p-5 bg-slate-50 rounded-2xl border border-slate-200 card-hover flex flex-col justify-between";
        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800">${p.brand} &bull; ${p.category}</span>
              <span class="text-[11px] text-slate-500">Lead time: <strong>${p.lead_time_days} ngày</strong></span>
            </div>
            <h4 class="font-bold text-slate-900 text-sm mb-1">${p.name}</h4>
            <div class="text-xs text-sky-700 font-bold mb-2">${new Intl.NumberFormat('vi-VN').format(p.standard_price_vnd)} VNĐ</div>
            <div class="space-y-1 text-[11px] text-slate-600">
              ${p.specs.ports ? `<div>&bull; Cổng: ${p.specs.ports}</div>` : ''}
              ${p.specs.layer ? `<div>&bull; Định tuyến: ${p.specs.layer}</div>` : ''}
              ${p.specs.poe_budget_watt ? `<div>&bull; Công suất PoE: ${p.specs.poe_budget_watt}W</div>` : ''}
              ${p.specs.threat_protection ? `<div>&bull; Threat Protection: ${p.specs.threat_protection}</div>` : ''}
              ${p.specs.standard ? `<div>&bull; Chuẩn WiFi: ${p.specs.standard}</div>` : ''}
            </div>
          </div>
          <div class="pt-3 mt-3 border-t border-slate-200 text-[10px] text-slate-400">
            Mã định danh: ${p.id} &bull; BH: ${p.warranty_months} tháng
          </div>
        `;
        grid.appendChild(card);
      });
    }

    async function loadSample(filename) {
      const res = await fetch('/api/sample?name=' + encodeURIComponent(filename));
      const data = await res.json();
      document.getElementById('rfp-input').value = data.content;
      document.getElementById('rfp-input').scrollIntoView({ behavior: 'smooth' });
    }

    function clearInput() {
      document.getElementById('rfp-input').value = '';
    }

    async function runProcess() {
      const text = document.getElementById('rfp-input').value.trim();
      if (!text) {
        alert('Vui lòng nhập hoặc chọn một hồ sơ RFP!');
        return;
      }

      const btn = document.getElementById('btn-run');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Đang phân tích & đối chiếu...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ rfp_text: text })
        });
        const pkg = await res.json();
        currentPkg = pkg;
        renderResults(pkg);
      } catch (err) {
        alert('Lỗi xử lý: ' + err);
      } finally {
        btn.innerHTML = '<i class="fa-solid fa-bolt mr-2"></i>CHẠY AI AGENT THẨM ĐỊNH & LẬP BÁO GIÁ';
        btn.disabled = false;
      }
    }

    function renderResults(pkg) {
      document.getElementById('results-placeholder').classList.add('hidden');
      document.getElementById('results-content').classList.remove('hidden');

      document.getElementById('project-title-display').innerText = pkg.project_title;
      document.getElementById('client-name-display').innerText = 'Khách hàng: ' + pkg.client_name + ' | Mã RFP: ' + pkg.rfp_id;

      resetFlowSteps();
      document.getElementById('step-1').className = 'p-3 rounded-xl border step-pass transition-all';
      document.getElementById('step-2').className = 'p-3 rounded-xl border step-pass transition-all';

      const isComplete = pkg.completeness && pkg.completeness.is_complete;
      const statusBadge = document.getElementById('status-badge');
      const actionContainer = document.getElementById('action-badge-container');
      const tabClarificationBtn = document.getElementById('btn-tab-clarification');

      if (!isComplete) {
        document.getElementById('step-3').className = 'p-3 rounded-xl border step-warn transition-all';
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800';
        statusBadge.innerText = 'THIẾU THÔNG TIN (GATE 1: KHÔNG ĐẠT)';
        actionContainer.innerHTML = '<span class="text-xs bg-amber-100 text-amber-900 font-bold px-3 py-1 rounded-lg">Kinh doanh liên hệ KH làm rõ</span>';

        tabClarificationBtn.classList.remove('hidden');
        document.getElementById('clarification-textarea').value = pkg.completeness.clarification_email_draft || '';
        switchTab('tab-clarification');
        document.getElementById('hitl-panel').classList.add('hidden');
        return;
      }

      document.getElementById('step-3').className = 'p-3 rounded-xl border step-pass transition-all';
      document.getElementById('step-4').className = 'p-3 rounded-xl border step-pass transition-all';
      document.getElementById('step-5').className = 'p-3 rounded-xl border step-pass transition-all';
      document.getElementById('step-6').className = 'p-3 rounded-xl border step-pass transition-all';

      tabClarificationBtn.classList.add('hidden');
      document.getElementById('hitl-panel').classList.remove('hidden');

      const hasEscalation = pkg.escalation && pkg.escalation.requires_escalation;
      if (hasEscalation) {
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800';
        statusBadge.innerText = 'CẦN CHUYỂN DUYỆT CẤP CAO (GATE 2: CÓ)';
        actionContainer.innerHTML = '<span class="text-xs bg-rose-100 text-rose-800 font-bold px-3 py-1 rounded-lg">' + pkg.escalation.approver_name + '</span>';
      } else {
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800';
        statusBadge.innerText = 'ĐẠT CHUẨN TIÊU CHUẨN (GATE 2: KHÔNG)';
        actionContainer.innerHTML = '<span class="text-xs bg-emerald-100 text-emerald-800 font-bold px-3 py-1 rounded-lg">Sales Rep tự quyết</span>';
      }

      // Matrix
      const matrixBody = document.getElementById('matrix-body');
      matrixBody.innerHTML = '';
      if (pkg.compliance_matrix) {
        document.getElementById('matrix-count').innerText = `${pkg.compliance_matrix.length} tiêu chí thẩm định`;
        pkg.compliance_matrix.forEach(row => {
          let bClass = 'bg-emerald-100 text-emerald-800 font-semibold';
          if (row.compliance_status.includes('Không') || row.compliance_status.includes('Ngoài')) {
            bClass = 'bg-rose-100 text-rose-800 font-bold';
          } else if (row.compliance_status.includes('Cần')) {
            bClass = 'bg-amber-100 text-amber-800 font-bold';
          } else if (row.compliance_status.includes('Vượt')) {
            bClass = 'bg-sky-100 text-sky-800 font-bold';
          }

          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50/60';
          tr.innerHTML = `
            <td class="p-2.5 font-bold text-slate-800">${row.client_requirement}</td>
            <td class="p-2.5">${row.thien_minh_solution}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded text-[10px] ${bClass}">${row.compliance_status}</span></td>
            <td class="p-2.5 text-slate-500 text-[11px]">${row.technical_proof}</td>
          `;
          matrixBody.appendChild(tr);
        });
      }

      // Pricing
      if (pkg.pricing) {
        const fmt = v => new Intl.NumberFormat('vi-VN').format(Math.round(v)) + ' đ';
        document.getElementById('price-list').innerText = fmt(pkg.pricing.total_list_price);
        document.getElementById('discount-pct').innerText = (pkg.pricing.requested_discount_rate * 100).toFixed(1) + '%';
        document.getElementById('price-discount').innerText = '- ' + fmt(pkg.pricing.discount_amount);
        document.getElementById('price-final').innerText = fmt(pkg.pricing.final_quoted_price);
        document.getElementById('price-margin').innerText = (pkg.pricing.gross_margin_rate * 100).toFixed(1) + '% (' + fmt(pkg.pricing.gross_margin_amount) + ')';
      }

      // Schedule
      if (pkg.schedule_feasibility) {
        const s = pkg.schedule_feasibility;
        document.getElementById('sched-client-deadline').innerText = s.customer_deadline || 'Không xác định';
        document.getElementById('sched-est-finish').innerText = s.estimated_finish_date;
        const bEl = document.getElementById('sched-buffer');
        bEl.innerText = (s.buffer_days >= 0 ? '+' : '') + s.buffer_days + ' ngày';
        bEl.className = s.buffer_days >= 5 ? 'font-bold text-sm text-emerald-600' : 'font-bold text-sm text-rose-600';

        document.getElementById('sched-sr-engineer').innerText = s.assigned_senior_engineer || 'Kỹ sư Trưởng CCIE/NSE 7';
        document.getElementById('sched-dep-engineer').innerText = s.assigned_deployment_engineer || 'Kỹ sư CCNP/NSE 4';
        document.getElementById('sched-lead-time').innerText = s.max_lead_time_days + ' ngày';
        document.getElementById('sched-man-days').innerText = s.deployment_man_days + ' man-days';

        const bBox = document.getElementById('sched-bottlenecks-box');
        const bList = document.getElementById('sched-bottlenecks-list');
        bList.innerHTML = '';
        if (s.bottlenecks && s.bottlenecks.length > 0) {
          bBox.classList.remove('hidden');
          s.bottlenecks.forEach(b => {
            const li = document.createElement('li');
            li.innerText = b;
            bList.appendChild(li);
          });
        } else {
          bBox.classList.add('hidden');
        }
      }

      // Governance
      if (pkg.escalation) {
        const esc = pkg.escalation;
        const box = document.getElementById('gov-authority-box');
        box.className = esc.requires_escalation ? 'p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-900' : 'p-4 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-900';
        document.getElementById('gov-approver-name').innerText = esc.approver_name;
        document.getElementById('gov-action-desc').innerText = esc.action_required;

        const trigList = document.getElementById('gov-triggers-list');
        trigList.innerHTML = '';
        if (esc.triggers && esc.triggers.length > 0) {
          esc.triggers.forEach(t => {
            const div = document.createElement('div');
            div.className = "p-3 rounded-xl border border-slate-200 bg-slate-50 flex items-start space-x-2";
            div.innerHTML = `
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${t.severity==='CRITICAL'?'bg-rose-600 text-white':'bg-amber-500 text-white'}">${t.severity}</span>
              <div>
                <strong class="text-slate-900">${t.title}:</strong>
                <p class="text-slate-600 text-xs mt-0.5">${t.detail}</p>
              </div>
            `;
            trigList.appendChild(div);
          });
        } else {
          trigList.innerHTML = '<div class="text-emerald-700 italic">Không có cờ cảnh báo ngoại lệ. Mọi chỉ số tuân thủ chính sách tiêu chuẩn.</div>';
        }

        const mitList = document.getElementById('gov-mitigations-list');
        mitList.innerHTML = '';
        if (esc.mitigation_suggestions && esc.mitigation_suggestions.length > 0) {
          esc.mitigation_suggestions.forEach(m => {
            const li = document.createElement('li');
            li.innerText = m;
            mitList.appendChild(li);
          });
        } else {
          mitList.innerHTML = '<li>Áp dụng hợp đồng và điều khoản chào giá chuẩn của công ty.</li>';
        }
      }

      // Raw quotation
      fetch('/api/quotation-text')
        .then(r => r.json())
        .then(d => {
          document.getElementById('quotation-pre').innerText = d.quotation_text;
        });

      switchTab('tab-matrix');
    }

    function resetFlowSteps() {
      for (let i = 1; i <= 6; i++) {
        document.getElementById('step-' + i).className = 'p-3 rounded-xl border border-slate-200 bg-slate-50 transition-all';
      }
    }

    function switchTab(tabId) {
      const tabs = ['tab-matrix', 'tab-pricing', 'tab-schedule', 'tab-governance', 'tab-clarification'];
      tabs.forEach(t => {
        const el = document.getElementById(t);
        const btn = document.getElementById('btn-' + t);
        if (el && btn) {
          if (t === tabId) {
            el.classList.remove('hidden');
            btn.className = 'px-4 py-3 border-b-2 border-sky-600 text-sky-600 bg-white font-bold whitespace-nowrap';
          } else {
            el.classList.add('hidden');
            btn.className = 'px-4 py-3 border-b-2 border-transparent text-slate-600 hover:text-slate-900 font-semibold whitespace-nowrap';
          }
        }
      });
    }

    function copyClarification() {
      const ta = document.getElementById('clarification-textarea');
      ta.select();
      document.execCommand('copy');
      alert('Đã sao chép nội dung văn bản làm rõ!');
    }

    function printQuotation() {
      const w = window.open('', '_blank');
      w.document.write('<pre style="font-family: monospace; white-space: pre-wrap; font-size: 13px;">' + document.getElementById('quotation-pre').innerText + '</pre>');
      w.document.close();
      w.print();
    }

    async function submitHITL(approved) {
      if (!currentPkg) return;
      const approver = prompt('Họ tên người kiểm duyệt (KD / Kỹ thuật / Vận hành / Giám đốc):', 'Trưởng phòng Kinh doanh');
      if (!approver) return;
      const note = prompt('Ghi chú kiểm duyệt:', approved ? 'Đạt chuẩn' : 'Cần rà soát lại phương án');

      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: approved, approver: approver, feedback: note })
      });
      const data = await res.json();
      if (approved) {
        alert('ĐÃ PHÊ DUYỆT XUẤT BẢN CHÀO GIÁ THÀNH CÔNG! Sẵn sàng gửi khách hàng.');
        document.getElementById('hitl-btn-group').innerHTML = '<span class="text-xs bg-emerald-600 text-white font-bold px-4 py-2 rounded-xl"><i class="fa-solid fa-check-circle mr-1"></i>Đã Phê Duyệt Xuất Bản</span>';
      } else {
        alert('Hồ sơ đã được chuyển trạng thái: CẦN CHỈNH SỬA.');
        document.getElementById('hitl-btn-group').innerHTML = '<span class="text-xs bg-rose-600 text-white font-bold px-4 py-2 rounded-xl"><i class="fa-solid fa-rotate-left mr-1"></i>Yêu cầu sửa đổi</span>';
      }
    }

    function toggleChat() {
      document.getElementById('ai-chat-box').classList.toggle('hidden');
    }

    async function sendChat() {
      const inp = document.getElementById('chat-msg');
      const text = inp.value.trim();
      if (!text) return;
      const logs = document.getElementById('chat-logs');
      logs.innerHTML += `<div class="bg-sky-600 text-white p-2 rounded-xl text-xs text-right max-w-[85%] ml-auto">${text}</div>`;
      inp.value = '';

      const res = await fetch('/api/chat-advisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      logs.innerHTML += `<div class="bg-white p-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs shadow-xs">${data.reply}</div>`;
      logs.scrollTop = logs.scrollHeight;
    }

    loadCatalog();
  </script>
</body>
</html>
"""

class ThienMinhHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path == "/" or path == "/index.html":
            self._send_response(200, "text/html; charset=utf-8", HTML_PAGE.encode("utf-8"))

        elif path == "/api/products":
            self._send_json(master_products)

        elif path == "/api/sample":
            params = urllib.parse.parse_qs(url.query)
            name = params.get("name", ["rfp_02_chuan_hop_le.txt"])[0]
            clean_name = os.path.basename(name)
            filepath = os.path.join(BASE_DIR, "samples", clean_name)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self._send_json({"filename": clean_name, "content": content})
            else:
                self.send_error(404, "Sample not found")

        elif path == "/api/quotation-text":
            global current_package
            if current_package and current_package.pricing and current_package.schedule_feasibility:
                decomp = orchestrator.extract_agent.extract_and_decompose(current_package.audit_trail[0]["message"])
                txt = orchestrator.proposal_agent.generate_quotation_text(
                    decomp,
                    current_package.catalog_matches,
                    current_package.pricing,
                    current_package.schedule_feasibility
                )
                self._send_json({"quotation_text": txt})
            else:
                self._send_json({"quotation_text": "Chưa có dữ liệu bảng chào giá."})

        else:
            self.send_error(404)

    def do_POST(self):
        global current_package
        url = urllib.parse.urlparse(self.path)
        path = url.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(body)

        if path == "/api/process":
            rfp_text = payload.get("rfp_text", "")
            pkg = orchestrator.process_rfp(rfp_text)
            current_package = pkg
            self._send_json(pkg.to_dict())

        elif path == "/api/approve":
            approved = payload.get("approved", True)
            approver = payload.get("approver", "Người kiểm duyệt")
            feedback = payload.get("feedback", "")
            if current_package:
                current_package = orchestrator.apply_hitl_approval(current_package, approver, approved, feedback)
                self._send_json(current_package.to_dict())
            else:
                self.send_error(400, "No active package")

        elif path == "/api/chat-advisor":
            msg = payload.get("message", "").lower()
            if any(w in msg for w in ["chính sách", "chiết khấu"]):
                reply = "Chính sách chiết khấu chuẩn của Thiên Minh: Sales Rep tự quyết &le;8%, Trưởng phòng KD duyệt 8.1% - 12%, Ban Giám đốc duyệt &gt;12% hoặc Gross Margin &lt;22%."
            elif any(w in msg for w in ["palo alto", "ngoài catalog"]):
                reply = "Palo Alto hiện nằm ngoài Master Catalog của Thiên Minh. Nếu khách hàng yêu cầu, hệ thống sẽ kích hoạt cờ đỏ chuyển Trưởng phòng Kỹ thuật và Ban Giám đốc phê duyệt."
            elif any(w in msg for w in ["tiến độ", "kỹ sư"]):
                reply = "Thiên Minh hiện có 2 Kỹ sư Trưởng (CCIE/NSE 7) và 4 Kỹ sư triển khai (CCNP/NSE 4). Lead time thiết bị Cisco là 7-10 ngày, Fortinet 5-10 ngày, Aruba 5 ngày."
            else:
                reply = f"Hệ thống đã nhận câu hỏi: '{msg}'. Bạn có thể chọn 1 trong 3 kịch bản mẫu ở giao diện chính để AI Agent thực hiện thẩm định tự động ngay!"
            self._send_json({"reply": reply})

        else:
            self.send_error(404)

    def _send_response(self, code, content_type, body_bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body_bytes)

    def _send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send_response(200, "application/json; charset=utf-8", body)

def start_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), ThienMinhHandler)
    print(f"""
================================================================================
  🚀 THIÊN MINH AI AGENT PORTAL IS RUNNING LOCALLY!
  👉 Mở trình duyệt và truy cập: http://localhost:{port}
================================================================================
  - Thẩm định RFP/RFQ tự động theo lưu đồ quy trình nghiệp vụ Thiên Minh
  - Ma trận đáp ứng kỹ thuật & Bảng chào giá tự động
  - Phân cấp phê duyệt HITL: Sales Rep &bull; Trưởng phòng &bull; Ban Giám đốc
================================================================================
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Dừng server Thiên Minh.")
    finally:
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)
