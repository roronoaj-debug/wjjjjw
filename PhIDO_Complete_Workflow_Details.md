# PhIDO 完整工作流程详细说明

> 基于所有流程相关问题的完整梳理 - 精确到函数级别

---

## 📊 核心阶段对照表

| **阶段** | **主要函数** | **输入数据** | **输出数据** | **AI参与** | **代码位置** |
|---------|------------|------------|------------|----------|------------|
| **Phase 0<br/>意图分类** | `llm_api.intent_classification()` | `session.current_message` | `PromptClass(category_id, response)` | ✅ 硬编码prompt | llm_api.py:1304-1328 |
| **Phase 1<br/>实体抽取** | `llm_api.entity_extraction()` | 用户描述文本 | `session.p200_pretemplate` (YAML) | ✅ 模板选择<br/>sp_normal / sp_paper | llm_api.py:1374-1450<br/>≤1000字符/≥1000字符 |
| | `llm_api.preschematic()` | `p200_pretemplate` | `session.p200_preschematic` (DOT) | ✅ prompts.yaml:dot_simple | llm_api.py:1489-1494 |
| **Phase 2<br/>组件检索** | `llm_api.llm_search()` | `components_list` / `templates_dict` | `p200_componenets_search_r`<br/>`p200_retreived_templates` | ✅ 语义搜索 | llm_api.py (搜索) |
| | UI 选择界面 | 搜索结果 | `p200_selected_components`<br/>或 `p200_selected_template` | ❌ 用户手动选择 | webapp.py:2322-2456 |
| **Phase 3A<br/>组件路径DSL** | `map_pretemplate_to_template()` | `pretemplate` + 选中组件 | `session.p300_circuit_dsl` | ❌ 确定性构建 | webapp.py:876-907 |
| **Phase 3B<br/>模板路径DSL** | UI 规格输入 | 用户手动输入specs | `session.user_specs` | ❌ 用户输入 | webapp.py:2568-2574 |
| | `llm_api.parse_user_specs()` | `user_specs` + template schema | parsed_spec 或 Error | ✅ 验证兼容性 | llm_api.py:1511-1576 |
| **Phase 4<br/>原理图生成** | `get_ports_info()` | `circuit_dsl` | 带端口信息的DSL | ❌ 组件内省 | DemoPDK.py |
| | `get_params()` | `circuit_dsl` | 带参数信息的DSL | ❌ 组件内省 | DemoPDK.py |
| | `llm_api.apply_settings()` | `circuit_dsl` | 带参数值的DSL | ✅ 仅组件路径 | llm_api.py:1578+ |
| | `utils.circuit_to_dot()` | `circuit_dsl` | DOT string (无边) | ❌ 格式转换 | utils.py:58-112 |
| | `llm_api.dot_add_edges()` | `dot_string` + nodes | DOT with edges | ✅ 组件路径 | llm_api.py:1153-1186 |
| | `llm_api.dot_add_edges_templates()` | `dot_string` + template | DOT with edges | ✅ 模板路径 | llm_api.py:1229-1263 |
| | `utils.dot_planarity()` | `dot_string` | happy_flag (bool) | ❌ 几何计算 | utils.py:728-815 |
| | `llm_api.dot_add_edges_errorfunc()` | `dot_string` with crosses | Fixed DOT | ✅ 迭代4次 | llm_api.py:1188-1227 |
| | `utils.edges_dot_to_yaml()` | DOT edges | `circuit_dsl` with edges | ❌ 解析转换 | utils.py |
| | `footprint_netlist()` | `circuit_dsl` | `footprints_dict` + DSL | ❌ 组件尺寸 | DemoPDK.py |
| | `utils.get_graphviz_placements()` | scaled DOT | node coordinates | ❌ Graphviz | utils.py:277-302 |
| | `utils.add_placements_to_dsl()` | coordinates | DSL with placements | ❌ 合并数据 | utils.py |
| | `utils.add_final_ports()` | DSL | DSL with final ports | ❌ 端口定义 | utils.py |
| **Phase 5<br/>版图与仿真** | `utils.dsl_to_gf()` | `p300_circuit_dsl` | `p400_gf_netlist` | ❌ 参数过滤 | utils.py:139-198 |
| | `yaml_netlist_to_gds()` | gf_netlist | GDS Component `c` | ❌ GDSFactory | DemoPDK.py:118-210 |
| | `c.get_netlist(recursive=True)` | Component | recursive netlist | ❌ 递归展开 | GDSFactory |
| | `sax.circuit()` | netlist + models | SAX model function | ❌ 电路组装 | SAX |
| | `c.plot()` | Component | Matplotlib Figure | ❌ 可视化 | GDSFactory |
| **5A SAX仿真** | `session.p400_sax_circuit(wl)` | wavelength array | S-parameters dict | ❌ 预计算插值 | SAX runtime |
| | `utils.plot_dict_arrays()` | wl + S-params | plot_sax.png | ❌ Matplotlib | utils.py:606-654 |
| **5B GDS显示** | `st.pyplot()` | gdsfig | UI显示 | ❌ Streamlit | webapp.py:2752-2753 |
| **5C DRC检查** | `c.write_gds()` | Component | placeholder.gds | ❌ GDS2格式 | GDSFactory |
| | `run_drc()` | gds_file_path | report.lydrb | ❌ KLayout批处理 | drc.py:11-64 |
| **5D 优化(禁用)** | `circuit_optimizer()` | circuit_dsl | optimized netlist | ❌ 当前=0 | webapp.py:2898 |

