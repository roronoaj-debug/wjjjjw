# 论文参数提取模板 (Paper Extraction Template)

从论文中提取信息以添加组件到 DesignLibrary 的标准流程。

---

## 1. 基础信息 (Basic Info)

| 字段 | 说明 | 位置 | 示例值 |
|-----|------|------|-------|
| **组件名称** | 英文小写下划线命名 | 自定义 | `add_drop_ring_resonator` |
| **中文名称** | 器件中文描述 | 论文标题 | 硅基环形谐振器滤波器 |
| **功能描述** | 1-2句话描述功能 | Abstract | 用于WDM的add-drop滤波器 |
| **工作波段** | C-band/O-band/自定义 | Methods | C-band (1530-1565nm) |
| **论文DOI** | 参考文献 | 论文首页 | `10.1364/OE.xxx` |
| **来源** | 期刊/会议 | 论文首页 | Nature Photonics |

---

## 2. 端口定义 (Port Definition)

| 字段 | 说明 | 位置 |
|-----|------|------|
| **端口数量** | 总光学端口数 | 器件示意图 |
| **端口命名** | 按PhIDO规范: o1, o2... | - |
| **端口功能** | 每个端口的作用 | 器件示意图 |

### 常见端口配置示例：

```yaml
# Add-Drop Ring (4端口)
ports:
  - name: o1, function: input
  - name: o2, function: through
  - name: o3, function: add 
  - name: o4, function: drop

# MZI (2端口 或 4端口)
ports:
  - name: o1, function: input
  - name: o2, function: output

# 1x2 Splitter (3端口)
ports:
  - name: o1, function: input
  - name: o2, function: output_bar
  - name: o3, function: output_cross
```

---

## 3. 几何参数 (Geometry Parameters)

### 3.1 波导参数
| 参数 | 符号 | 单位 | 典型位置 | 示例值 |
|-----|------|------|---------|-------|
| 波导宽度 | w, width | nm | Fabrication | 450-500 nm |
| 波导高度 | h, height | nm | Fabrication | 220 nm (SOI) |
| 脊高度 | slab_height | nm | Fabrication | 90 nm |
| 侧壁角度 | sidewall_angle | ° | Fabrication | 82-90° |

### 3.2 耦合器参数
| 参数 | 符号 | 单位 | 典型位置 | 示例值 |
|-----|------|------|---------|-------|
| 耦合间隙 | gap | nm | Methods/Fig | 100-300 nm |
| 耦合长度 | coupling_length | μm | Methods | 5-20 μm |
| 耦合系数 | κ, kappa | - | Results | 0.1-0.5 |

### 3.3 谐振器参数
| 参数 | 符号 | 单位 | 典型位置 | 示例值 |
|-----|------|------|---------|-------|
| 环半径 | radius, R | μm | Methods/Fig | 5-50 μm |
| 环周长 | perimeter | μm | 计算 | 2πR |
| 弯曲类型 | bend_type | - | Methods | euler/circular |

### 3.4 MZI参数
| 参数 | 符号 | 单位 | 典型位置 | 示例值 |
|-----|------|------|---------|-------|
| 臂长差 | delta_L | μm | Methods | 50-200 μm |
| 分束器类型 | splitter_type | - | Methods | MMI/DC/Y-branch |
| 臂长 | arm_length | μm | Methods | 100-500 μm |

---

## 4. 性能指标 (Performance Specs)

### 4.1 通用指标
| 参数 | 符号 | 单位 | 典型位置 | 理想值 |
|-----|------|------|---------|-------|
| 插入损耗 | IL | dB | Results Fig | < 1 dB |
| 消光比 | ER | dB | Results | > 20 dB |
| 3dB带宽 | BW_3dB | nm/GHz | Results | 依应用 |
| 偏振相关损耗 | PDL | dB | Results | < 0.5 dB |

### 4.2 谐振器特有
| 参数 | 符号 | 单位 | 典型位置 |
|-----|------|------|---------|
| 自由光谱范围 | FSR | nm | Results Fig |
| Q因子 | Q | - | Results |
| Finesse | F | - | Results |
| 谐振波长 | λ_res | nm | Results |

### 4.3 调制器特有
| 参数 | 符号 | 单位 | 典型位置 |
|-----|------|------|---------|
| Vπ·L | VπL | V·cm | Results |
| 调制带宽 | BW | GHz | Results |
| 上升时间 | t_rise | ps | Results |

---

## 5. S参数数据 (S-Parameters)

### 5.1 数据获取方法

