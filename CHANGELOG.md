# CHANGELOG

## 2025-11-03

本次更新重点提升系统鲁棒性与自动化纠错能力：

### 修复
- 过滤未知组件参数，避免 `unexpected keyword argument`，例如自动移除 `waveguide_width`。
- 顶层端口名与实例名不一致（DOT 名如 `C1` 与 DSL 名如 `N1`）导致的构建失败：新增 DOT→DSL 节点名映射。
- 端口数量不足引发 `at least 2 ports need to be defined`：自动补足至少两个外部端口。
- YAML/JSON 解析不稳定：优先使用严格 JSON 解析，失败回退 YAML，并清理 Markdown 围栏与含冒号字段。
- DOT 解析失败：清洗 DOT、补全大括号、保存无效 DOT 至 `build/invalid_dot_*.dot`，并在无法提取坐标时回退线性布局。
- 端口解析允许包含额外冒号，避免 `too many values to unpack`。

### 改进
- 组件选择阶段的交互稳定性：按钮始终可见（提交/自动选择/重置）。
- 放置与别名匹配：根据 DOT label 的 DSL id 建立别名并大小写不敏感匹配，降低 `KeyError` 概率。
- netlist 转换：对缺失 `placement` 的节点提供回退坐标，避免 `KeyError: 'placement'`。

### 使用提示
- 启动建议：
	- 本地：`streamlit run PhotonicsAI/Photon/webapp.py`
	- 远程：`--server.address 0.0.0.0 --server.port 8501` 并做好端口开放/转发。
- LLM 配置：`.env` 配置 `LLM_MODEL`、`LLM_API_KEY`、`LLM_BASE_URL`。

### 兼容性
- 对现有 DSL/模板兼容。如需 `mzi_2x2_heater_tin_cband` 支持可调宽度，后续可在组件中新增参数（默认不变）。

### 已知问题
- 若 LLM 输出混有自然语言/Markdown，仍可能走兜底路径；建议尽量使用纯 JSON/DOT 输出。
- 无效 DOT 会存储在 `build/invalid_dot_*.dot`，方便后续诊断与优化。
