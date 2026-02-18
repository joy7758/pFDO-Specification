# product_api/ui.py
# 前端极简高级风 UI 渲染逻辑 (Apple/Microsoft 极简风格)

import json
from typing import Dict, Any, List

def _base_css() -> str:
    """返回极简风格 CSS (深灰/白/深红)"""
    return """
    <style>
        :root {
            --primary-red: #C62828;
            --primary-hover: #B71C1C;
            --bg-body: #F5F5F7;
            --bg-card: #FFFFFF;
            --text-dark: #1D1D1F;
            --text-grey: #86868B;
            --border-light: #E5E5E5;
            --shadow-subtle: 0 4px 12px rgba(0,0,0,0.03);
            --radius-card: 16px;
            --font-stack: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: var(--font-stack);
            background-color: var(--bg-body);
            color: var(--text-dark);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }

        a { text-decoration: none; color: inherit; transition: opacity 0.2s; }
        a:hover { opacity: 0.7; }

        /* 布局容器 */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* 顶部导航 */
        header {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
            position: sticky;
            top: 0;
            z-index: 1000;
            padding: 0 20px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo { font-weight: 600; font-size: 18px; color: var(--text-dark); display: flex; align-items: center; gap: 8px; }
        .logo::before { content: ''; width: 12px; height: 12px; background: var(--primary-red); border-radius: 50%; display: inline-block; }
        
        .nav-links { display: flex; gap: 24px; font-size: 14px; font-weight: 500; }
        .nav-links a.active { color: var(--primary-red); }

        /* 卡片 */
        .card {
            background: var(--bg-card);
            border-radius: var(--radius-card);
            padding: 24px;
            box-shadow: var(--shadow-subtle);
            border: 1px solid rgba(0,0,0,0.02);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-2px); }

        h1 { font-size: 40px; font-weight: 700; margin-bottom: 16px; letter-spacing: -0.02em; }
        h2 { font-size: 24px; font-weight: 600; margin-bottom: 12px; }
        h3 { font-size: 18px; font-weight: 600; margin-bottom: 8px; color: var(--text-dark); }
        p { color: var(--text-grey); font-size: 16px; margin-bottom: 24px; line-height: 1.6; }

        /* 按钮 */
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 99px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        .btn-primary { background: var(--primary-red); color: white; }
        .btn-primary:hover { background: var(--primary-hover); transform: scale(1.02); opacity: 1; }
        .btn-secondary { background: #F5F5F7; color: var(--text-dark); }
        .btn-secondary:hover { background: #E5E5EA; opacity: 1; }
        .btn-outline { border: 1px solid var(--border-light); background: transparent; color: var(--text-grey); }
        .btn-outline:hover { border-color: var(--text-grey); color: var(--text-dark); opacity: 1; }

        /* 栅格系统 */
        .grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px; }
        .col-3 { grid-column: span 3; }
        .col-4 { grid-column: span 4; }
        .col-5 { grid-column: span 5; }
        .col-6 { grid-column: span 6; }
        .col-7 { grid-column: span 7; }
        .col-8 { grid-column: span 8; }
        .col-9 { grid-column: span 9; }
        .col-12 { grid-column: span 12; }

        @media (max-width: 1024px) {
            .col-3, .col-4, .col-5, .col-6, .col-7, .col-8, .col-9 { grid-column: span 12; }
        }

        /* 标签 */
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .tag-red { background: #FFEBEE; color: #C62828; }
        .tag-orange { background: #FFF3E0; color: #EF6C00; }
        .tag-green { background: #E8F5E9; color: #2E7D32; }
        .tag-blue { background: #E3F2FD; color: #1565C0; }
        .tag-grey { background: #EEEEEE; color: #616161; }

        /* 代码块 */
        pre {
            background: #F5F5F7;
            padding: 16px;
            border-radius: 12px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 13px;
            color: #333;
            border: 1px solid rgba(0,0,0,0.05);
        }

        /* 列表 */
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-light);
        }
        .list-item:last-child { border-bottom: none; }

        /* Ticker 组件 */
        .ticker-container {
            width: 100%;
            height: 48px;
            background: #fff;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            padding: 0 20px;
            font-size: 14px;
            overflow: hidden;
            position: relative;
            z-index: 2000;
        }
        .ticker-item {
            display: none;
            align-items: center;
            width: 100%;
            animation: fadeIn 0.5s ease-in-out;
            cursor: pointer;
        }
        .ticker-item.active { display: flex; }
        .ticker-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
            white-space: nowrap;
        }
        .ticker-title { font-weight: 600; margin-right: 8px; white-space: nowrap; }
        .ticker-text { color: var(--text-dark); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .ticker-arrow { color: var(--text-grey); margin-left: 12px; font-size: 12px; }

        /* Ticker Modal */
        .ticker-modal {
            display: none;
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 600px;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            border-radius: 12px;
            padding: 24px;
            z-index: 2001;
            animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .ticker-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .ticker-modal-title { font-size: 18px; font-weight: 600; }
        .ticker-modal-close { cursor: pointer; color: var(--text-grey); font-size: 24px; line-height: 1; }
        .ticker-modal-content { font-size: 15px; line-height: 1.6; color: var(--text-dark); }
        .ticker-modal-meta { margin-top: 16px; font-size: 12px; color: var(--text-grey); }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translate(-50%, -10px); }
            to { opacity: 1; transform: translate(-50%, 0); }
        }
        
        /* 遮罩 */
        .ticker-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.2);
            z-index: 2000;
            backdrop-filter: blur(2px);
        }
    </style>
    """

