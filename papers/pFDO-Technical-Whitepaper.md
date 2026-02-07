# pFDO Technical Whitepaper v1.1: The Biomimetic Protocol
# pFDO 技术白皮书 v1.1：仿生协议规范

## Section 1: Finite State Machine (FSM) / 有限状态机模型

To ensure the deterministic behavior of physical assets in decentralized environments, pFDO follows a rigorous FSM.
为确保物理资产在去中心化环境中的确定性行为，pFDO 遵循严格的有限状态机模型。

### 1.1 State Definitions / 状态定义
- **S_0 (Dormant)**: Passive state. Energy level below threshold $E_{min}$.
  **休眠态**：被动状态。能量水平低于阈值 $E_{min}$。
- **S_1 (Active)**: Authenticated state via MIP. Ready for interaction.
  **激活态**：通过 MIP 协议验证后的状态。准备进行交互。
- **S_2 (Metabolic)**: Executing state update or data transfer. Consuming energy.
  **代谢态**：执行状态更新或数据传输。正在消耗能量。

### 1.2 Transition Logic / 转移逻辑
The transition $\delta$ is triggered by the input vector $\Sigma = \langle V, E \rangle$, where $V \in \{0, 1\}$ is MIP verification and $E$ is harvested energy.
状态转移 $\delta$ 由输入向量 $\Sigma = \langle V, E \rangle$ 触发，其中 $V$ 为 MIP 验证结果，$E$ 为捕获能量。

| Current State | Input (V, E) | Next State | Action |
| :--- | :--- | :--- | :--- |
| S_0 (Dormant) | V=1, E > E_min | S_1 (Active) | Wake up & Pulse |
| S_1 (Active) | V=1, E > E_metabolic | S_2 (Metabolic) | Open Thermodynamic Gate |
| S_2 (Metabolic) | Update Complete | S_0 (Dormant) | Reset & Cool down |
---

## Section 2: Data Type Registry (DTR) Mapping / 数据类型注册表映射

To achieve machine-actionability, pFDO defines specific data types to be registered in the FDO-DTR ecosystem.
为实现机器可执行性，pFDO 定义了需在 FDO-DTR 生态中注册的特定数据类型。

### 2.1 Physical Epitope Profile (Type ID: pFDO_Epitope_v1)
A digital representation of the signal manifold decay signatures.
信号流形衰减特征的数字表示。
- **Attributes**: `decay_slope`, `spatial_entropy`, `rssi_gradient`.
- **Validation**: Cross-referenced with the MIP-Manifold distance function.

### 2.2 Metabolic Cost Metrics (Type ID: pFDO_Metabolism_v1)
Defines the mapping between digital operations and thermodynamic costs.
定义数字操作与热力学代价之间的映射关系。
- **Unit**: `$\mu J/bit$` (Micro-Joules per bit updated).
- **Constraint**: $\Delta E \ge k_B T \ln 2$.

---

## Section 3: PID Kernel Metadata Extension / PID 内核元数据扩展

The PID (Persistent Identifier) for a pFDO must resolve to a kernel record containing the following attributes:
pFDO 的 PID（持久标识符）解析后必须包含以下内核记录属性：

1. **`hasMIPCapability`**: Boolean. Indicates if the asset supports physical-layer auth.
2. **`energyHarvestingProfile`**: Describes the AmBC (Ambient Backscatter) frequency range.
3. **`authoritativeLocation`**: The physical sovereignty coordinate defined by the last verified MIP event.
