import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. 页面设置
st.set_page_config(page_title="pFDO 协议演示器", layout="wide")

# 2. 侧边栏：环境模拟
st.sidebar.header("🌍 环境模拟器")
energy = st.sidebar.slider("🔋 捕获能量 (Energy)", 0.0, 1.5, 0.5, 0.1)
rssi = st.sidebar.slider("📡 信号强度 (RSSI dBm)", -100, -30, -80, 5)

# 3. 核心协议逻辑
mip_passed = rssi > -65 
thermo_gate_open = energy >= 0.8

if not mip_passed:
    status, color = "拒绝访问 (MIP 失败)", "red"
elif not thermo_gate_open:
    status, color = "已激活 (能量不足/锁定)", "orange"
else:
    status, color = "代谢更新中 (全功能开启)", "green"

# 4. 主界面显示
st.title("🧬 pFDO 仿生协议交互演示系统")
st.markdown(f"### 当前对象状态: <span style='color:{color};'>{status}</span>", unsafe_allow_html=True)

# 5. 绘制状态相图
st.markdown("---")
st.subheader("📊 协议状态空间相图")

# 生成绘图数据
x_range = np.linspace(-100, -30, 50)
y_range = np.linspace(0, 1.5, 50)
X, Y = np.meshgrid(x_range, y_range)
Z = np.zeros_like(X)
Z[(X > -65) & (Y < 0.8)] = 1
Z[(X > -65) & (Y >= 0.8)] = 2

# 使用 Plotly 绘图
fig = go.Figure(data=go.Contour(
    z=Z, x=x_range, y=y_range, 
    colorscale=[[0, 'red'], [0.5, 'orange'], [1, 'green']],
    showscale=False
))

# 标出当前点 (注意这里的语法：全部使用 key=value 形式，防止报错)
fig.add_trace(go.Scatter(
    x=[rssi], 
    y=[energy], 
    mode='markers+text', 
    text=["pFDO 位置"], 
    textposition="top center",
    marker=dict(size=15, color='blue', line=dict(width=2, color='white'))
))

fig.update_layout(
    xaxis_title="信号强度 (RSSI dBm)",
    yaxis_title="环境能量 (Energy)",
    height=500
)

st.plotly_chart(fig, use_container_width=True)
st.caption("© 2026 pFDO Architecture")