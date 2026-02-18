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
            --grid-col-width: 1fr;
            --grid-row-height: 60px; /* Base unit for height */
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: var(--font-stack);
            background-color: var(--bg-body);
            color: var(--text-dark);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
            padding-bottom: 100px;
        }

        a { text-decoration: none; color: inherit; transition: opacity 0.2s; }
        a:hover { opacity: 0.7; }

        /* 布局容器 */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 20px;
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

        /* 卡片基础 */
        .card {
            background: var(--bg-card);
            border-radius: var(--radius-card);
            padding: 24px;
            box-shadow: var(--shadow-subtle);
            border: 1px solid rgba(0,0,0,0.02);
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        /* High Level Alert Border */
        .card.border-red {
            border: 2px solid var(--primary-red);
        }
        
        /* 布局编辑模式下的卡片样式 */
        body.edit-mode .card {
            border: 2px dashed var(--primary-red);
            cursor: move;
            user-select: none;
            z-index: 10;
        }
        body.edit-mode .card:hover {
            background: #FFFAFA;
        }

        /* 拖拽手柄 */
        .drag-handle {
            display: none;
            position: absolute;
            top: 0; left: 0; right: 0; height: 30px;
            background: rgba(198, 40, 40, 0.1);
            border-bottom: 1px solid rgba(198, 40, 40, 0.2);
            cursor: grab;
            justify-content: center;
            align-items: center;
            font-size: 12px;
            color: var(--primary-red);
            font-weight: 600;
        }
        body.edit-mode .drag-handle { display: flex; }
        
        /* 缩放手柄 */
        .resize-handle {
            display: none;
            position: absolute;
            bottom: 0; right: 0;
            width: 20px; height: 20px;
            cursor: nwse-resize;
            background: linear-gradient(135deg, transparent 50%, var(--primary-red) 50%);
            border-bottom-right-radius: var(--radius-card);
        }
        body.edit-mode .resize-handle { display: block; }

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
            text-align: center;
        }
        .btn-primary { background: var(--primary-red); color: white; }
        .btn-primary:hover { background: var(--primary-hover); transform: scale(1.02); opacity: 1; }
        .btn-secondary { background: #F5F5F7; color: var(--text-dark); }
        .btn-secondary:hover { background: #E5E5EA; opacity: 1; }
        .btn-outline { border: 1px solid var(--border-light); background: transparent; color: var(--text-grey); }
        .btn-outline:hover { border-color: var(--text-grey); color: var(--text-dark); opacity: 1; }
        
        /* Action Button (Microsoft/Apple minimal) */
        .btn-action {
            background: #fff;
            border: 1px solid #E5E5E5;
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .btn-action:hover {
            border-color: #CCC;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .btn-action:active { transform: scale(0.98); }
        .btn-action .act-name { font-weight: 600; font-size: 15px; color: #111; display: block; margin-bottom: 4px; }
        .btn-action .act-desc { font-size: 12px; color: #666; display: block; }
        .btn-action.processing { opacity: 0.7; pointer-events: none; background: #F9F9F9; }

        /* 12列网格布局容器 */
        .grid-layout-container {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            grid-auto-rows: var(--grid-row-height); 
            gap: 20px;
            position: relative;
        }

        /* 辅助类 */
        .grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px; } /* 内部使用 */
        .col-4 { grid-column: span 4; } /* 传统 fallback */
        
        /* 标签 */
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .tag-red { background: #FFEBEE; color: #C62828; }
        .tag-orange { background: #FFF3E0; color: #EF6C00; }
        .tag-green { background: #E8F5E9; color: #2E7D32; }
        .tag-blue { background: #E3F2FD; color: #1565C0; }
        .tag-grey { background: #EEEEEE; color: #616161; }
        .tag-purple { background: #F3E5F5; color: #7B1FA2; }

        /* Gradient Text */
        .text-gradient-green {
            background: linear-gradient(90deg, #2E7D32, #66BB6A);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

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

        /* Toast */
        .toast-container {
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            pointer-events: none;
        }
        .toast {
            background: rgba(0,0,0,0.85);
            color: white;
            padding: 10px 24px;
            border-radius: 99px;
            font-size: 14px;
            margin-bottom: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateY(-20px);
            animation: toastIn 0.3s forwards;
        }
        @keyframes toastIn {
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* 风险地图 */
        .risk-item {
            padding: 12px;
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.2s;
        }
        .risk-item:hover { background: #F9F9F9; }
        .risk-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        .risk-reason { 
            font-size: 13px; color: #666; margin-top: 8px; padding-top: 8px; border-top: 1px solid #f0f0f0; 
            display: none; 
        }
        .risk-item.expanded .risk-reason { display: block; }
        .badge-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }

        /* Ticker - Updated */
        .ticker-container {
            width: 100%; height: 48px; background: #fff; border-bottom: 1px solid rgba(0,0,0,0.05);
            display: flex; align-items: center; padding: 0 20px; font-size: 14px;
            overflow: hidden; position: relative; z-index: 2000;
        }
        .ticker-wrapper { flex: 1; height: 100%; position: relative; overflow: hidden; }
        .ticker-item {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; align-items: center;
            opacity: 0; transform: translateY(10px); transition: all 0.5s ease;
            pointer-events: none;
        }
        .ticker-item.active { opacity: 1; transform: translateY(0); pointer-events: auto; }
        
        .ticker-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 12px; }
        .dot-red { background: #D32F2F; box-shadow: 0 0 6px rgba(211, 47, 47, 0.4); }
        .dot-orange { background: #EF6C00; box-shadow: 0 0 6px rgba(239, 108, 0, 0.4); }
        .dot-blue { background: #2196F3; }
        .dot-green { background: #4CAF50; }
        .dot-grey { background: #9E9E9E; }
        
        .ticker-tag { font-weight: 600; margin-right: 12px; color: var(--text-dark); }
        .ticker-text { color: #555; margin-right: 12px; }
        .ticker-meta { font-size: 12px; color: #999; margin-left: auto; display: flex; align-items: center; gap: 12px; }
        
        .ticker-btn { 
            padding: 4px 12px; border-radius: 99px; font-size: 12px; 
            background: #f5f5f7; color: #333; cursor: pointer; border: 1px solid transparent; 
        }
        .ticker-btn:hover { background: #e5e5e5; }
        
        /* Ticker Modal */
        .ticker-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 600px; max-height: 80vh; background: #fff; z-index: 5002;
            border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); padding: 24px;
            overflow-y: auto;
        }
        .ticker-overlay {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); z-index: 5001;
        }
        
        .t-modal-item { display: flex; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
        .t-modal-item:last-child { border-bottom: none; }
        
        /* Leader Summary Panel (Top Right) */
        .leader-summary {
            position: absolute;
            right: 20px;
            top: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid rgba(0,0,0,0.05);
            width: 280px;
            z-index: 900;
        }
        .ls-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #333; display: flex; justify-content: space-between; }
        .ls-item { display: flex; justify-content: space-between; font-size: 13px; color: #666; margin-bottom: 6px; }
        .ls-item span:last-child { font-weight: 500; color: #333; }

        /* Narrative Control Card (Top Right - below leader) */
        .narrative-control {
            position: absolute;
            right: 310px; /* Left of leader summary */
            top: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid rgba(0,0,0,0.05);
            width: 280px;
            z-index: 900;
        }
        .nc-title { font-size: 12px; font-weight: 600; color: #666; margin-bottom: 4px; text-transform: uppercase; }
        .nc-val { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
        .sim-switch-row { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
        .sim-btn {
            border: 1px solid #e5e5e5;
            background: #fff;
            color: #333;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            cursor: pointer;
        }
        .sim-btn.active { border-color: #c62828; color: #c62828; background: #ffebee; }
        
        /* Risk Thermometer (Left Side) */
        .risk-thermometer-container {
            position: fixed;
            left: 20px;
            top: 200px;
            width: 60px;
            height: 300px;
            background: #fff;
            border-radius: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
            padding: 10px;
            z-index: 900;
            border: 1px solid rgba(0,0,0,0.05);
        }
        .rt-bar-bg { width: 12px; height: 240px; background: #eee; border-radius: 6px; position: relative; overflow: hidden; }
        .rt-bar-fill { 
            position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, #4CAF50, #FFC107, #F44336); 
            border-radius: 6px; transition: height 1s ease-in-out;
        }
        .rt-label { font-size: 12px; font-weight: 600; margin-top: 10px; color: #333; }
        
        /* Streak Stats (Bottom) */
        .streak-container {
            display: flex;
            align-items: center;
            gap: 12px;
            background: #fff;
            padding: 8px 16px;
            border-radius: 99px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
            margin-right: 20px;
        }
        .streak-num { font-size: 18px; font-weight: 700; color: #4CAF50; }
        .streak-text { font-size: 12px; color: #666; }

        /* Narrative Label */
        .narrative-label {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-left: 10px;
        }
        .nl-improving { background: #E8F5E9; color: #2E7D32; }
        .nl-stable { background: #E3F2FD; color: #1565C0; }
        .nl-crisis { background: #FFEBEE; color: #C62828; }

    </style>
    """

_JS_TICKER = """
        <script>
            let tickerItems = [];
            let tickerIdx = 0;
            let tickerTimer = null;
            let isPaused = false;
            
            async function initTicker() {
                try {
                    const res = await fetch('/api/v1/ticker');
                    const data = await res.json();
                    if(data.items && data.items.length > 0) {
                        tickerItems = data.items;
                        renderTicker();
                        startTicker();
                    }
                } catch(e) { console.error("Ticker load error", e); }
            }
            
            function renderTicker() {
                const container = document.getElementById('ticker-list');
                let html = '';
                tickerItems.forEach((item, idx) => {
                    let dotClass = 'dot-grey';
                    if(item.level === '红') dotClass = 'dot-red';
                    if(item.level === '橙') dotClass = 'dot-orange';
                    if(item.level === '蓝') dotClass = 'dot-blue';
                    if(item.level === '绿') dotClass = 'dot-green';
                    
                    html += `
                        <div class="ticker-item ${idx===0?'active':''}" onclick="handleTickerClick('${item.link}')">
                            <span class="ticker-dot ${dotClass}"></span>
                            <span class="ticker-tag">${item.tag}</span>
                            <span class="ticker-text" style="font-weight:500;">${item.title}</span>
                            <span class="ticker-text" style="color:#666; font-size:13px;">${item.summary || ''}</span>
                            <div class="ticker-meta">
                                <span>${item.source} ${item.time}</span>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                
                // Pause on hover
                container.addEventListener('mouseenter', () => { isPaused = true; });
                container.addEventListener('mouseleave', () => { isPaused = false; });
            }
            
            function startTicker() {
                if(tickerTimer) clearInterval(tickerTimer);
                tickerTimer = setInterval(() => {
                    if(isPaused) return;
                    
                    const els = document.querySelectorAll('.ticker-item');
                    if(els.length === 0) return;
                    
                    els[tickerIdx].classList.remove('active');
                    tickerIdx = (tickerIdx + 1) % els.length;
                    els[tickerIdx].classList.add('active');
                }, 5000); // 5s rotate
            }
            
            function handleTickerClick(link) {
                if(!link) return;
                // Scroll to anchor if on same page
                if(link.startsWith('/park#')) {
                    const id = link.split('#')[1];
                    const target = document.getElementById(id) || document.getElementById(`card-${id}`);
                    if(target) {
                        target.scrollIntoView({behavior: 'smooth', block: 'center'});
                        target.style.boxShadow = "0 0 0 2px var(--primary-red)";
                        setTimeout(() => target.style.boxShadow = "", 2000);
                    } else {
                        window.location.href = link;
                    }
                } else {
                    window.location.href = link;
                }
            }
            
            function openTickerModal() {
                const list = document.getElementById('ticker-modal-list');
                let html = '';
                tickerItems.forEach(item => {
                     let dotColor = '#999';
                     if(item.level === '红') dotColor = '#D32F2F';
                     if(item.level === '橙') dotColor = '#EF6C00';
                     if(item.level === '蓝') dotColor = '#2196F3';
                     if(item.level === '绿') dotColor = '#4CAF50';
                     
                     html += `
                        <div class="t-modal-item" onclick="handleTickerClick('${item.link}'); closeTickerModal();" style="cursor:pointer;">
                            <div style="margin-top:6px; width:8px; height:8px; border-radius:50%; background:${dotColor}; margin-right:12px; flex-shrink:0;"></div>
                            <div style="flex:1;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                    <span style="font-weight:600;">${item.tag} · ${item.title}</span>
                                    <span style="font-size:12px; color:#999;">${item.time}</span>
                                </div>
                                <div style="font-size:13px; color:#555;">${item.summary || '暂无详情'}</div>
                            </div>
                        </div>
                     `;
                });
                list.innerHTML = html;
                document.getElementById('ticker-overlay').style.display = 'block';
                document.getElementById('ticker-modal').style.display = 'block';
            }
            
            function closeTickerModal() {
                document.getElementById('ticker-overlay').style.display = 'none';
                document.getElementById('ticker-modal').style.display = 'none';
            }
            
            document.addEventListener('DOMContentLoaded', initTicker);
        </script>
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
        <div id="toast-container" class="toast-container"></div>
        
        <!-- Ticker -->
        <div id="top-ticker" class="ticker-container">
            <div class="ticker-wrapper" id="ticker-list">
                <!-- Items injected here -->
                <div style="display:flex; align-items:center; height:100%; color:#999; padding-left:20px;">
                    正在获取实时信息...
                </div>
            </div>
            <div style="border-left:1px solid #eee; padding-left:16px; margin-left:16px;">
                <button class="ticker-btn" onclick="openTickerModal()">更多</button>
            </div>
        </div>

        <!-- Ticker Modal -->
        <div id="ticker-overlay" class="ticker-overlay" onclick="closeTickerModal()"></div>
        <div id="ticker-modal" class="ticker-modal">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                <h3 style="margin:0;">实时信息总线</h3>
                <span style="cursor:pointer; font-size:20px;" onclick="closeTickerModal()">×</span>
            </div>
            <div id="ticker-modal-list"></div>
        </div>
        
        {_JS_TICKER}
        
        <header>
            <a href="/" class="logo">红岩 · 园区数字合规共建平台</a>
            <nav class="nav-links">
                {nav_html}
            </nav>
        </header>
        {content}
    </body>
    </html>
    """

def render_home() -> str:
    # 保持原样
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
    """
    return _page_layout("首页", content, "/")

def render_demo_page() -> str:
    # 保持原样
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
    <div class="container" style="max-width: 800px; padding-top: 40px;">
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>企业数据合规检测</h1>
            <p>粘贴文本内容，快速检测潜在的隐私泄露风险。</p>
        </div>
        
        <div class="card">
            <form action="/demo/scan" method="post">
                <textarea id="text-input" name="text" placeholder="在此粘贴包含敏感信息（手机号/邮箱/身份证）的文本内容..." style="min-height: 240px; width: 100%; border: 1px solid #ddd; padding: 10px; border-radius: 8px; font-family: inherit; resize: vertical;"></textarea>
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
    # 保持原样
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
    <div class="container" style="max-width: 1000px; padding-top: 40px;">
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
                <h3>结构化结果</h3>
                <pre style="max-height: 400px; overflow-y: auto;">{json_str}</pre>
            </div>
        </div>
    </div>
    """
    return _page_layout("检测结果", content, "/demo")

def render_docs_cn() -> str:
    # 保持原样
    content = """
    <div class="container" style="max-width: 900px; padding-top: 40px;">
        <h1>接口说明文档</h1>
        <p>（此处省略详情，与之前保持一致）</p>
    </div>
    """
    return _page_layout("接口文档", content, "/docs-cn")

def render_park_dashboard() -> str:
    # ---------------------------
    # 全新的可编辑大屏
    # ---------------------------
    
    css_extra = """
    <style>
        .edit-toolbar {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 5000;
            display: flex;
            gap: 12px;
            background: rgba(255,255,255,0.9);
            padding: 10px 16px;
            border-radius: 99px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0,0,0,0.1);
        }
        .weather-card {
            background: linear-gradient(135deg, #4A90E2, #002F6C);
            color: white;
            border: none;
        }
        .w-header { display: flex; justify-content: space-between; align-items: start; }
        .w-temp { font-size: 42px; font-weight: 200; line-height: 1; }
        .w-cond { font-size: 14px; font-weight: 500; margin-top: 4px; }
        .w-hl { font-size: 12px; opacity: 0.8; }
        
        .action-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }
        
        /* SVG Charts */
        .chart-container {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
    """
    
    js = """
    <script>
        const currentQuery = new URLSearchParams(window.location.search);
        const simQuery = currentQuery.get('sim');
        function apiPath(path) {
            if (simQuery && ['improving', 'stable', 'crisis'].includes(simQuery)) {
                const sep = path.includes('?') ? '&' : '?';
                return `${path}${sep}sim=${simQuery}`;
            }
            return path;
        }
        function switchSim(mode) {
            window.location.href = `/park?sim=${mode}`;
        }

        // --- Layout Config ---
        const DEFAULT_LAYOUT = [
            { id: 'card-briefing', x: 0, y: 0, w: 4, h: 4 },
            { id: 'card-narrative-summary', x: 4, y: 0, w: 4, h: 4 }, /* Narrative Summary */
            { id: 'card-stats', x: 8, y: 0, w: 4, h: 4 },
            
            { id: 'card-explain', x: 0, y: 4, w: 6, h: 6 },
            { id: 'card-actions', x: 6, y: 4, w: 6, h: 3 },
            { id: 'card-score', x: 6, y: 7, w: 6, h: 3 },
            
            { id: 'card-must-focus', x: 0, y: 10, w: 4, h: 5 },
            { id: 'card-behavior', x: 4, y: 10, w: 4, h: 5 },
            { id: 'card-time-pressure', x: 8, y: 10, w: 4, h: 5 },

            { id: 'card-risk-map', x: 0, y: 15, w: 6, h: 5 },
            { id: 'card-weather', x: 6, y: 15, w: 6, h: 5 },
            
            { id: 'card-charts', x: 0, y: 20, w: 8, h: 5 },
            { id: 'card-alerts', x: 8, y: 20, w: 4, h: 5 },

            { id: 'card-systems', x: 0, y: 25, w: 6, h: 4 },
            { id: 'card-plugins', x: 6, y: 25, w: 6, h: 4 }
        ];

        let currentLayout = [];
        let isEditMode = false;
        
        // --- Init ---
        document.addEventListener('DOMContentLoaded', () => {
            loadLayout();
            initDashboardData();
        });

        function loadLayout() {
            const saved = localStorage.getItem('redrock_park_layout_v1_beta');
            if (saved) {
                try {
                    currentLayout = JSON.parse(saved);
                } catch(e) {
                    currentLayout = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
                }
            } else {
                currentLayout = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
            }
            applyLayout();
        }

        function applyLayout() {
            currentLayout.forEach(item => {
                const el = document.getElementById(item.id);
                if (el) {
                    // grid-column: start / span w
                    el.style.gridColumn = `${item.x + 1} / span ${item.w}`;
                    el.style.gridRow = `${item.y + 1} / span ${item.h}`;
                }
            });
        }
        
        function saveLayout() {
            localStorage.setItem('redrock_park_layout_v1_beta', JSON.stringify(currentLayout));
            showToast('布局已保存');
        }
        
        function resetLayout() {
            if(confirm('确定恢复默认布局吗？')) {
                localStorage.removeItem('redrock_park_layout_v1_beta');
                currentLayout = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
                applyLayout();
                showToast('已恢复默认布局');
            }
        }
        
        function toggleEditMode() {
            isEditMode = !isEditMode;
            document.body.classList.toggle('edit-mode', isEditMode);
            const btn = document.getElementById('btn-edit-toggle');
            btn.innerText = isEditMode ? '完成编辑' : '编辑布局';
            btn.className = isEditMode ? 'btn btn-primary' : 'btn btn-secondary';
            
            if (isEditMode) {
                initDragAndResize();
            } else {
                saveLayout();
            }
        }

        // --- Interaction Logic (Drag & Resize) ---
        function initDragAndResize() {
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                const handle = card.querySelector('.drag-handle');
                const resize = card.querySelector('.resize-handle');
                
                if(handle) {
                    handle.onmousedown = (e) => startDrag(e, card);
                }
                if(resize) {
                    resize.onmousedown = (e) => startResize(e, card);
                }
            });
        }

        // Helpers for Grid Calculation
        const COL_COUNT = 12;
        const GRID_GAP = 20;
        
        function getGridMetrics() {
            const container = document.getElementById('park-layout');
            const rect = container.getBoundingClientRect();
            const colWidth = (rect.width - (GRID_GAP * (COL_COUNT - 1))) / COL_COUNT;
            const rowHeight = 60; // From CSS var
            return { colWidth, rowHeight, rect };
        }

        function startDrag(e, card) {
            e.preventDefault();
            const metrics = getGridMetrics();
            const id = card.id;
            const layoutItem = currentLayout.find(i => i.id === id);
            
            const startX = e.clientX;
            const startY = e.clientY;
            const startGridX = layoutItem.x;
            const startGridY = layoutItem.y;
            
            function onMove(ev) {
                const dx = ev.clientX - startX;
                const dy = ev.clientY - startY;
                
                const dCol = Math.round(dx / (metrics.colWidth + GRID_GAP));
                const dRow = Math.round(dy / (metrics.rowHeight + GRID_GAP));
                
                let newX = startGridX + dCol;
                let newY = startGridY + dRow;
                
                // Bounds
                newX = Math.max(0, Math.min(COL_COUNT - layoutItem.w, newX));
                newY = Math.max(0, newY); // No bottom limit
                
                layoutItem.x = newX;
                layoutItem.y = newY;
                applyLayout();
            }
            
            function onUp() {
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
            }
            
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        }

        function startResize(e, card) {
            e.preventDefault();
            e.stopPropagation();
            const metrics = getGridMetrics();
            const id = card.id;
            const layoutItem = currentLayout.find(i => i.id === id);
            
            const startX = e.clientX;
            const startY = e.clientY;
            const startW = layoutItem.w;
            const startH = layoutItem.h;
            
            function onMove(ev) {
                const dx = ev.clientX - startX;
                const dy = ev.clientY - startY;
                
                const dCol = Math.round(dx / (metrics.colWidth + GRID_GAP));
                const dRow = Math.round(dy / (metrics.rowHeight + GRID_GAP));
                
                let newW = Math.max(2, Math.min(COL_COUNT - layoutItem.x, startW + dCol));
                let newH = Math.max(2, startH + dRow);
                
                layoutItem.w = newW;
                layoutItem.h = newH;
                applyLayout();
            }
            
            function onUp() {
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
            }
            
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        }


        // --- Data Fetching & Rendering ---
        
        async function initDashboardData() {
             loadNarrativeStatus(); // Load narrative status first
             loadActions();
             loadRiskMap();
             loadBriefing();
             loadStats();
             loadWeather();
             loadMustFocus();
             loadBehavior();
             loadTimePressure();
             loadRiskExplain(); 
             loadLeaderSummary();
             loadRiskThermometer();
             loadStreakStats();
             loadNarrativeSummary(); // New
             loadTrends(); // Updated for charts
        }
        
        async function loadNarrativeStatus() {
            try {
                const res = await fetch(apiPath('/api/v1/narrative/status'));
                const data = await res.json();
                if(data.error) return;
                
                document.getElementById('nc-mode').innerText = data.effective_mode_label || '--';
                document.getElementById('nc-sim').innerText = data.effective_mode || '--';
                document.getElementById('nc-ver').innerText = data.engine_version;
                document.getElementById('nc-source').innerText = data.source === 'query_param' ? '请求参数' : '环境变量';

                const mode = data.effective_mode || '';
                ['improving', 'stable', 'crisis'].forEach(m => {
                    const el = document.getElementById(`sim-btn-${m}`);
                    if (!el) return;
                    if (m === mode) el.classList.add('active');
                    else el.classList.remove('active');
                });
            } catch(e) { console.error(e); }
        }

        async function loadNarrativeSummary() {
            try {
                const res = await fetch(apiPath('/api/v1/narrative/summary'));
                const data = await res.json();
                
                document.getElementById('ns-title').innerText = data.title || "暂无结论";
                document.getElementById('ns-text').innerText = data.summary || "暂无叙事摘要";
                document.getElementById('nc-oneline').innerText = data.title || "暂无";

                const evidenceDiv = document.getElementById('ns-evidence');
                evidenceDiv.innerHTML = '';
                (data.evidence || []).forEach((item) => {
                    const li = document.createElement('li');
                    li.style.marginBottom = '4px';
                    li.textContent = item;
                    evidenceDiv.appendChild(li);
                });
                
                const actDiv = document.getElementById('ns-actions');
                actDiv.innerHTML = '';
                if(data.actions && data.actions.length > 0) {
                    data.actions.slice(0, 2).forEach(act => {
                        const btn = document.createElement('button');
                        btn.className = 'btn btn-secondary';
                        btn.style.marginRight = '8px';
                        btn.style.marginTop = '8px';
                        btn.innerText = act.label || '执行动作';
                        btn.onclick = () => runAction(act.id);
                        actDiv.appendChild(btn);
                    });
                }
            } catch(e) { console.error(e); }
        }

        async function loadTrends() {
             try {
                 const res = await fetch(apiPath('/api/v1/trends'));
                 const data = await res.json();
                 
                 // Update narrative label
                 const container = document.getElementById('chart-narrative-label');
                 if(data.risk_scores) {
                      // Determine trend roughly
                      const scores = data.risk_scores;
                      const first = scores[0];
                      const last = scores[scores.length-1];
                      let mode = 'stable';
                      if (last > first + 10) mode = 'improving';
                      if (last < first - 10) mode = 'crisis';
                      
                      let cls = 'nl-stable';
                      let text = '平稳运行';
                      if(mode === 'improving') { cls = 'nl-improving'; text = '持续改善'; }
                      if(mode === 'crisis') { cls = 'nl-crisis'; text = '风险上升'; }
                      
                      container.innerHTML = `<span class="narrative-label ${cls}">${text}</span>`;
                 }
                 
                 // Render simple SVG Chart
                 renderChart(data.risk_scores);
                 
             } catch(e) { console.error(e); }
        }
        
        function renderChart(data) {
             const svgEl = document.getElementById('chart-svg');
             if(!svgEl || !data || data.length === 0) return;
             
             // Normalize data to 0-100 range for Y (Chart height)
             const width = 500;
             const height = 150;
             const padding = 10;
             
             const maxVal = 100;
             const minVal = 0;
             const xStep = (width - padding*2) / (data.length - 1);
             
             // Points
             let points = "";
             data.forEach((val, idx) => {
                 const x = padding + idx * xStep;
                 const y = height - padding - ((val - minVal) / (maxVal - minVal)) * (height - padding*2);
                 points += `${x},${y} `;
             });
             
             const polyline = `<polyline points="${points}" fill="none" stroke="#C62828" stroke-width="2" vector-effect="non-scaling-stroke" />`;
             
             // Area
             const areaPoints = `${padding},${height - padding} ` + points + `${width - padding},${height - padding}`;
             const polygon = `<polygon points="${areaPoints}" fill="rgba(198, 40, 40, 0.1)" stroke="none" />`;
             
             svgEl.innerHTML = polygon + polyline;
             // Update ViewBox
             svgEl.setAttribute('viewBox', `0 0 ${width} ${height}`);
        }

        async function loadActions() {
            try {
                const res = await fetch(apiPath('/api/v1/actions'));
                const data = await res.json();
                const container = document.getElementById('action-container');
                container.innerHTML = '';
                
                data.actions.forEach(act => {
                    const btn = document.createElement('div');
                    btn.className = 'btn-action';
                    btn.innerHTML = `
                        <span class="act-name">${act.name}</span>
                        <span class="act-desc">${act.description}</span>
                    `;
                    btn.onclick = () => runAction(act.id, btn);
                    container.appendChild(btn);
                });
            } catch(e) { console.error(e); }
        }
        
        async function runAction(id, btnEl) {
            if(btnEl) btnEl.classList.add('processing');
            try {
                const res = await fetch(apiPath(`/api/v1/actions/${id}/run`), { method: 'POST' });
                const data = await res.json();
                if(data.success) {
                    showToast(`执行成功：${data.message}`);
                } else {
                    showToast(`执行失败：${data.message}`);
                }
            } catch(e) {
                showToast('网络请求失败');
            } finally {
                if(btnEl) btnEl.classList.remove('processing');
            }
        }
        
        async function loadRiskMap() {
            try {
                const res = await fetch('/api/v1/risk-map');
                const data = await res.json();
                const container = document.getElementById('risk-list');
                container.innerHTML = '';
                
                data.risks.forEach(r => {
                    const div = document.createElement('div');
                    div.className = 'risk-item';
                    
                    let color = '#ccc';
                    if(r.level === 'high') color = '#D32F2F';
                    if(r.level === 'mid') color = '#EF6C00';
                    if(r.level === 'low') color = '#2E7D32';
                    
                    div.innerHTML = `
                        <div class="risk-header" onclick="this.parentElement.classList.toggle('expanded')">
                            <div style="display:flex; align-items:center;">
                                <span class="badge-dot" style="background:${color}"></span>
                                <span style="font-weight:500;">${r.name}</span>
                            </div>
                            <span style="font-size:12px; color:#888;">展开</span>
                        </div>
                        <div class="risk-reason">${r.reason}</div>
                    `;
                    container.appendChild(div);
                });
            } catch(e) { console.error(e); }
        }

        async function loadBriefing() {
            try {
                const res = await fetch(apiPath('/api/v1/briefing'));
                const data = await res.json();
                
                document.getElementById('br-title').innerText = data.title;
                document.getElementById('br-date').innerText = data.date;
                document.getElementById('br-summary').innerText = data.summary;
                
                // Must Focus Today
                const focusCount = data.must_focus_count || 0;
                const focusEl = document.getElementById('must-focus-area');
                if (focusCount > 0) {
                    focusEl.style.display = 'block';
                    focusEl.innerHTML = `
                        <div style="background:#FFEBEE; color:#C62828; padding:8px 12px; border-radius:8px; margin-top:12px; cursor:pointer; display:flex; justify-content:space-between; align-items:center;"
                             onclick="document.getElementById('card-risk-map').scrollIntoView({behavior:'smooth'})">
                            <span style="font-weight:600;">🚨 今日必须关注：${focusCount} 个高风险项</span>
                            <span>前往处理 &rarr;</span>
                        </div>
                    `;
                } else {
                    focusEl.style.display = 'none';
                }

            } catch(e) { console.error(e); }
        }

        async function loadStats() {
            fetch(apiPath('/api/v1/overview')).then(r=>r.json()).then(d => {
                document.getElementById('risk-score').innerText = d.compliance_score;
                document.getElementById('scan-count').innerText = d.scans_today;
            });
        }
        
        async function loadWeather() {
             fetch('/api/v1/weather').then(r=>r.json()).then(w => {
                 document.getElementById('w-temp').innerText = w.current.temp;
                 document.getElementById('w-cond').innerText = w.current.condition;
             });
        }

        async function loadMustFocus() {
            try {
                const res = await fetch(apiPath('/api/v1/must-focus'));
                const data = await res.json();
                
                // Border Red logic
                const card = document.getElementById('card-must-focus');
                if (data.level === 'high') {
                    card.classList.add('border-red');
                } else {
                    card.classList.remove('border-red');
                }
                
                const list = document.getElementById('mf-list');
                list.innerHTML = '';
                
                if (data.items.length === 0) {
                    list.innerHTML = `<div style="color:#999; text-align:center; padding:20px;">暂无必须关注事项</div>`;
                } else {
                    data.items.forEach(item => {
                       const div = document.createElement('div');
                       div.style.marginBottom = '8px';
                       div.style.paddingBottom = '8px';
                       div.style.borderBottom = '1px solid #f0f0f0';
                       
                       let icon = item.type === 'risk' ? '⚠️' : '🔔';
                       
                       div.innerHTML = `
                           <div style="font-weight:500; font-size:14px; margin-bottom:2px;">${icon} ${item.desc}</div>
                           <div style="font-size:12px; color:#666;">${item.reason}</div>
                       `;
                       list.appendChild(div);
                    });
                }
                document.getElementById('mf-suggestion').innerText = data.suggestion;
                
            } catch(e) { console.error(e); }
        }

        async function loadBehavior() {
            try {
                const res = await fetch('/api/v1/behavior-stats');
                const data = await res.json();
                
                document.getElementById('bh-users').innerText = data.active_users;
                document.getElementById('bh-actions').innerText = data.actions_today;
                document.getElementById('bh-resp').innerText = data.avg_response_time;
                document.getElementById('bh-module').innerText = data.most_active_module;
            } catch(e) { console.error(e); }
        }

        async function loadTimePressure() {
            try {
                const res = await fetch('/api/v1/time-pressure');
                const data = await res.json();
                
                const card = document.getElementById('card-time-pressure');
                if (data.level === 'high') {
                    card.classList.add('border-red');
                } else {
                    card.classList.remove('border-red');
                }
                
                document.getElementById('tp-pending').innerText = data.pending_tasks;
                document.getElementById('tp-urgent').innerText = data.urgent_tasks;
                document.getElementById('tp-deadline').innerText = data.next_deadline;
                
                const badge = document.getElementById('tp-badge');
                if (data.level === 'high' || data.level === 'medium') {
                    badge.style.display = 'inline-block';
                    badge.innerText = data.level === 'high' ? '高压' : '中压';
                } else {
                    badge.style.display = 'none';
                }
                
            } catch(e) { console.error(e); }
        }

        async function loadLeaderSummary() {
            try {
                const res = await fetch('/api/v1/leader-summary');
                const data = await res.json();
                
                document.getElementById('ls-efficiency').innerText = data.efficiency;
                document.getElementById('ls-team').innerText = data.team_status;
                document.getElementById('ls-budget').innerText = data.budget_usage;
            } catch(e) { console.error(e); }
        }

        async function loadRiskThermometer() {
            try {
                const res = await fetch(apiPath('/api/v1/risk-thermometer'));
                const data = await res.json();
                
                const fill = document.getElementById('rt-fill');
                const heightPercent = (data.temperature / data.max) * 100;
                fill.style.height = `${heightPercent}%`;
                
                document.getElementById('rt-val').innerText = `${data.temperature}°`;
            } catch(e) { console.error(e); }
        }

        async function loadStreakStats() {
            try {
                const res = await fetch('/api/v1/streak');
                const data = await res.json();
                
                document.getElementById('streak-num').innerText = data.safe_days;
            } catch(e) { console.error(e); }
        }

        async function loadRiskExplain() {
            try {
                const res = await fetch('/api/v1/risk/explain');
                const data = await res.json();
                
                document.getElementById('re-score').innerText = data.total_score;
                document.getElementById('re-level').innerText = data.level;
                
                // Color level
                const badge = document.getElementById('re-level-badge');
                if(data.level === '严重' || data.level === '高') badge.style.backgroundColor = 'var(--primary-red)';
                else if(data.level === '中') badge.style.backgroundColor = '#EF6C00';
                else badge.style.backgroundColor = '#2E7D32';
                
                document.getElementById('re-driver').innerText = data.primary_driver ? data.primary_driver.name : '--';
                
                // Factors
                const fContainer = document.getElementById('re-factors');
                fContainer.innerHTML = '';
                // Sort by contribution desc
                const factors = data.factors || [];
                factors.sort((a,b) => b.contribution - a.contribution);
                
                factors.slice(0, 4).forEach(f => {
                    const row = document.createElement('div');
                    row.style.marginBottom = '8px';
                    
                    const maxC = factors[0].contribution || 1;
                    const w = Math.min(100, (f.contribution / maxC) * 100);
                    
                    row.innerHTML = `
                        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                            <span>${f.name}</span>
                            <span style="color:#666;">-${f.contribution}</span>
                        </div>
                        <div style="width:100%; height:4px; background:#eee; border-radius:2px;">
                            <div style="width:${w}%; height:100%; background:var(--primary-red); border-radius:2px; opacity:0.7;"></div>
                        </div>
                    `;
                    fContainer.appendChild(row);
                });
                
                // Suggestions
                const sContainer = document.getElementById('re-suggestions');
                sContainer.innerHTML = '';
                (data.suggestions || []).slice(0,2).forEach(s => {
                    const div = document.createElement('div');
                    div.style.background = '#F9F9F9';
                    div.style.padding = '8px';
                    div.style.borderRadius = '8px';
                    div.style.marginTop = '8px';
                    div.style.fontSize = '12px';
                    div.innerHTML = `<span style="font-weight:600; color:#333;">${s.title}</span><br><span style="color:#666;">${s.detail}</span>`;
                    sContainer.appendChild(div);
                });
                
            } catch(e) { console.error(e); }
        }

        function showToast(msg) {
            const div = document.createElement('div');
            div.className = 'toast';
            div.innerText = msg;
            document.getElementById('toast-container').appendChild(div);
            setTimeout(() => div.remove(), 3000);
        }
    </script>
    """

    content = f"""
    {css_extra}
    
    <!-- Leader Summary Panel -->
    <div class="leader-summary">
        <div class="ls-title">
            <span>领导摘要</span>
            <span style="font-weight:normal; color:#999; font-size:12px;">实时</span>
        </div>
        <div class="ls-item"><span>效率</span><span id="ls-efficiency">--</span></div>
        <div class="ls-item"><span>团队状态</span><span id="ls-team">--</span></div>
        <div class="ls-item"><span>预算使用</span><span id="ls-budget">--</span></div>
    </div>
    
    <!-- Narrative Mode Control Card -->
    <div class="narrative-control">
        <div class="nc-title">叙事引擎</div>
        <div class="nc-val"><span id="nc-mode">--</span> / <span id="nc-sim">--</span></div>
        <div style="font-size:12px; color:#666;">来源：<span id="nc-source">--</span></div>
        <div class="nc-title">版本</div>
        <div class="nc-val" id="nc-ver">--</div>
        <div class="nc-title">今日结论</div>
        <div style="font-size:12px; color:#333;" id="nc-oneline">--</div>
        <div class="sim-switch-row">
            <button id="sim-btn-improving" class="sim-btn" onclick="switchSim('improving')">持续改善</button>
            <button id="sim-btn-stable" class="sim-btn" onclick="switchSim('stable')">平稳运行</button>
            <button id="sim-btn-crisis" class="sim-btn" onclick="switchSim('crisis')">风险上升</button>
        </div>
    </div>
    
    <!-- Risk Thermometer -->
    <div class="risk-thermometer-container">
        <div class="rt-bar-bg">
            <div id="rt-fill" class="rt-bar-fill" style="height:0%;"></div>
        </div>
        <div class="rt-label" id="rt-val">--</div>
        <div style="font-size:10px; color:#999;">风险温度</div>
    </div>

    <!-- Static Header Row -->
    <div class="container" style="padding-bottom: 0;">
         <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <h2 style="margin:0;">园区智能运营中心</h2>
                <div style="font-size:14px; color:var(--text-grey);">{json.loads(json.dumps("2026年2月18日"))}</div> 
            </div>
            <div style="display:flex; align-items:center;">
                 <!-- Streak Stats -->
                 <div class="streak-container">
                    <span class="streak-num" id="streak-num">--</span>
                    <span class="streak-text">连续安全天数</span>
                 </div>
                 
                 <div style="text-align: right;">
                     <div style="font-size: 32px; font-weight: 700; font-family: monospace;">14:30:00</div>
                     <div style="font-size:12px; color:var(--text-grey);">系统运行正常</div>
                 </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Layout Grid -->
        <div id="park-layout" class="grid-layout-container">
            
            <!-- Briefing -->
            <div id="card-briefing" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <!-- Anchor -->
                <div id="briefing" style="position:absolute; top:-100px;"></div> 
                <h3><span id="br-title">每日简报</span> <span class="tag tag-grey" id="br-date">--</span></h3>
                <p id="br-summary" style="margin-bottom: 12px;">正在加载...</p>
                <div id="must-focus-area" style="display:none;"></div>
            </div>
            
            <!-- Narrative Summary (New) -->
            <div id="card-narrative-summary" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <h3>叙事摘要</h3>
                <div id="ns-title" style="font-size:16px; font-weight:600; margin-bottom:8px;">...</div>
                <p id="ns-text" style="font-size:14px; margin-bottom:8px; color:#555;">...</p>
                <ul id="ns-evidence" style="font-size:12px; color:#666; padding-left:16px; margin-bottom:8px;"></ul>
                <div id="ns-actions" style="flex:1; overflow-y:auto; margin-top:8px;">
                    <!-- Actions -->
                </div>
            </div>

            <!-- Stats -->
            <div id="card-stats" class="card" style="background:#333; color:white;">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <h3 style="color:white;">今日概览</h3>
                <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="margin-bottom:20px;">
                        <div style="font-size:12px; opacity:0.7;">今日扫描</div>
                        <div id="scan-count" style="font-size:36px; font-weight:600;">--</div>
                    </div>
                </div>
            </div>

            <!-- Risk Explain (New) -->
            <div id="card-explain" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0;">风险归因</h3>
                    <span id="re-level-badge" class="tag" style="background:#2E7D32; color:white;">
                        <span id="re-level">--</span>风险
                    </span>
                </div>
                
                <div style="display:flex; gap:16px; margin-bottom:16px;">
                    <div style="text-align:center;">
                        <div id="re-score" style="font-size:36px; font-weight:700; line-height:1;">--</div>
                        <div style="font-size:12px; color:#999;">当前总分</div>
                    </div>
                    <div style="flex:1; border-left:1px solid #eee; padding-left:16px; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:12px; color:#999;">核心主因</div>
                        <div id="re-driver" style="font-weight:600; font-size:15px; color:var(--text-dark);">--</div>
                    </div>
                </div>
                
                <div style="font-size:12px; color:#999; margin-bottom:8px;">扣分因子前四位</div>
                <div id="re-factors" style="margin-bottom:16px;">
                    <!-- Factors injected -->
                </div>
                
                <div style="font-size:12px; color:#999; margin-bottom:4px;">建议行动</div>
                <div id="re-suggestions" style="flex:1; overflow-y:auto;">
                    <!-- Suggestions injected -->
                </div>
            </div>

            <!-- Actions (Quick Decision) -->
            <div id="card-actions" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <h3>快速决策区</h3>
                    <span class="tag tag-blue">行动</span>
                </div>
                <div id="action-container" class="action-grid">
                    <!-- Buttons injected here -->
                </div>
            </div>

            <!-- Score -->
            <div id="card-score" class="card" style="text-align:center; justify-content:center;">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <div id="risk-score" style="font-size:72px; font-weight:800; color:var(--primary-red);">--</div>
                <div style="font-size:14px; color:var(--text-grey);">合规指数</div>
            </div>

            <!-- New: Must Focus -->
            <div id="card-must-focus" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <h3 style="color:var(--primary-red);">必须关注</h3>
                <div id="mf-list" style="flex:1; overflow-y:auto; margin-bottom:12px;">
                    <!-- Items -->
                </div>
                <div id="mf-suggestion" style="font-size:12px; color:#666; background:#f9f9f9; padding:8px; border-radius:8px;"></div>
            </div>

            <!-- New: Behavior Stats -->
            <div id="card-behavior" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <h3><span class="text-gradient-green">行为反馈</span></h3>
                <div style="flex:1; display:flex; flex-direction:column; justify-content:space-around;">
                    <div class="list-item"><span>活跃用户</span><span id="bh-users" style="font-weight:600;">--</span></div>
                    <div class="list-item"><span>今日操作</span><span id="bh-actions" style="font-weight:600;">--</span></div>
                    <div class="list-item"><span>平均响应</span><span id="bh-resp" style="font-weight:600;">--</span></div>
                    <div class="list-item"><span>热点模块</span><span id="bh-module" style="font-weight:600;">--</span></div>
                </div>
            </div>

            <!-- New: Time Pressure -->
            <div id="card-time-pressure" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <h3>时间压力</h3>
                    <span id="tp-badge" class="tag tag-orange" style="display:none;">高压</span>
                </div>
                <div style="text-align:center; margin-bottom:16px;">
                    <div style="font-size:12px; color:#999;">待处理任务</div>
                    <div id="tp-pending" style="font-size:36px; font-weight:700;">--</div>
                </div>
                <div class="list-item"><span>紧急任务</span><span id="tp-urgent" style="color:var(--primary-red); font-weight:600;">--</span></div>
                <div class="list-item"><span>下个截止</span><span id="tp-deadline" style="font-size:13px;">--</span></div>
            </div>

            <!-- Risk Map -->
            <div id="card-risk-map" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <h3>企业风险地图</h3>
                <div id="risk-list" style="overflow-y:auto; flex:1;">
                    <!-- Risks injected here -->
                </div>
            </div>

            <!-- Weather (With ID for anchor) -->
            <div id="card-weather" class="card weather-card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <!-- Anchor -->
                <div id="weather" style="position:absolute; top:-100px;"></div>
                <div id="air" style="position:absolute; top:-100px;"></div>
                <div class="w-header">
                     <div>
                        <div style="font-size: 14px; opacity: 0.9;">园区气象</div>
                        <div class="w-temp"><span id="w-temp">--</span>°</div>
                        <div class="w-cond" id="w-cond">--</div>
                    </div>
                    <div style="font-size: 40px;">⛅</div>
                </div>
            </div>

            <!-- Charts -->
            <div id="card-charts" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <div style="display:flex; align-items:center;">
                    <h3>趋势分析</h3>
                    <div id="chart-narrative-label"></div>
                </div>
                <div class="chart-container">
                    <svg id="chart-svg" width="100%" height="100%" preserveAspectRatio="none"></svg>
                </div>
            </div>

            <!-- Alerts -->
            <div id="card-alerts" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <!-- Anchor -->
                <div id="alerts" style="position:absolute; top:-100px;"></div>
                <h3>实时告警</h3>
                <div style="font-size:13px; color:#888;">暂无严重告警</div>
            </div>

            <!-- Systems -->
            <div id="card-systems" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <!-- Anchor -->
                <div id="integrations" style="position:absolute; top:-100px;"></div>
                <h3>系统接入</h3>
                <div class="list-item"><span>OA系统</span><span style="color:green;">●</span></div>
                <div class="list-item"><span>安防监控</span><span style="color:green;">●</span></div>
            </div>
            
            <!-- Plugins / Calendar -->
            <div id="card-plugins" class="card">
                <div class="drag-handle">拖拽移动</div>
                <div class="resize-handle"></div>
                <!-- Anchor -->
                <div id="calendar" style="position:absolute; top:-100px;"></div>
                <h3>扩展插件</h3>
                <div>
                    <span class="tag tag-grey">+ 门禁</span>
                    <span class="tag tag-grey">+ 财务</span>
                </div>
            </div>

        </div>
    </div>
    
    <div class="edit-toolbar">
        <button id="btn-reset" class="btn btn-outline" onclick="resetLayout()">恢复默认</button>
        <button id="btn-edit-toggle" class="btn btn-secondary" onclick="toggleEditMode()">编辑布局</button>
    </div>

    {js}
    """
    return _page_layout("园区大屏", content, "/park")
