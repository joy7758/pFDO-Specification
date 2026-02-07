# 🧬 pFDO: Physical FAIR Digital Object Specification
> **Toward a Biomimetic Framework for Matter-Digital Sovereignty** > **迈向物质-数字主权的仿生架构规范**

---

## 🏛️ The Three Sovereignty Principles / 三大主权原则

### I. Matter as Sovereign (物质即主权)
Digital existence is subordinate to physical reality. A pFDO is only valid if its physical counterpart maintains integrity within the defined spatial-temporal boundary.
数字存在从属于物理现实。只有当物理实体在定义的时空边界内保持完整性时，pFDO 才具有合法性。

### II. Energy as Logic (能量即逻辑)
State transitions are not free. Every protocol operation must satisfy the thermodynamic constraint ($\Delta S \ge 0$), simulating a digital "metabolism" that prevents unauthorized remote manipulation.
状态转换不是免费的。每项协议操作必须满足热力学约束，通过模拟数字“代谢”来杜绝未经授权的远程操控。

### III. Sovereignty via Complexity (高门槛技术主权)
By leveraging DTR (Digital Type Registry) and maDMP (Machine-actionable DMP), pFDO establishes a high-entry barrier, ensuring technical sovereignty in niche, high-value industrial sectors.
通过利用 DTR（数字类型注册表）和 maDMP（机器可行动 DMP），pFDO 建立了高准入门槛，确保在冷门、高价值工业领域的技术主权。

---

## 🛠️ Core Components / 核心组件

### 1. Metabolic Interface Protocol (MIP) / 代谢接口协议
Defined in `/docs/MIP_Specification.md`. It regulates state transitions based on energy thresholds and physical proximity.
定义于 `/docs/MIP_Specification.md`。基于能量阈值和物理近场逻辑调节状态转换。

### 2. DTR & maDMP Integration / 注册表与机器可行动计划
- **DTR**: Provides semantic epitopes for physical properties. 为物理属性提供语义表位。
- **maDMP**: Enables autonomous lifecycle tracking for physical assets. 实现物理资产的自主生命周期跟踪。

---

## 🕹️ Interactive Demonstrator / 交互式演示器
A real-time visualizer to demonstrate the **MIP state machine** logic.
用于演示 **MIP 状态机** 逻辑的实时可视化工具。

```bash
# Run the lab / 启动实验室
pip install streamlit plotly numpy
python3 -m streamlit run scripts/app_viz_demo.py