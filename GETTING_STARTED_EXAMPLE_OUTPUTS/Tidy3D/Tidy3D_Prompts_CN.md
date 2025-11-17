# Tidy3D 反向设计提示模板（中文）

本文件提供用于 Tidy3D 伴随法 / 拓扑优化的高质量中文提示模板，包含：
- 通用模板（可覆盖大多数平面光子器件）
- 设备定制变体（光栅耦合器、模式转换器、1x2 MMI）
- 建议的输出 JSON 结构（便于自动解析）

注意：
- 强制 LLM 仅输出 JSON，避免自然语言干扰解析；如果需要解释，请放入 `notes` 字段。
- 将“占位变量”按需替换，例如 `<band_nm>`, `<t_si_nm>` 等。
- 约束需结合工艺（最小特征、层厚、刻蚀深度）与仿真精度（网格、PML、采样）。

---

## 一、通用模板（伴随/拓扑优化）

系统角色与风格：
- 你是一名资深光子器件优化工程师，精通 Tidy3D、FDTD 及光子工艺设计规则。
- 输出必须为严格 JSON（UTF-8，无注释，无 Markdown 代码块标记）。

任务描述（模板）：
- 目标：在 <band_nm> 波段实现 <device_type>，优化目标为 <primary_metric>，兼顾 <secondary_metric_list>。
- 设计域：大小 <Lx_um>×<Ly_um>×<Lz_um> μm，位于 SOI 堆叠（Si 厚度 <t_si_nm> nm，BOX 厚度 <t_box_um> μm，上包层 SiO2/空气）。
- 端口：输入端 <in_port>，输出端 <out_ports>（数量与位置说明）。
- 材料与工艺：
  - Si 折射率使用 Tidy3D 内置材料库或指定色散模型。
  - 刻蚀类型：<full_etch|partial_etch>，刻蚀深度 <etch_depth_nm> nm。
  - 最小特征尺寸 <min_feature_nm> nm；建议形态滤波与最小化约束。
- 仿真设置：
  - 波长采样：中心 <lambda0_nm> nm，带宽 <span_nm> nm，采样点 <samples>。
  - 边界条件：PML（厚度 <pml_thk_um> μm）。
  - 网格：<= <mesh_nm> nm；对高折射梯度区域开启自适应细化。
  - 监视器：功率 / 功率谱 / 模态投影；定义端口模式为 TE<order>。
- 优化策略：
  - 方法：<adjoint|topology>，参数化 <levelset|density>，正则化 <TV|滤波半径>。
  - 目标函数：主目标 <primary_metric>（示例：插入损耗最小、耦合效率最大、串扰最小），次要目标权重 <weights>。
  - 迭代步数 <n_iter>，学习率 <lr>，每迭代保存中间版图与指标。
- 约束与对称：
  - 对称性（如镜像/旋转）以减少设计自由度与提高可制造性。
  - 端口区域保护（buffer zone）与接入锥形（taper）固定不优化。
- 产出要求：
  - 严格 JSON，字段见 `schema`，包含：`simulation`, `materials`, `geometry_param`, `ports`, `monitors`, `optimization`, `postprocess`。

输出 JSON 结构（schema）参考：
{
  "title": "<短标题>",
  "notes": "<可选，简短说明，仅此处允许自然语言>",
  "wavelengths": {"central_nm": <lambda0_nm>, "span_nm": <span_nm>, "samples": <samples>},
  "stack": {
    "substrate": {"material": "SiO2", "thickness_um": null},
    "box": {"material": "SiO2", "thickness_um": <t_box_um>},
    "device": {"material": "Si", "thickness_nm": <t_si_nm>},
    "clad_top": {"material": "SiO2", "thickness_um": <t_clad_um>, "override_air": false}
  },
  "simulation": {
    "domain_um": [<Lx_um>, <Ly_um>, <Lz_um>],
    "boundary": "pml",
    "pml_um": [<pmlx>, <pmly>, <pmlz>],
    "mesh_max_nm": <mesh_nm>,
    "symmetry": {"enable": <true|false>, "axes": ["x"], "phase_correction": false}
  },
  "ports": [
    {"name": "in", "type": "mode", "location": [<x>, <y>, <z>], "axis": "+x", "mode": {"pol": "TE", "order": 0}},
    {"name": "out1", "type": "mode", "location": [<x>, <y>, <z>], "axis": "-x", "mode": {"pol": "TE", "order": 0}}
  ],
  "monitors": [
    {"name": "s_out", "type": "mode_power", "ref_port": "out1"}
  ],
  "materials": {
    "Si": {"model": "td.material_db", "name": "Si"},
    "SiO2": {"model": "td.material_db", "name": "SiO2"}
  },
  "geometry_param": {
    "parametrization": "density|levelset",
    "region_um": [<x0>, <y0>, <x1>, <y1>],
    "min_feature_nm": <min_feature_nm>,
    "filter_radius_nm": <filter_nm>,
    "fixed_regions": [{"name": "port_tapers", "boxes": [[...]]}]
  },
  "optimization": {
    "method": "adjoint|topology",
    "objective": {
      "primary": {"metric": "efficiency|insertion_loss|xtalk", "target": "max|min", "port": "out1"},
      "secondary": [{"metric": "xtalk", "port": "out2", "weight": 0.1}]
    },
    "schedule": {"n_iter": <n_iter>, "lr": <lr>, "save_every": 10}
  },
  "postprocess": {
    "exports": ["gds", "png", "config_json"],
    "binarize_threshold": 0.5
  }
}

