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