---

## 🔀 关键决策点

### 1️⃣ 意图分类门槛（Phase 0）
```python
# llm_api.py:1304-1328
if interpreter_cat.category_id != 1:
    # 拒绝执行，返回说明文本
    st.markdown(interpreter_cat.response)
else:
    # 继续Phase 1
```

### 2️⃣ 实体抽取模板选择（Phase 1）
```python
# llm_api.py:1439-1441
if len(input_prompt) > 1000:
    sys_prompt = sp_paper  # 长文本/论文模板
else:
    sys_prompt = sp_normal  # 短文本模板
```

### 3️⃣ 组件 vs 模板路径分叉（Phase 2.5 → Phase 3）
```python
# webapp.py:2467-2650
if session.components_selected:
    # 组件路径：map_pretemplate_to_template()
    # 无需用户输入specs
elif session.template_selected:
    # 模板路径：UI输入specs → parse_user_specs()
    # 需要用户显式输入参数值
```

### 4️⃣ 原理图边生成策略（Phase 4）
```python
# webapp.py:2478-2490 (组件路径)
if not session.template_selected:
    llm_api.apply_settings()  # AI生成参数
    llm_api.dot_add_edges()   # AI生成边

# webapp.py:2667-2672 (模板路径)
else:
    # 跳过apply_settings（已有用户specs）
    llm_api.dot_add_edges_templates()  # 模板特定边
```

### 5️⃣ 交叉边修复循环（Phase 4）
```python
# webapp.py:2495-2509
for attempt in range(4):
    happy_flag = utils.dot_planarity(dot_string)
    if happy_flag:
        break  # 无交叉，退出
    else:
        dot_string = llm_api.dot_add_edges_errorfunc(session)
```

### 6️⃣ GDS写入容错策略（Phase 5C）
```python
# webapp.py:2768-2839
try:
    c.write_gds(gds_path)
except "layer numbers larger than 65535":
    try:
        c.flatten().write_gds(gds_path)  # 尝试flatten
    except:
        try:
            c.write_gds(gds_path, max_points=None)  # 修改参数
        except:
            skip_drc = True  # 全部失败，跳过DRC
```

---

## 📦 关键数据结构

### pretemplate (Phase 1输出)
```yaml
title: "2x2 MZI with Phase Shifter"
brief_summary: "Mach-Zehnder interferometer"
circuit_instructions: "Connect MZI arms with phase shifters"
components_list:
  - mzi_2x2
  - phase_shifter_thermal
```

### Circuit DSL (Phase 3/4核心数据)
```yaml
doc:
  title: "MZI Circuit"
  description: "..."
nodes:
  N1:
    component: "mzi_2x2"
    params:
      delta_length: 10.0  # Phase 4添加
    placement:           # Phase 4末尾添加
      x: 0.0
      y: 0.0
    ports:
      o1: {x: 100, y: 0}  # Phase 4添加
edges:
  E1:
    link: "N1:o2:N2:i1"  # Phase 4添加
    properties:
      type: "route"
properties:
  specs:  # 仅模板路径有此字段
    wavelength: 1550
```

### GDSFactory Netlist (Phase 5输入)
```yaml
name: "mzi_circuit_abc123"
instances:
  N1:
    component: "mzi_2x2"
    settings:
      delta_length: 10.0
routes:
  E1:
    links:
      N1:o2: N2:i1
placements:
  N1: {x: 0, y: 0}
ports:
  o1: N1,o1
```

---

## 🎯 AI参与边界总结

| **阶段** | **AI角色** | **确定性工具** |
|---------|-----------|--------------|
| **Phase 0** | intent_classification (门卫) | - |
| **Phase 1** | entity_extraction, preschematic | - |
| **Phase 2** | llm_search (语义搜索) | UI手动选择 |
| **Phase 3-组件** | - | map_pretemplate_to_template |
| **Phase 3-模板** | parse_user_specs (验证) | UI手动输入specs |
| **Phase 4-组件** | apply_settings, dot_add_edges, errorfunc | circuit_to_dot, dot_planarity |
| **Phase 4-模板** | dot_add_edges_templates, errorfunc | 同左 |
| **Phase 5** | **无AI** | GDSFactory, SAX, KLayout |
| **Phase 5-Tidy3D** | **无AI** (完整分支需GDS) | Tidy3D FDTD |

---

## 🔄 Session State关键字段

