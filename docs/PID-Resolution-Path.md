# PID Resolution Path & Binding Logic
# PID 解析路径与绑定逻辑

## 1. The Resolution Chain / 解析链
In the pFDO ecosystem, a Persistent Identifier (PID) does not merely point to a URL; it resolves to a structured **Kernel Record** through a multi-layer binding process.
在 pFDO 生态中，PID 不仅仅指向一个 URL，它通过多层绑定过程解析为结构化的**内核记录**。

### Formal Resolution Function / 形式化解析函数
Let $H$ be the global Handle System. The resolution of a pFDO PID $\pi$ is defined as:
设 $H$ 为全球 Handle 系统。pFDO PID $\pi$ 的解析定义为：
$$R(\pi) \xrightarrow{H} \{K, D, P\}$$
Where:
- $K$: Kernel Metadata (Storage, Checksum, Auth)
- $D$: DTR Pointer (Link to pFDO-DTR-Definitions.json)
- $P$: Policy Pointer (Link to pFDO-Policy-maDMP.json)

## 2. Multi-stage Redirection / 多级重定向逻辑

### Step 1: Global Prefix Routing
The resolver identifies the pFDO prefix (e.g., `21.T12345`) and routes the query to the authoritative Local Handle Service (LHS).

### Step 2: Kernel Attribute Extraction
The LHS returns a JSON-LD snippet containing the **MIP Verification Requirement**. 
LHS 返回包含 **MIP 验证需求** 的 JSON-LD 片段。

### Step 3: Semantic Binding
The client fetches the Data Type definition from the DTR to understand how to process the physical manifold signals.
客户端从 DTR 获取数据类型定义，以理解如何处理物理流形信号。

## 3. Physical-Digital Binding / 物理-数字绑定锚点
To prevent "PID Spoofing," pFDO mandates that the resolution process is only completed when the **MIP Handshake** returns a valid state. 
为防止 PID 欺诈，pFDO 强制要求解析过程仅在 **MIP 握手** 返回有效状态时才算完成。