def _page_layout(title: str, content: str, active_tab: str = "") -> str:
    """页面通用布局"""
    nav_links = {
        "/": "首页",
        "/demo": "企业检测",
        "/park": "园区大屏",
        "/docs-cn": "接口文档"
    }
    nav_html = ""
    for link, name in nav_links.items():
        cls = "active" if link == active_tab else ""
        nav_html += f'<a href="{link}" class="{cls}">{name}</a>'

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - 红岩数字合规</title>
        {_base_css()}
    </head>
    <body>
        <div id="top-ticker" class="ticker-container" style="display:none;">
            <!-- Ticker items injected here -->
        </div>
        
        <!-- Ticker Modal & Overlay -->
        <div id="ticker-overlay" class="ticker-overlay" onclick="closeTickerModal()"></div>
        <div id="ticker-modal" class="ticker-modal">
            <div class="ticker-modal-header">
                <div class="ticker-modal-title" id="ticker-modal-title">标题</div>
                <div class="ticker-modal-close" onclick="closeTickerModal()">×</div>
            </div>
            <div class="ticker-modal-content" id="ticker-modal-body">内容</div>
            <div class="ticker-modal-meta" id="ticker-modal-meta">来源：系统</div>
        </div>

        <header>
            <a href="/" class="logo">红岩 · 园区数字合规共建平台</a>
            <nav class="nav-links">
                {nav_html}
            </nav>
        </header>
        {content}
        <footer style="text-align: center; padding: 40px; color: var(--text-grey); font-size: 13px; border-top: 1px solid var(--border-light); margin-top: 40px;">
            <p style="margin-bottom: 8px;">红岩 · 园区数字合规共建平台 v1.0.0</p>
            <p style="font-size: 12px;">&copy; 2026 RedRock Digital Compliance. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """

def render_home() -> str:
    content = """
    <div style="text-align: center; padding: 80px 20px 60px;">
        <h1 style="font-size: 56px; line-height: 1.1; margin-bottom: 24px;">
            园区级数字合规基础设施<br>
            <span style="color: var(--primary-red);">实时审计 · 风险治理 · 数据中枢</span>
        </h1>
        <p style="font-size: 20px; max-width: 700px; margin: 0 auto 40px;">
            基于架构师主权模式打造的企业级敏感数据扫描引擎。<br>
            支持全量数据实时审计，提供秒级合规反馈，构建安全可信的园区数字生态。
        </p>
        <div style="display: flex; gap: 16px; justify-content: center;">
            <a href="/park" class="btn btn-primary" style="padding: 14px 32px; font-size: 16px;">进入园区大屏</a>
            <a href="/demo" class="btn btn-secondary" style="padding: 14px 32px; font-size: 16px;">企业合规自测</a>
            <a href="/docs-cn" class="btn btn-outline" style="padding: 14px 32px; font-size: 16px;">接口文档</a>
        </div>
    </div>

    <div class="container">
        <div class="grid-12">
            <div class="col-4 card">
                <div style="font-size: 32px; margin-bottom: 16px;">⚡️</div>
                <h3>毫秒级实时监测</h3>
                <p style="margin-bottom: 0;">基于流式处理架构，对上传数据进行毫秒级 PII 扫描，精准识别手机号、邮箱与身份证信息。</p>
            </div>
            <div class="col-4 card">
                <div style="font-size: 32px; margin-bottom: 16px;">📊</div>
                <h3>全景风险可视</h3>
                <p style="margin-bottom: 0;">直观的风险仪表盘，多维度展示园区整体合规态势，助力管理者快速决策。</p>
            </div>
            <div class="col-4 card">
                <div style="font-size: 32px; margin-bottom: 16px;">🔗</div>
                <h3>开放生态集成</h3>
                <p style="margin-bottom: 0;">提供标准 RESTful API，支持第三方系统快速接入，共建园区数字合规生态。</p>
            </div>
        </div>
    </div>
    """
    return _page_layout("首页", content, "/")

def render_demo_page() -> str:
    script = """
    <script>
        function fillExample() {
            const example = `这是一段包含敏感信息的示例文本：
1. 客户张三，手机号码是 13812345678，用于接收短信通知。
2. 运营总监李四，工作邮箱为 lisi.work@example-company.com，请勿外传。
3. 临时工王五，身份证号 110101199001011234，入职手续已办理。
4. 其他干扰项：订单号 202305010001，客服电话 400-800-8888（非手机号）。`;
            document.getElementById('text-input').value = example;
        }
    </script>
    """
    content = f"""
    <div class="container" style="max-width: 800px;">
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>企业数据合规检测</h1>
            <p>粘贴文本内容，快速检测潜在的隐私泄露风险。</p>
        </div>
        
        <div class="card">
            <form action="/demo/scan" method="post">
                <textarea id="text-input" name="text" placeholder="在此粘贴包含敏感信息（手机号/邮箱/身份证）的文本内容..." style="min-height: 240px; width: 100%; border: 1px solid #ddd; padding: 10px; border-radius: 8px; font-family: inherit;"></textarea>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px;">
                    <button type="button" class="btn btn-secondary" onclick="fillExample()">加载测试样本</button>
                    <button type="submit" class="btn btn-primary">启动合规检测</button>
                </div>
            </form>
        </div>
    </div>
    {script}
    """
    return _page_layout("企业检测", content, "/demo")

def render_demo_result(text: str, result: Dict[str, Any]) -> str:
    summary = result.get("summary", {})
    hits = result.get("per_record", [{}])[0].get("hits", {})
    
    highlighted = text
    for p in hits.get("phone", []):
        highlighted = highlighted.replace(p, f"<mark class='phone' style='background:#E3F2FD; color:#1565C0; padding:0 2px; border-radius:2px;'>{p}</mark>")
    for e in hits.get("email", []):
        highlighted = highlighted.replace(e, f"<mark class='email' style='background:#E8F5E9; color:#2E7D32; padding:0 2px; border-radius:2px;'>{e}</mark>")
    for i in hits.get("id18", []):
        highlighted = highlighted.replace(i, f"<mark class='idcard' style='background:#FFF3E0; color:#EF6C00; padding:0 2px; border-radius:2px;'>{i}</mark>")
        
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    
    content = f"""
    <div class="container" style="max-width: 1000px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
            <h1>检测报告</h1>
            <a href="/demo" class="btn btn-secondary">返回重测</a>
        </div>

        <div class="grid-12" style="margin-bottom: 30px;">
            <div class="col-4 card" style="text-align: center;">
                <div style="font-size: 48px; font-weight: 700; color: var(--primary-red); margin-bottom: 4px;">{summary.get('phones_found', 0)}</div>
                <div style="font-size: 14px; color: var(--text-grey); text-transform: uppercase;">发现手机号</div>
            </div>
            <div class="col-4 card" style="text-align: center;">
                <div style="font-size: 48px; font-weight: 700; color: #2E7D32; margin-bottom: 4px;">{summary.get('emails_found', 0)}</div>
                <div style="font-size: 14px; color: var(--text-grey); text-transform: uppercase;">发现邮箱</div>
            </div>
            <div class="col-4 card" style="text-align: center;">
                <div style="font-size: 48px; font-weight: 700; color: #EF6C00; margin-bottom: 4px;">{summary.get('id18_found', 0)}</div>
                <div style="font-size: 14px; color: var(--text-grey); text-transform: uppercase;">发现身份证</div>
            </div>
        </div>

        <div class="grid-12">
            <div class="col-8 card">
                <h3>原文高亮</h3>
                <div style="font-family: monospace; white-space: pre-wrap; font-size: 14px; line-height: 1.8; color: #333;">{highlighted}</div>
            </div>
            <div class="col-4 card">
                <h3>结构化结果 (JSON)</h3>
                <pre style="max-height: 400px; overflow-y: auto;">{json_str}</pre>
            </div>
        </div>
    </div>
    """
    return _page_layout("检测结果", content, "/demo")

def render_docs_cn() -> str:
    content = """
    <div class="container" style="max-width: 900px;">
        <div style="text-align: center; margin-bottom: 60px;">
            <h1>API 接口文档</h1>
            <p>红岩数字合规平台标准 RESTful 接口规范说明。</p>
        </div>

        <div class="card" style="margin-bottom: 30px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0;">园区大屏数据</h3>
                <span class="tag tag-blue">GET</span>
            </div>
            <code style="background: #F5F5F7; padding: 4px 8px; border-radius: 4px; font-family: monospace;">/api/v1/overview</code>
            <p style="margin-top: 16px;">获取园区大屏的实时统计、告警、趋势等聚合数据。</p>
            <pre>{
  "park_name": "红岩 · 数字化示范园区",
  "risk_score": 92,
  "scans_today": 145,
  ...
}</pre>
        </div>
        
        <div class="card" style="margin-bottom: 30px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0;">天气数据</h3>
                <span class="tag tag-blue">GET</span>
            </div>
            <code style="background: #F5F5F7; padding: 4px 8px; border-radius: 4px; font-family: monospace;">/api/v1/weather</code>
            <p style="margin-top: 16px;">获取当前天气及未来预报。</p>
        </div>

        <div class="card" style="margin-bottom: 30px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0;">PII 敏感扫描</h3>
                <span class="tag tag-green">POST</span>
            </div>
            <code style="background: #F5F5F7; padding: 4px 8px; border-radius: 4px; font-family: monospace;">/scan/pii</code>
            <p style="margin-top: 16px;">核心扫描接口，支持批量检测手机号、邮箱与身份证。</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <p style="font-size: 13px; font-weight: 600;">请求示例：</p>
                    <pre>[
  {
    "source_type": "api",
    "record_id": "1001",
    "content": "用户 13800138000"
  }
]</pre>
                </div>
                <div>
                    <p style="font-size: 13px; font-weight: 600;">响应示例：</p>
                    <pre>{
  "summary": { "phones_found": 1, ... },
  "per_record": [
    { "hits": { "phone": ["13800138000"] } }
  ]
}</pre>
                </div>
            </div>
        </div>

        <div class="card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0;">健康检查</h3>
                <span class="tag tag-blue">GET</span>
            </div>
            <code style="background: #F5F5F7; padding: 4px 8px; border-radius: 4px; font-family: monospace;">/health</code>
            <p style="margin-top: 16px;">系统存活探测接口。</p>
            <pre>{ "status": "ok" }</pre>
        </div>
    </div>
    """
    return _page_layout("接口文档", content, "/docs-cn")

def render_park_dashboard() -> str:
    # 园区大屏 - 纯前端渲染模版，数据通过 API 拉取
    
    script = """
    <script>
        // Ticker Logic
        let tickerItems = [];
        
        async function initTicker() {
            try {
                const res = await fetch('/api/v1/ticker');
                const data = await res.json();
                tickerItems = data.items;
                if (!tickerItems || tickerItems.length === 0) return;

                const container = document.getElementById('top-ticker');
                container.style.display = 'flex';
                
                let html = '';
                tickerItems.forEach((item, index) => {
                    let badgeClass = 'tag-grey';
                    if (item.type === 'alert') badgeClass = 'tag-red';
                    if (item.type === 'weather') badgeClass = 'tag-blue';
                    if (item.type === 'briefing') badgeClass = 'tag-orange';
                    if (item.type === 'almanac') badgeClass = 'tag-green';
                    if (item.type === 'system') badgeClass = 'tag-purple';
                    
                    // On click: open modal
                    html += `
                        <div class="ticker-item ${index === 0 ? 'active' : ''}" onclick="openTickerModal(${index})">
                            <span class="ticker-badge ${badgeClass}">${item.title}</span>
                            <span class="ticker-text">${item.summary}</span>
                            <span class="ticker-arrow">查看详情 ›</span>
                        </div>
                    `;
                });
                container.innerHTML = html;

                // Auto rotate (8s)
                let currentIndex = 0;
                const els = container.querySelectorAll('.ticker-item');
                let interval = setInterval(() => {
                    els[currentIndex].classList.remove('active');
                    currentIndex = (currentIndex + 1) % els.length;
                    els[currentIndex].classList.add('active');
                }, 8000);

                // Pause on hover
                container.addEventListener('mouseenter', () => clearInterval(interval));
                container.addEventListener('mouseleave', () => {
                    interval = setInterval(() => {
                        els[currentIndex].classList.remove('active');
                        currentIndex = (currentIndex + 1) % els.length;
                        els[currentIndex].classList.add('active');
                    }, 8000);
                });

            } catch (e) {
                console.error("Ticker init failed", e);
            }
        }
        
        function openTickerModal(index) {
            const item = tickerItems[index];
            if(!item) return;
            
            document.getElementById('ticker-modal-title').innerText = item.title;
            document.getElementById('ticker-modal-body').innerText = item.summary; // Or item.content if available
            document.getElementById('ticker-modal-meta').innerText = `来源：${item.source || '系统'} · ID: ${item.id} · 优先级: ${item.priority}`;
            
            document.getElementById('ticker-overlay').style.display = 'block';
            document.getElementById('ticker-modal').style.display = 'block';
        }
        
        function closeTickerModal() {
            document.getElementById('ticker-overlay').style.display = 'none';
            document.getElementById('ticker-modal').style.display = 'none';
        }
        
        // Init both
        document.addEventListener('DOMContentLoaded', () => {
            initTicker();
        });

        // 简易 SVG 图表绘制函数
        function drawLineChart(id, data, color) {
            const svg = document.getElementById(id);
            if(!svg) return;
            const width = svg.clientWidth || 300;
            const height = svg.clientHeight || 100;
            const max = Math.max(...data) * 1.2;
            const stepX = width / (data.length - 1);
            
            let points = "";
            data.forEach((val, idx) => {
                const x = idx * stepX;
                const y = height - (val / max * height);
                points += `${x},${y} `;
            });
            
            const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
            polyline.setAttribute("points", points.trim());
            polyline.setAttribute("fill", "none");
            polyline.setAttribute("stroke", color);
            polyline.setAttribute("stroke-width", "3");
            polyline.setAttribute("stroke-linecap", "round");
            polyline.setAttribute("stroke-linejoin", "round");
            svg.innerHTML = ''; 
            svg.appendChild(polyline);
            
            // 绘制区域
            const areaPoints = points + `${width},${height} 0,${height}`;
            const polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            polygon.setAttribute("points", areaPoints);
            polygon.setAttribute("fill", color);
            polygon.setAttribute("opacity", "0.1");
            svg.appendChild(polygon);
        }
        
        function getWeatherIcon(code) {
             const map = {
                 'sun': '☀️', 'cloud': '☁️', 'rain': '🌧️', 'bolt': '⚡️', 'snow': '❄️'
             };
             return map[code] || '🌥️';
        }

        async function initDashboard() {
            try {
                // 1. 获取 Overview
                const overviewRes = await fetch('/api/v1/overview');
                const overview = await overviewRes.json();
                document.getElementById('risk-score').innerText = overview.risk_score;
                document.getElementById('scans-today').innerText = overview.scans_today;
                document.getElementById('hits-today').innerText = overview.hits_today;
                document.getElementById('alerts-active').innerText = overview.alerts_active;
                
                // 2. 获取 Calendar
                const calRes = await fetch('/api/v1/calendar');
                const calendar = await calRes.json();
                
                // 头部日期
                document.getElementById('cal-solar').innerText = calendar.solar_date + ' ' + calendar.weekday;
                document.getElementById('cal-lunar').innerText = calendar.lunar + ' · ' + calendar.term;
                
                // 自定义倒计时
                const custom = calendar.custom_countdown;
                document.getElementById('custom-countdown-name').innerText = custom.name;
                document.getElementById('custom-countdown-days').innerText = custom.days_left;
                
                // 下个节日
                const nextH = calendar.next_holiday;
                document.getElementById('next-holiday-name').innerText = nextH.name;
                document.getElementById('next-holiday-days').innerText = nextH.days_left;
                
                // Almanac Detail
                const alm = calendar.almanac;
                document.getElementById('alm-summary').innerText = calendar.display_line;
                
                // Fill details table
                const detailHTML = `
                    <div class="almanac-grid">
                        <div class="alm-cell"><span class="tag tag-red">宜</span> <div class="alm-text">${alm.yi.join(' ')}</div></div>
                        <div class="alm-cell"><span class="tag tag-grey">忌</span> <div class="alm-text">${alm.ji.join(' ')}</div></div>
                        <div class="alm-cell"><span class="tag tag-blue">吉神</span> <div class="alm-text">${alm.jishen.join(' ')}</div></div>
                        <div class="alm-cell"><span class="tag tag-orange">凶煞</span> <div class="alm-text">${alm.xiongsha.join(' ')}</div></div>
                        <div class="alm-cell"><span class="tag tag-purple">冲煞</span> <div class="alm-text">${alm.chong} ${alm.sha}</div></div>
                        <div class="alm-cell"><span class="tag tag-purple">值神</span> <div class="alm-text">${alm.zhishen}</div></div>
                        <div class="alm-cell col-span-2"><span class="tag tag-grey">胎神</span> <div class="alm-text">${alm.taishen}</div></div>
                    </div>
                `;
                document.getElementById('alm-detail-content').innerHTML = detailHTML;
                
                // 3. 获取 Weather (Apple Style)
                const weatherRes = await fetch('/api/v1/weather');
                const weather = await weatherRes.json();
                const cur = weather.current;
                
                // Current
                document.getElementById('w-temp').innerText = cur.temp;
                document.getElementById('w-cond').innerText = cur.condition;
                document.getElementById('w-hl').innerText = `H:${weather.daily[0].high}° L:${weather.daily[0].low}°`;
                document.getElementById('w-icon').innerText = getWeatherIcon(cur.icon || 'cloud');
                
                // Hourly
                const hourlyContainer = document.getElementById('w-hourly');
                hourlyContainer.innerHTML = '';
                weather.hourly.forEach(h => {
                    const div = document.createElement('div');
                    div.className = 'w-hourly-item';
                    div.innerHTML = `
                        <div class="time">${h.time}</div>
                        <div class="icon">${getWeatherIcon(h.icon)}</div>
                        <div class="temp">${h.temp}°</div>
                        ${parseInt(h.precip) > 0 ? `<div class="precip">${h.precip}</div>` : ''}
                    `;
                    hourlyContainer.appendChild(div);
                });
                
                // Daily
                const dailyContainer = document.getElementById('w-daily');
                dailyContainer.innerHTML = '';
                weather.daily.forEach(d => {
                    const div = document.createElement('div');
                    div.className = 'w-daily-item';
                    div.innerHTML = `
                        <div class="day">${d.day_name}</div>
                        <div class="icon">${getWeatherIcon(d.icon)}</div>
                        <div class="temp-bar">
                             <span class="low">${d.low}°</span>
                             <div class="bar-bg"><div class="bar-fill" style="left: 10%; width: 80%;"></div></div>
                             <span class="high">${d.high}°</span>
                        </div>
                    `;
                    dailyContainer.appendChild(div);
                });
                
                // Grid details
                document.getElementById('w-uv').innerText = cur.uv;
                document.getElementById('w-humidity').innerText = cur.humidity;
                document.getElementById('w-wind').innerText = cur.wind;
                document.getElementById('w-feel').innerText = cur.feels_like + '°';
                document.getElementById('w-precip').innerText = cur.precip_prob;
                document.getElementById('w-vis').innerText = cur.visibility;
                
                // 4. 获取 Air
                const airRes = await fetch('/api/v1/air');
                const air = await airRes.json();
                document.getElementById('air-aqi').innerText = air.aqi;
                document.getElementById('air-level').innerText = air.level;
                document.getElementById('air-trend').innerText = air.trend === 'rising' ? '↗' : (air.trend === 'falling' ? '↘' : '→');
                document.getElementById('air-tip').innerText = air.health_tip;
                
                // 5. 获取 Trends
                const trendRes = await fetch('/api/v1/trends');
                const trends = await trendRes.json();
                drawLineChart('chart-scan', trends.scan_volume, '#2196F3');
                drawLineChart('chart-hits', trends.pii_hits, '#EF6C00');
                drawLineChart('chart-risk', trends.risk_scores, '#C62828');
                
                // 6. 获取 Alerts
                const alertRes = await fetch('/api/v1/alerts');
                const alertsData = await alertRes.json();
                const alertList = document.getElementById('alert-list');
                alertList.innerHTML = '';
                alertsData.alerts.slice(0, 5).forEach(alert => {
                    const row = document.createElement('div');
                    row.className = 'list-item';
                    let tagClass = 'tag-blue';
                    if(alert.level === 'HIGH') tagClass = 'tag-red';
                    if(alert.level === 'MEDIUM') tagClass = 'tag-orange';
                    
                    row.innerHTML = `
                        <div style="flex:1;"><span class="tag ${tagClass}">${alert.level}</span></div>
                        <div style="flex:3; font-weight:500;">${alert.type}</div>
                        <div style="flex:2; text-align:right; font-size:12px; color:var(--text-grey);">${alert.time}</div>
                    `;
                    alertList.appendChild(row);
                });

                // 7. Integrations
                const intRes = await fetch('/api/v1/integrations');
                const intData = await intRes.json();
                const sysList = document.getElementById('sys-list');
                sysList.innerHTML = '';
                intData.systems.forEach(sys => {
                     const row = document.createElement('div');
                     row.style.marginBottom = '8px';
                     row.style.display = 'flex';
                     row.style.justifyContent = 'space-between';
                     row.style.fontSize = '13px';
                     row.innerHTML = `<span>${sys.name}</span><span style="color:#2E7D32;">● ${sys.status}</span>`;
                     sysList.appendChild(row);
                });
                 
                const pluginList = document.getElementById('plugin-list');
                pluginList.innerHTML = '';
                intData.available_plugins.forEach(p => {
                    const tag = document.createElement('span');
                    tag.className = 'tag tag-grey';
                    tag.style.marginRight = '6px';
                    tag.style.marginBottom = '6px';
                    tag.innerText = `+ ${p.name}`;
                    pluginList.appendChild(tag);
                });

            } catch(e) {
                console.error("Dashboard init error:", e);
            }
            
            // Clock
            setInterval(() => {
                const now = new Date();
                document.getElementById('clock-time').innerText = now.toLocaleTimeString('en-GB');
            }, 1000);
        }
        
        initDashboard();
    </script>
    """
    
    style = """
    <style>
        /* Weather Module Styles (Apple-like) */
        .weather-card {
            background: linear-gradient(135deg, #4A90E2, #002F6C);
            color: white;
            border: none;
        }
        .w-header { display: flex; justify-content: space-between; align-items: start; }
        .w-temp { font-size: 52px; font-weight: 200; line-height: 1; }
        .w-cond { font-size: 16px; font-weight: 500; margin-top: 4px; }
        .w-hl { font-size: 13px; opacity: 0.8; }
        
        .w-hourly { 
            display: flex; 
            overflow-x: auto; 
            gap: 20px; 
            padding: 16px 0; 
            border-top: 1px solid rgba(255,255,255,0.2); 
            border-bottom: 1px solid rgba(255,255,255,0.2);
            margin: 16px 0;
            scrollbar-width: none;
        }
        .w-hourly::-webkit-scrollbar { display: none; }
        .w-hourly-item { text-align: center; flex: 0 0 auto; }
        .w-hourly-item .time { font-size: 12px; opacity: 0.8; margin-bottom: 4px; }
        .w-hourly-item .icon { font-size: 20px; margin-bottom: 4px; }
        .w-hourly-item .temp { font-size: 14px; font-weight: 600; }
        .w-hourly-item .precip { font-size: 10px; color: #81D4FA; }
        
        .w-daily-item { display: flex; align-items: center; padding: 6px 0; font-size: 14px; }
        .w-daily-item .day { width: 40px; opacity: 0.9; }
        .w-daily-item .icon { width: 30px; text-align: center; }
        .w-daily-item .temp-bar { flex: 1; display: flex; align-items: center; gap: 8px; }
        .w-daily-item .bar-bg { flex: 1; height: 4px; background: rgba(0,0,0,0.2); border-radius: 2px; position: relative; }
        .w-daily-item .bar-fill { height: 4px; background: rgba(255,255,255,0.8); border-radius: 2px; position: absolute; }
        .w-daily-item .low { width: 24px; text-align: right; opacity: 0.7; }
        .w-daily-item .high { width: 24px; text-align: right; font-weight: 600; }
        
        .w-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
        .w-grid-item { background: rgba(0,0,0,0.1); border-radius: 8px; padding: 8px 12px; }
        .w-grid-label { font-size: 11px; opacity: 0.7; text-transform: uppercase; margin-bottom: 2px; }
        .w-grid-val { font-size: 18px; font-weight: 600; }

        /* Almanac Grid */
        .almanac-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
        .alm-cell { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: #555; }
        .alm-text { line-height: 1.4; flex: 1; }
        .col-span-2 { grid-column: span 2; }
        .tag-purple { background: #F3E5F5; color: #7B1FA2; }
    </style>
    """
    
    content = f"""
    {style}
    <div class="container" style="max-width: 1400px; padding-top: 20px;">
        <!-- Row 0: Header -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
            <div>
                <h2 style="margin:0;">园区智能运营中心</h2>
                <div id="cal-solar" style="color:var(--text-grey); font-size:16px; margin-top:4px;">正在加载日期...</div>
            </div>
            
            <div style="flex: 1; margin: 0 40px;">
                <!-- Almanac Bar -->
                <div class="card" style="padding: 12px 20px; min-height: 48px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;" onclick="document.getElementById('alm-detail').style.display = document.getElementById('alm-detail').style.display === 'none' ? 'block' : 'none'">
                        <div style="font-size: 14px; color: var(--text-dark);">
                            <span class="tag tag-red" style="margin-right: 8px;">今日黄历</span>
                            <span id="alm-summary">加载中...</span>
                        </div>
                        <div style="font-size: 12px; color: var(--text-grey);">▼ 展开详情</div>
                    </div>
                    <div id="alm-detail" style="display: none; padding-top: 12px; margin-top: 12px; border-top: 1px solid #eee;">
                        <div id="alm-detail-content"></div>
                    </div>
                </div>
            </div>

            <div style="text-align: right;">
                <div id="clock-time" style="font-size: 36px; font-weight: 700; font-family: monospace; line-height: 1;">--:--:--</div>
                <div id="cal-lunar" style="color:var(--text-grey); font-size:14px; margin-top:4px;">--</div>
            </div>
        </div>

        <!-- Row 1: Weather & Environment -->
        <div class="grid-12" style="margin-bottom: 20px;">
            <!-- Weather Card (Apple Style) -->
            <div class="col-5 card weather-card">
                <div class="w-header">
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">我的园区</div>
                        <div class="w-temp"><span id="w-temp">--</span>°</div>
                        <div class="w-cond" id="w-cond">--</div>
                        <div class="w-hl" id="w-hl">H:-- L:--</div>
                    </div>
                    <div style="font-size: 40px;" id="w-icon">⛅</div>
                </div>
                
                <div class="w-hourly" id="w-hourly">
                    <!-- Hourly items -->
                </div>
                
                <div class="grid-12">
                    <div class="col-6">
                        <div id="w-daily">
                            <!-- Daily items -->
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="w-grid">
                            <div class="w-grid-item">
                                <div class="w-grid-label">紫外线指数</div>
                                <div class="w-grid-val" id="w-uv">--</div>
                            </div>
                            <div class="w-grid-item">
                                <div class="w-grid-label">体感温度</div>
                                <div class="w-grid-val" id="w-feel">--</div>
                            </div>
                            <div class="w-grid-item">
                                <div class="w-grid-label">湿度</div>
                                <div class="w-grid-val" id="w-humidity">--</div>
                            </div>
                            <div class="w-grid-item">
                                <div class="w-grid-label">风向</div>
                                <div class="w-grid-val" id="w-wind" style="font-size: 14px;">--</div>
                            </div>
                             <div class="w-grid-item">
                                <div class="w-grid-label">降水概率</div>
                                <div class="w-grid-val" id="w-precip">--</div>
                            </div>
                            <div class="w-grid-item">
                                <div class="w-grid-label">能见度</div>
                                <div class="w-grid-val" id="w-vis">--</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Countdowns & Air Quality -->
            <div class="col-3" style="display:flex; flex-direction:column; gap:20px;">
                <!-- Air Quality Card -->
                <div class="card" style="flex: 1;">
                    <div style="font-size: 14px; color: var(--text-grey); margin-bottom: 8px;">空气质量</div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                        <div>
                            <span id="air-aqi" style="font-size: 36px; font-weight: 700;">--</span>
                            <span id="air-level" class="tag tag-green" style="vertical-align: top; margin-left: 4px;">--</span>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-size: 12px; color: var(--text-grey);">趋势</div>
                             <div style="font-size: 24px; font-weight: 600; color: var(--text-dark);" id="air-trend">→</div>
                        </div>
                    </div>
                    <div id="air-tip" style="font-size: 13px; color: var(--text-grey); background: #f9f9f9; padding: 8px; border-radius: 8px;">--</div>
                </div>
                
                <!-- Countdowns -->
                 <div class="card" style="flex: 1; display: flex; flex-direction: column; justify-content: space-around;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; margin-bottom: 10px;">
                        <div style="font-size: 13px; color: var(--text-grey);">下一个节日</div>
                        <div style="text-align: right;">
                            <div id="next-holiday-name" style="font-weight: 600; font-size: 14px;">--</div>
                            <div style="font-size: 12px; color: var(--primary-red);"><span id="next-holiday-days" style="font-weight: 700; font-size: 16px;">--</span> 天后</div>
                        </div>
                    </div>
                     <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 13px; color: var(--text-grey);">园区倒计时</div>
                         <div style="text-align: right;">
                            <div id="custom-countdown-name" style="font-weight: 600; font-size: 14px;">--</div>
                            <div style="font-size: 12px; color: var(--primary-red);"><span id="custom-countdown-days" style="font-weight: 700; font-size: 16px;">--</span> 天后</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Stats -->
            <div class="col-4 card" style="background: #333; color: white;">
                <div style="display: flex; justify-content: space-between; height: 100%;">
                    <div style="display: flex; flex-direction: column; justify-content: space-between;">
                         <div>
                            <div style="font-size: 13px; opacity: 0.7;">今日扫描</div>
                            <div id="scans-today" style="font-size: 28px; font-weight: 600;">--</div>
                         </div>
                         <div>
                            <div style="font-size: 13px; opacity: 0.7;">敏感命中</div>
                            <div id="hits-today" style="font-size: 28px; font-weight: 600; color: #FFB74D;">--</div>
                         </div>
                    </div>
                    <div style="display: flex; flex-direction: column; justify-content: space-between; text-align: right;">
                        <div>
                            <div style="font-size: 13px; opacity: 0.7;">实时告警</div>
                            <div id="alerts-active" style="font-size: 28px; font-weight: 600; color: #EF5350;">--</div>
                        </div>
                        <div style="opacity: 0.5; font-size: 12px;">实时监控中</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Row 2: Charts & Core Data -->
        <div class="grid-12" style="margin-bottom: 20px;">
            <div class="col-3 card">
                 <div style="text-align: center; padding: 20px 0;">
                    <div id="risk-score" style="font-size: 80px; font-weight: 800; color: #C62828; line-height: 1;">--</div>
                    <div style="font-size: 14px; color: var(--text-grey); margin-top: 10px; font-weight: 600;">园区合规指数</div>
                    <div style="font-size: 12px; color: var(--text-grey); margin-top: 4px;">击败了 85% 的同类园区</div>
                </div>
            </div>
            
            <div class="col-9 card">
                <div class="grid-12">
                    <div class="col-4">
                        <div style="font-size: 14px; color: var(--text-grey); margin-bottom: 10px;">扫描量趋势 (7日)</div>
                        <svg id="chart-scan" style="width: 100%; height: 120px;"></svg>
                    </div>
                    <div class="col-4">
                        <div style="font-size: 14px; color: var(--text-grey); margin-bottom: 10px;">敏感命中趋势 (7日)</div>
                        <svg id="chart-hits" style="width: 100%; height: 120px;"></svg>
                    </div>
                    <div class="col-4">
                        <div style="font-size: 14px; color: var(--text-grey); margin-bottom: 10px;">风险指数趋势 (7日)</div>
                        <svg id="chart-risk" style="width: 100%; height: 120px;"></svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- Row 3: Alerts & Integrations -->
        <div class="grid-12">
             <div class="col-6 card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>实时风险预警</h3>
                    <span class="tag tag-red">LIVE</span>
                </div>
                <div id="alert-list">
                    <!-- Alerts -->
                </div>
            </div>
            
            <div class="col-3 card">
                <h3 style="margin-bottom: 16px;">接入系统状态</h3>
                <div id="sys-list">
                    <!-- Systems -->
                </div>
            </div>
            
            <div class="col-3 card">
                <h3 style="margin-bottom: 16px;">可接入插件</h3>
                <div id="plugin-list">
                    <!-- Plugins -->
                </div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border-light); font-size: 12px; color: var(--text-grey);">
                    可无缝对接门禁、视频、财务等子系统，实现全域数据合规纳管。
                </div>
            </div>
        </div>
    </div>
    {script}
    """
    return _page_layout("园区大屏", content, "/park")