| **字段名** | **类型** | **含义** | **设置位置** |
|-----------|---------|---------|------------|
| `step_by_step_mode` | bool | 分步/自动模式 | webapp.py:1408 |
| `current_message` | str | 当前输入文本 | webapp.py:1155-1172 |
| `entity_extraction_complete` | bool | Phase 1完成标志 | webapp.py:2318 |
| `component_search_complete` | bool | Phase 2完成标志 | webapp.py:2413/2364 |
| `schematic_complete` | bool | Phase 4完成标志 | webapp.py:2540/2650 |
| `components_selected` | bool | 组件路径标志 | webapp.py:2413 |
| `template_selected` | bool | 模板路径标志 | webapp.py:2364 |
| `p200_pretemplate` | dict | 实体抽取结果 | llm_api.py:1374-1450 |
| `p200_selected_components` | list[str] | 选中组件名 | webapp.py:2407 |
| `p200_selected_template` | str | 选中模板ID | webapp.py:2362 |
| `p300_circuit_dsl` | dict | 电路DSL | webapp.py:2467-2650 |
| `p300_dot_string` | str | DOT图定义 | webapp.py:2488-2672 |
| `p400_gf_netlist` | dict | GDSFactory netlist | webapp.py:2728 |
| `p400_sax_circuit` | function | SAX仿真函数 | DemoPDK.py:186-191 |
| `p400_gdsfig` | Figure | GDS可视化图 | DemoPDK.py:201-202 |

---

## 📈 性能优化策略

### 1. 参数过滤缓存 (utils.dsl_to_gf)
```python
@lru_cache(maxsize=256)
def _allowed_settings_for(component_name: str) -> set:
    # 缓存组件合法参数，避免重复查询
```

### 2. 并行路径执行 (Phase 5)
```python
# SAX仿真、GDS显示、DRC检查可独立执行
# webapp.py:2740-2839
```

### 3. 容错降级 (Phase 5)
```python
# 路由失败 → ignore_links=True
# GDS写入失败 → flatten → 修改参数 → skip_drc
```

---

## 🚨 常见错误处理

| **错误类型** | **位置** | **处理策略** |
|------------|---------|-------------|
| 意图分类失败 | Phase 0 | 返回拒绝消息 |
| 组件搜索无结果 | Phase 2 | 允许手动输入或使用模板 |
| 模板specs验证失败 | Phase 3B | 返回Error，重新输入 |
| DOT交叉边 | Phase 4 | 迭代修复4次，失败则保留 |
| GDS路由失败 | Phase 5 | ignore_links重试 |
| GDS大层号 | Phase 5C | flatten → 修改参数 → 跳过DRC |
| SAX端口不足 | Phase 5A | 使用dummy circuit |

---

## 🔗 外部工具依赖

| **工具** | **用途** | **阶段** | **必需性** |
|---------|---------|---------|-----------|
| **OpenAI/Claude等LLM** | 实体抽取、边生成 | Phase 0-4 | ✅ 必需 |
| **GDSFactory** | GDS生成、可视化 | Phase 5 | ✅ 必需 |
| **SAX** | 电路仿真 | Phase 5A | ✅ 必需 |
| **KLayout** | DRC检查 | Phase 5C | ⚠️ 推荐 |
| **Graphviz** | 布局计算 | Phase 4 | ✅ 必需 |
| **Tidy3D** | FDTD仿真 | Phase 5D | ❌ 可选 |

---

## 📂 文件结构对应

```
PhotonicsAI/Photon/
├── webapp.py           # 主流程编排 (2914行)
│   ├── Phase 0-2      # 2267-2456
│   ├── Phase 3-4      # 2458-2650
│   └── Phase 5        # 2654-2914
├── llm_api.py          # LLM调用 (1763行)
│   ├── intent_classification  # 1304-1328
│   ├── entity_extraction      # 1374-1450
│   ├── preschematic           # 1489-1494
│   ├── parse_user_specs       # 1511-1576
│   ├── apply_settings         # 1578+
│   ├── dot_add_edges          # 1153-1186
│   └── dot_add_edges_errorfunc # 1188-1227
├── utils.py            # 工具函数 (863行)
│   ├── dsl_to_gf              # 139-198
│   ├── circuit_to_dot         # 58-112
│   ├── dot_planarity          # 728-815
│   └── plot_dict_arrays       # 606-654
├── DemoPDK.py          # 组件库接口 (498行)
│   ├── yaml_netlist_to_gds    # 118-210
│   ├── get_ports_info         # 组件内省
│   └── footprint_netlist      # 尺寸获取
└── drc/drc.py          # DRC检查 (70行)
    └── run_drc                # 11-64
```

---

## 🎓 学习路径建议

1. **入门**: 跟踪自动模式单次运行，观察session state变化
2. **理解数据流**: Circuit DSL格式 → DOT图 → GDSFactory netlist
3. **深入Phase 4**: 原理图生成的多步骤转换和坐标计算
4. **优化理解**: 为什么需要两次转换（DSL→Netlist→GDS）
5. **扩展**: 如何添加新组件到DesignLibrary

---

**生成时间**: 2026-02-12  
**基准版本**: PhIDO main branch  
**覆盖所有流程相关问题**: ✅ 完整