**方法A: 从论文图表提取**
1. 使用 WebPlotDigitizer (https://automeris.io/WebPlotDigitizer)
2. 导入论文中的传输谱图
3. 数字化曲线数据点
4. 导出为CSV格式

**方法B: 从仿真获取**
1. 使用 Tidy3D/Lumerical FDTD 仿真
2. 基于论文几何参数建模
3. 提取S参数
4. 导出保存

### 5.2 .npz 文件格式

```python
import numpy as np

# 波长数组 (单位: μm)
wavelengths = np.linspace(1.5, 1.6, 101)  # 1500-1600nm, 101点

# S参数 (复数数组，长度与wavelengths相同)
# 端口命名: ("o1", "o2") 表示从o1入射到o2出射
sparams = {
    ("o1", "o1"): reflection_at_input,      # 反射
    ("o1", "o2"): transmission_through,      # 透射(through)
    ("o1", "o3"): transmission_add,          # add端口
    ("o1", "o4"): transmission_drop,         # drop端口
    # ... 其他端口组合
}

# 保存为npz
np.savez(
    "add_drop_ring_radius10um.npz",
    wavelengths=wavelengths,
    **{f"{p[0]}@{p[1]}": v for p, v in sparams.items()}
)
```

### 5.3 从图表提取示例

论文中的透射谱图通常显示:
- X轴: 波长 (nm) 或频率 (THz)
- Y轴: 透射率 (dB) 或归一化功率

提取步骤:
```
1. 截图论文Fig (如 Transmission spectrum)
2. 导入 WebPlotDigitizer
3. 设置坐标轴 (标定X/Y范围)
4. 自动/手动提取曲线数据点
5. 导出为 wavelength, transmission_dB
6. 转换: |S21|² = 10^(transmission_dB/10)
```

---

## 6. 材料与制造 (Material & Fabrication)

| 字段 | 说明 | 典型位置 | 示例值 |
|-----|------|---------|-------|
| 核心材料 | waveguide core | Fabrication | Si, Si3N4, LN |
| 包层材料 | cladding | Fabrication | SiO2, Air |
| 衬底 | substrate | Fabrication | BOX (buried oxide) |
| 平台 | foundry/process | Methods | IME, AMF, IMEC |
| 刻蚀深度 | etch depth | Fabrication | 全刻蚀/部分刻蚀 |

### 材料折射率参考:
```yaml
silicon:
  n_core: 3.48  # @ 1550nm
  n_clad: 1.44  # SiO2
  
silicon_nitride:  
  n_core: 2.0   # @ 1550nm
  n_clad: 1.44  # SiO2
  
lithium_niobate:
  n_o: 2.21     # ordinary
  n_e: 2.14     # extraordinary @ 1550nm
```

---

## 7. 填写示例

以下以 "Low-power microelectromechanically tunable silicon photonic ring resonator add–drop filter" 为例：

```yaml
# 基础信息
component_name: mems_tunable_add_drop_ring
chinese_name: MEMS可调环形add-drop滤波器
description: 低功耗MEMS可调谐硅光环形谐振器滤波器
wavelength_band: C-band
doi: 10.1364/OL.40.003556
source: Optics Letters

# 端口定义
ports:
  - {name: o1, function: input}
  - {name: o2, function: through}
  - {name: o3, function: add}
  - {name: o4, function: drop}

# 几何参数 (需从论文中提取)
geometry:
  waveguide_width: 500  # nm
  waveguide_height: 220  # nm
  ring_radius: 10  # μm (需确认)
  coupling_gap: 200  # nm (需确认)
  
# 性能指标 (从Results获取)
performance:
  insertion_loss: TBD  # dB
  extinction_ratio: TBD  # dB
  fsr: TBD  # nm
  q_factor: TBD
  tuning_range: TBD  # nm
  power_consumption: TBD  # mW

# S参数
s_parameters:
  source: "需从Fig.X数字化提取或FDTD仿真"
  file: "mems_tunable_add_drop_ring.npz"

# 材料信息
material:
  core: silicon
  cladding: SiO2
  substrate: SOI
```

---

## 8. 组件文件模板

提取完成后，创建 `DesignLibrary/component_name.py`:

```python
"""
Name: component_name
Description: 组件描述
ports: ['o1', 'o2', 'o3', 'o4']
NodeLabels:
  - label1
  - label2  
Bandwidth: C-band
Args:
  - param1: 参数1说明 (默认值)
  - param2: 参数2说明 (默认值)
Reference: DOI或论文链接
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
from functools import partial
from ..Photon.utils import model_from_npz, get_file_path

@gf.cell
def component_name(
    param1: float = default1,
    param2: float = default2,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    组件描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
        cross_section: 波导截面
        
    Returns:
        gf.Component: GDS组件
    """
    c = gf.Component()
    
    # GDS几何定义
    # ... (使用gdsfactory API构建)
    
    # 添加端口
    c.add_port(name="o1", center=(0, 0), width=0.5, orientation=180, layer=(1, 0))
    c.add_port(name="o2", center=(length, 0), width=0.5, orientation=0, layer=(1, 0))
    
    return c


def get_model() -> dict:
    """返回SAX仿真模型"""
    # 方式1: 使用预计算的FDTD数据
    model = model_from_npz(get_file_path("component_name/component_name.npz"))
    return {"component_name": model}
    
    # 方式2: 解析模型 (如果有公式)
    # def analytical_model(wl=1.55, param1=default1):
    #     ...计算S矩阵...
    #     return sdict
    # return {"component_name": analytical_model}
```

---

## 9. 论文关键词搜索指南

根据器件类型使用以下关键词组合搜索：

| 器件类型 | 搜索关键词 |
|---------|-----------|
| 环形谐振器 | `"silicon ring resonator" fabrication measurement` |
| Add-drop滤波器 | `"add-drop filter" "silicon photonics" S-parameters` |
| MZI调制器 | `"Mach-Zehnder modulator" "silicon" Vpi measurement` |
| 光栅耦合器 | `"grating coupler" "coupling efficiency" "fiber-chip"` |
| MMI分束器 | `"multimode interference" "1x2 splitter" "insertion loss"` |
| 定向耦合器 | `"directional coupler" "coupling ratio" fabrication` |
| 边缘耦合器 | `"edge coupler" "spot size converter" "mode converter"` |
| 偏振分束器 | `"polarization splitter" "PBS" "silicon photonics"` |

---

## 10. 检查清单

添加新组件前，确认已收集：

- [ ] 组件名称 (英文小写下划线)
- [ ] 功能描述 (1-2句)
- [ ] 端口数量和命名
- [ ] 波导尺寸 (width, height)
- [ ] 关键几何参数 (radius, gap, length等)
- [ ] 至少1项性能指标 (IL, ER, FSR等)
- [ ] S参数数据来源 (图表提取或仿真)
- [ ] 参考文献 (DOI或链接)
- [ ] 材料/平台信息