使用说明：
- 将上述模板直接投喂给 LLM，并要求“仅输出 JSON”。
- 将生成的 JSON 直接用于你自己的 Tidy3D 驱动脚本（或我们提供的 `tidy3d_runner` 扩展）。

---

## 二、设备变体模板

### 1) 光栅耦合器（垂直耦合，C 波段）
- 目标：最大化光纤（NA≈0.12，8°倾角）耦合效率，工作波段 1530–1570 nm，中心 1550 nm。
- 端口：
  - 输入：光纤入射（等效为上方倾斜平面波/模式源）；
  - 输出：芯片内波导 TE0 模式端口。
- 工艺：
  - Si 厚 <t_si_nm>=220 nm，部分刻蚀 <etch_depth_nm>=70 nm；
  - 最小特征 <min_feature_nm>=120 nm；
  - 可施加线性 chirp、占空比/周期参数化或拓扑密度法。
- 约束：背反射 < -20 dB；旁瓣抑制；对称/锥形缓冲保留。
- 建议 schema 特化：
  - `ports` 中包含一个顶部入射端（可用面源近似）与一个平面波导端口；
  - 在 `objective.primary` 使用效率最大化，监视器放在波导端口位置。

### 2) 模式转换器（TE0 → TE1，片上）
- 目标：TE0(输入) → TE1(输出) 转换效率最大，TE0 → TE0 残留最小；1550 ± 25 nm；
- 工艺：全刻蚀，min feature 100 nm；保持长度 < 20 μm；
- 约束：
  - 端口固定区 2 μm 不参与优化；
  - 中心线镜像约束可选；
  - 抑制向 TM 模式泄露（添加次要目标）。
- 建议 schema 特化：
  - `ports` 定义输入 TE0 和输出 TE1（order: 1）；
  - `optimization.secondary` 添加对其他模式的抑制（如 TE0@out）。

### 3) 1x2 MMI 分束器（50/50）
- 目标：插入损耗最小，两个输出端口等幅相位（50/50±1%）；
- 工艺：Si 220 nm；部分刻蚀 70 nm；min feature 120 nm；
- 建议 schema 特化：
  - `objective.secondary` 中加入两输出功率差异的惩罚项；
  - 可加入对相位匹配的约束（差相位 ≈ 0）。

---

## 三、最小可用 JSON 示例（模式转换器）
{
  "title": "TE0_to_TE1_Mode_Converter_Adjoint",
  "notes": "以拓扑密度参数化 + TV 正则化；端口缓冲区 2 μm 固定",
  "wavelengths": {"central_nm": 1550.0, "span_nm": 50.0, "samples": 11},
  "stack": {
    "substrate": {"material": "SiO2", "thickness_um": null},
    "box": {"material": "SiO2", "thickness_um": 2.0},
    "device": {"material": "Si", "thickness_nm": 220},
    "clad_top": {"material": "SiO2", "thickness_um": 1.5, "override_air": false}
  },
  "simulation": {
    "domain_um": [20.0, 4.0, 2.0],
    "boundary": "pml",
    "pml_um": [1.0, 1.0, 1.0],
    "mesh_max_nm": 20,
    "symmetry": {"enable": false, "axes": [], "phase_correction": false}
  },
  "ports": [
    {"name": "in", "type": "mode", "location": [0.5, 0.0, 1.0], "axis": "+x", "mode": {"pol": "TE", "order": 0}},
    {"name": "out", "type": "mode", "location": [19.5, 0.0, 1.0], "axis": "+x", "mode": {"pol": "TE", "order": 1}}
  ],
  "monitors": [
    {"name": "m_out", "type": "mode_power", "ref_port": "out"}
  ],
  "materials": {
    "Si": {"model": "td.material_db", "name": "Si"},
    "SiO2": {"model": "td.material_db", "name": "SiO2"}
  },
  "geometry_param": {
    "parametrization": "density",
    "region_um": [2.0, -1.0, 18.0, 1.0],
    "min_feature_nm": 100,
    "filter_radius_nm": 80,
    "fixed_regions": [{"name": "port_buffers", "boxes": [[0.0, -1.0, 2.0, 1.0], [18.0, -1.0, 20.0, 1.0]]}]
  },
  "optimization": {
    "method": "adjoint",
    "objective": {
      "primary": {"metric": "efficiency", "target": "max", "port": "out"},
      "secondary": [
        {"metric": "mode_leak", "port": "out", "mode": {"pol": "TE", "order": 0}, "weight": 0.2}
      ]
    },
    "schedule": {"n_iter": 150, "lr": 0.05, "save_every": 10}
  },
  "postprocess": {"exports": ["gds", "png", "config_json"], "binarize_threshold": 0.5}
}

---

## 四、使用建议
- 在调用时，前置“仅输出 JSON”的强约束，并在解析失败时让 LLM 重试；
- 若你的流程需要 DOT/DSL → Tidy3D 映射，建议固定端口缓冲与 tapers，不参与优化；
- 真实大规模 FDTD 运行前，先用小网格/短时间 sanity check（如 `simulation` 中网格与域减小，`n_iter` 降到 5-10）。
