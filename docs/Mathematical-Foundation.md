# Mathematical Foundation of pFDO & MIP Protocol
# pFDO 架构与 MIP 协议的数学基础

## 1. Information-Physical Mapping / 信息-物理映射
We define a pFDO as a mapping $\mathcal{M}$ from the physical state space $\mathcal{P}$ to the digital semantic space $\mathcal{S}$:
我们将 pFDO 定义为从物理状态空间 $\mathcal{P}$ 到数字语义空间 $\mathcal{S}$ 的映射 $\mathcal{M}$：
$$\mathcal{M}: \mathcal{P} \xrightarrow{E} \mathcal{S}$$
where $E$ is the ambient energy activation function.
其中 $E$ 为环境能量激发函数。

## 2. MIP Sovereignty Verification / MIP 主权验证逻辑
The security of the Matter-Immune Protocol (MIP) is grounded in the spatial manifold distance of backscatter signals.
MIP 协议的安全性建立在反向散射信号的空间流形距离之上。

Let $s$ be the received signal fingerprint and $\Gamma$ be the pre-registered Physical Epitope. The verification $V$ is defined as:
设 $s$ 为接收到的信号指纹，$\Gamma$ 为预注册的物理表位。验证函数 $V$ 定义为：
$$V(s, \Gamma) = \begin{cases} 1, & \text{if } \|s - \Gamma\|_2 < \epsilon \text{ and } \text{RSSI} > \tau \\ 0, & \text{otherwise} \end{cases}$$
- $\|\cdot\|_2$: Euclidean distance in the signal feature space. (信号特征空间中的欧几里得距离)
- $\tau$: Physical sovereignty boundary threshold. (物理主权边界阈值)

## 3. Thermodynamic Constraint / 热力学约束
To prevent resource exhaustion attacks, every state update $\Delta \sigma$ must satisfy the Landauer-based energy constraint:
为防止资源枯竭攻击，任何状态更新 $\Delta \sigma$ 必须满足基于兰道尔原理的能量约束：
$$W_{input} \ge k_B T \ln 2 \cdot I(\Delta \sigma)$$
where $I(\Delta \sigma)$ is the information entropy change of the update.
其中 $I(\Delta \sigma)$ 为该次更新的信息熵变化。
