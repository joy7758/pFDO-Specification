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
        .col-6 { grid-column: span 6; }
        .col-8 { grid-column: span 8; }
        .col-9 { grid-column: span 9; }
        .col-12 { grid-column: span 12; }

        @media (max-width: 1024px) {
            .col-3, .col-4, .col-6, .col-8, .col-9 { grid-column: span 12; }
        }

        /* 标签 */
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .tag-red { background: #FFEBEE; color: #C62828; }
        .tag-orange { background: #FFF3E0; color: #EF6C00; }
        .tag-green { background: #E8F5E9; color: #2E7D32; }
        .tag-blue { background: #E3F2FD; color: #1565C0; }

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
                <textarea id="text-input" name="text" placeholder="在此粘贴包含敏感信息（手机号/邮箱/身份证）的文本内容..." style="min-height: 240px;"></textarea>
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
        highlighted = highlighted.replace(p, f"<mark class='phone'>{p}</mark>")
    for e in hits.get("email", []):
        highlighted = highlighted.replace(e, f"<mark class='email'>{e}</mark>")
    for i in hits.get("id18", []):
        highlighted = highlighted.replace(i, f"<mark class='idcard'>{i}</mark>")
        
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
            <code style="background: #F5F5F7; padding: 4px 8px; border-radius: 4px; font-family: monospace;">/api/park/dashboard</code>
            <p style="margin-top: 16px;">获取园区大屏的实时统计、告警、趋势等聚合数据。</p>
            <pre>{
  "park_name": "红岩 · 数字化示范园区",
  "risk_score": 92,
  "statistics": { ... },
  "recent_alerts": [ ... ]
}</pre>
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
    # 纯内联 JS/CSS 实现图表
    
    script = """
    <script>
        // 简易 SVG 图表绘制函数
        function drawLineChart(id, data, color) {
            const svg = document.getElementById(id);
            const width = svg.clientWidth;
            const height = svg.clientHeight;
            const max = Math.max(...data) * 1.2;
            const min = 0;
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

        async function initDashboard() {
            // 1. 获取 Overview
            const overviewRes = await fetch('/api/v1/overview');
            const overview = await overviewRes.json();
            document.getElementById('risk-score').innerText = overview.risk_score;
            document.getElementById('total-files').innerText = overview.total_files;
            document.getElementById('total-records').innerText = overview.total_records.toLocaleString();
            document.getElementById('risk-today').innerText = overview.risk_events_today;
            
            // 2. 获取 Trends
            const trendRes = await fetch('/api/v1/trends');
            const trends = await trendRes.json();
            drawLineChart('trend-chart', trends.risk_scores, '#C62828');
            
            // 3. 获取 Alerts
            const alertRes = await fetch('/api/v1/alerts');
            const alertsData = await alertRes.json();
            const alertList = document.getElementById('alert-list');
            alertList.innerHTML = '';
            alertsData.alerts.forEach(alert => {
                const row = document.createElement('div');
                row.className = 'list-item';
                let tagClass = 'tag-blue';
                if(alert.level === 'HIGH') tagClass = 'tag-red';
                if(alert.level === 'MEDIUM') tagClass = 'tag-orange';
                
                row.innerHTML = `
                    <div style="flex:1;"><span class="tag ${tagClass}">${alert.level}</span></div>
                    <div style="flex:2; font-weight:500;">${alert.type}</div>
                    <div style="flex:3; color:var(--text-grey); font-size:13px;">${alert.source} · ${alert.msg}</div>
                    <div style="flex:1; text-align:right; font-size:12px; color:var(--text-grey);">${alert.time}</div>
                `;
                alertList.appendChild(row);
            });
            
            // 4. 获取 Weather/Air
            const weatherRes = await fetch('/api/v1/weather');
            const weather = await weatherRes.json();
            document.getElementById('weather-temp').innerText = weather.current.temp + '°';
            document.getElementById('weather-cond').innerText = weather.current.condition;
            
            const airRes = await fetch('/api/v1/air');
            const air = await airRes.json();
            document.getElementById('air-aqi').innerText = air.aqi;
            document.getElementById('air-level').innerText = air.level;
            
            // 5. Integrations
            const intRes = await fetch('/api/v1/integrations');
            const intData = await intRes.json();
            const intList = document.getElementById('sys-list');
            intList.innerHTML = '';
            intData.systems.forEach(sys => {
                const item = document.createElement('div');
                item.className = 'card';
                item.style.padding = '16px';
                item.style.marginBottom = '12px';
                item.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:600;">${sys.name}</div>
                        <span class="tag ${sys.status==='ONLINE'?'tag-green':'tag-grey'}">${sys.status}</span>
                    </div>
                    <div style="font-size:12px; color:var(--text-grey); margin-top:4px;">最后同步: ${sys.last_sync}</div>
                `;
                intList.appendChild(item);
            });
            
            // 时钟
            setInterval(() => {
                const now = new Date();
                document.getElementById('clock-time').innerText = now.toLocaleTimeString('en-GB');
            }, 1000);
        }
        
        initDashboard();
    </script>
    """
    
    content = f"""
    <div class="container" style="max-width: 1400px; padding-top: 20px;">
        <!-- Header Info -->
        <div class="grid-12" style="margin-bottom: 24px; align-items: center;">
            <div class="col-4">
                <h2 style="margin:0;">实时合规态势感知</h2>
                <div style="color:var(--text-grey); font-size:14px;">数据更新于: 实时流式计算中</div>
            </div>
            <div class="col-4" style="text-align: center;">
                <div id="clock-time" style="font-size: 32px; font-weight: 700; font-family: monospace;">--:--:--</div>
                <div style="font-size: 14px; color: var(--text-grey);">农历正月十二 · 雨水 · 距清明还有 45 天</div>
            </div>
            <div class="col-4" style="text-align: right; display: flex; justify-content: flex-end; gap: 20px;">
                <div class="card" style="padding: 10px 20px; display: inline-block; min-width: 120px;">
                    <div style="font-size: 12px; color: var(--text-grey);">北京</div>
                    <div><span id="weather-temp" style="font-weight:700; font-size:18px;">--</span> <span id="weather-cond" style="font-size:14px;">--</span></div>
                </div>
                <div class="card" style="padding: 10px 20px; display: inline-block; min-width: 120px;">
                    <div style="font-size: 12px; color: var(--text-grey);">空气质量</div>
                    <div><span id="air-aqi" style="font-weight:700; font-size:18px;">--</span> <span id="air-level" style="font-size:14px;">--</span></div>
                </div>
            </div>
        </div>

        <div class="grid-12">
            <!-- Left Column: Overview Stats -->
            <div class="col-3">
                <div class="card" style="text-align: center; margin-bottom: 20px; padding: 40px 20px;">
                    <div id="risk-score" style="font-size: 80px; font-weight: 800; color: #C62828; line-height: 1;">--</div>
                    <div style="font-size: 14px; color: var(--text-grey); margin-top: 10px; font-weight: 600;">当前合规评分</div>
                </div>
                
                <div class="grid-2" style="gap: 12px; margin-bottom: 20px;">
                    <div class="card" style="padding: 16px; text-align: center;">
                        <div id="risk-today" style="font-size: 24px; font-weight: 700; color: #C62828;">--</div>
                        <div style="font-size: 12px; color: var(--text-grey);">今日高危告警</div>
                    </div>
                     <div class="card" style="padding: 16px; text-align: center;">
                        <div style="font-size: 24px; font-weight: 700; color: #2E7D32;">98%</div>
                        <div style="font-size: 12px; color: var(--text-grey);">已处置率</div>
                    </div>
                </div>

                <div class="card" style="padding: 20px;">
                    <div style="font-size: 12px; color: var(--text-grey);">纳管文件总数</div>
                    <div id="total-files" style="font-size: 24px; font-weight: 600; margin-bottom: 12px;">--</div>
                    <div style="font-size: 12px; color: var(--text-grey);">累计扫描记录</div>
                    <div id="total-records" style="font-size: 24px; font-weight: 600;">--</div>
                </div>
            </div>

            <!-- Middle Column: Trend & Alerts -->
            <div class="col-6">
                <div class="card" style="margin-bottom: 20px; height: 260px; display: flex; flex-direction: column;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <h3>风险趋势 (7日)</h3>
                    </div>
                    <svg id="trend-chart" style="flex: 1; width: 100%;"></svg>
                </div>

                <div class="card" style="min-height: 400px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>实时告警流</h3>
                        <div class="tag tag-blue">Live</div>
                    </div>
                    <div id="alert-list" style="overflow-y: auto; max-height: 320px;">
                        <!-- Alerts injected here -->
                    </div>
                </div>
            </div>

            <!-- Right Column: Systems & Extras -->
            <div class="col-3">
                <div class="card" style="margin-bottom: 20px;">
                    <h3>系统接入状态</h3>
                    <div id="sys-list" style="margin-top: 16px;">
                        <!-- Systems injected here -->
                    </div>
                </div>
                
                 <div class="card">
                    <h3>Top 风险来源</h3>
                    <div style="margin-top: 10px;">
                        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;">
                            <span>财务系统</span>
                            <span style="font-weight:600;">34%</span>
                        </div>
                        <div style="background:#F5F5F7; height:6px; border-radius:3px; margin-bottom:16px;">
                            <div style="width:34%; background:#C62828; height:100%; border-radius:3px;"></div>
                        </div>

                        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;">
                            <span>OA办公</span>
                            <span style="font-weight:600;">28%</span>
                        </div>
                        <div style="background:#F5F5F7; height:6px; border-radius:3px; margin-bottom:16px;">
                            <div style="width:28%; background:#EF6C00; height:100%; border-radius:3px;"></div>
                        </div>

                        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;">
                            <span>访客WIFI</span>
                            <span style="font-weight:600;">15%</span>
                        </div>
                        <div style="background:#F5F5F7; height:6px; border-radius:3px; margin-bottom:16px;">
                            <div style="width:15%; background:#2E7D32; height:100%; border-radius:3px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {script}
    """
    return _page_layout("园区大屏", content, "/park")
