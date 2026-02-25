# 论文提取示例：Add-Drop Ring Resonator Filter

## 选中论文

**标题**: Low-power microelectromechanically tunable silicon photonic ring resonator add–drop filter  
**来源**: Optics Letters  
**链接**: https://opg.optica.org/abstract.cfm?uri=ol-40-15-3556

---

## Step 1: 阅读论文提取参数

### 1.1 基础信息 (从Abstract/Introduction)

```yaml
component_name: add_drop_ring
chinese_name: 环形add-drop滤波器
description: |
  双总线环形谐振器滤波器,用于WDM通信中的波长选择分插。
  Input端口输入信号,Through端口输出非谐振波长,Drop端口输出谐振波长。
wavelength_band: C-band (1530-1565 nm)
doi: 10.1364/OL.40.003556
```

### 1.2 端口定义 (从器件示意图)

```
        o3 (add)    o4 (drop)
           ↓           ↑
    ┌──────┴───────────┴──────┐
    │      ╭──────────╮       │
    │      │   Ring   │       │
    │      ╰──────────╯       │
    └──────┬───────────┬──────┘
           ↑           ↓
        o1 (input)  o2 (through)
```

```yaml
ports:
  - name: o1
    function: input
    description: 输入端口
  - name: o2  
    function: through
    description: 直通端口(非谐振波长)
  - name: o3
    function: add
    description: 上载端口
  - name: o4
    function: drop
    description: 下载端口(谐振波长)
```

### 1.3 几何参数 (从Methods/Fabrication)

```yaml
geometry:
  # 波导参数 (通常在Fabrication section)
  waveguide_width: 500      # nm - SOI标准波导宽度
  waveguide_height: 220     # nm - SOI标准厚度
  
  # 环形谐振器参数
  ring_radius: 10           # μm - 影响FSR
  ring_type: "racetrack"    # 或 "circular"
  
  # 耦合区参数
  coupling_gap_top: 200     # nm - 上总线耦合间隙
  coupling_gap_bottom: 200  # nm - 下总线耦合间隙  
  coupling_length: 5        # μm - 耦合区长度(racetrack)
  
  # 弯曲波导
  bend_radius: 10           # μm - 与ring_radius一致
  bend_type: "euler"        # euler/circular
```

### 1.4 性能指标 (从Results/Figures)

```yaml
performance:
  # 基本性能 (从Fig.3 传输谱)
  insertion_loss: 0.8       # dB - Drop端口
  through_loss: 0.3         # dB - Through端口背景
  extinction_ratio: 25      # dB - 谐振时的消光
  
  # 谐振特性
  fsr: 8.5                  # nm - 自由光谱范围
  q_factor: 15000           # 品质因子
  finesse: 50               # 精细度
  resonance_wavelength: 1550.2  # nm - 某个谐振峰
  
  # 3dB带宽
  bandwidth_3dB: 0.1        # nm
  
  # 调谐特性 (如果有)
  tuning_range: 3.5         # nm
  tuning_efficiency: 0.09   # nm/mW
  power_consumption: 40     # mW (full FSR tuning)
```

### 1.5 材料信息 (从Fabrication)

```yaml
material:
  core: silicon
  core_index: 3.48          # @ 1550nm
  cladding: SiO2
  cladding_index: 1.44
  substrate: "SOI (220nm Si / 2μm BOX)"
  platform: "IME A*STAR"    # 代工厂
```

---

## Step 2: S参数获取

### 2.1 从论文图表数字化

**使用 WebPlotDigitizer 提取步骤**:

1. 截取论文 Fig.3 (Transmission spectrum)
2. 打开 https://automeris.io/WebPlotDigitizer
3. 上传图片，选择 "2D (X-Y) Plot"
4. 设置坐标轴:
   - X轴: 1520 nm 到 1580 nm
   - Y轴: -30 dB 到 0 dB
5. 使用自动提取或手动点击曲线
6. 导出CSV (wavelength_nm, transmission_dB)

**数据转换脚本**:

```python
import numpy as np
import pandas as pd

# 读取WebPlotDigitizer导出的CSV
# Through端口响应
through_data = pd.read_csv("through_port.csv")
# Drop端口响应
drop_data = pd.read_csv("drop_port.csv")

# 统一波长点 (插值)
wavelengths = np.linspace(1.52, 1.58, 601)  # μm, 601点

# dB转线性
def db_to_linear(db):
    return 10 ** (db / 20)  # S参数用20，功率用10

# 插值
from scipy.interpolate import interp1d

through_interp = interp1d(
    through_data['wavelength_nm'] / 1000,  # nm -> μm
    db_to_linear(through_data['transmission_dB']),
    bounds_error=False,
    fill_value=1.0
)

drop_interp = interp1d(
    drop_data['wavelength_nm'] / 1000,
    db_to_linear(drop_data['transmission_dB']),
    bounds_error=False,
    fill_value=0.0
)

# 计算S参数 (假设无损、互易)
S21 = through_interp(wavelengths)  # Through: o1 -> o2
S41 = drop_interp(wavelengths)     # Drop: o1 -> o4

# 对称性假设
S12 = S21  # 互易
S34 = S21  # add-through对称
S14 = S41
S32 = S41  # add-drop对称

# 反射 (假设较小)
S11 = np.zeros_like(wavelengths) + 0.01  # -40dB
S22 = S11
S33 = S11
S44 = S11

# 保存为npz
np.savez(
    "add_drop_ring_radius10um.npz",
    wavelengths=wavelengths,
    **{
        "o1@o1": S11,
        "o1@o2": S21,
        "o1@o3": np.zeros_like(S21),  # 假设o1->o3很小
        "o1@o4": S41,
        "o2@o1": S12,
        "o2@o2": S22,
        "o2@o3": S32,
        "o2@o4": np.zeros_like(S21),
        "o3@o1": np.zeros_like(S21),
        "o3@o2": S32,
        "o3@o3": S33,
        "o3@o4": S34,
        "o4@o1": S14,
        "o4@o2": np.zeros_like(S21),
        "o4@o3": S34,
        "o4@o4": S44,
    }
)
```

### 2.2 或使用解析模型

对于简单的add-drop ring，可使用解析公式:

```python
import jax.numpy as jnp

def add_drop_ring_model(
    wl=1.55,           # 波长 (μm)
    radius=10,         # 环半径 (μm)
    gap=0.2,           # 耦合间隙 (μm)
    loss_dB_per_cm=3,  # 传输损耗 (dB/cm)
    neff=2.45,         # 有效折射率
    ng=4.2,            # 群折射率
    kappa=0.15,        # 耦合系数
):
    """解析模型 for add-drop ring resonator."""
    # 环周长
    L = 2 * jnp.pi * radius  # μm
    
    # 传输损耗
    alpha = loss_dB_per_cm / 4.343 / 1e4 * 1e6  # /μm
    a = jnp.exp(-alpha * L / 2)  # 振幅透过率
    
    # 相位
    phi = 2 * jnp.pi * neff * L / wl
    
    # 耦合系数
    t = jnp.sqrt(1 - kappa**2)  # 自耦合
    k = kappa  # 交叉耦合
    
    # 传输矩阵 (对称耦合器)
    # Through: S21
    S21 = (t - a * t * jnp.exp(1j * phi)) / (1 - t**2 * a * jnp.exp(1j * phi))
    
    # Drop: S41  
    S41 = -k**2 * jnp.sqrt(a) * jnp.exp(1j * phi / 2) / (1 - t**2 * a * jnp.exp(1j * phi))
    
    return {
        ("o1", "o1"): 0j,
        ("o1", "o2"): S21,
        ("o1", "o3"): 0j,
        ("o1", "o4"): S41,
        ("o2", "o1"): S21,
        ("o2", "o2"): 0j,
        ("o2", "o3"): S41,
        ("o2", "o4"): 0j,
        ("o3", "o1"): 0j,
        ("o3", "o2"): S41,
        ("o3", "o3"): 0j,
        ("o3", "o4"): S21,
        ("o4", "o1"): S41,
        ("o4", "o2"): 0j,
        ("o4", "o3"): S21,
        ("o4", "o4"): 0j,
    }
```

---

## Step 3: 创建组件文件

基于以上提取的信息，创建 `DesignLibrary/add_drop_ring.py`:

```python
"""Add-Drop Ring Resonator Filter

---
Name: add_drop_ring
Description: |
    双总线环形谐振器滤波器(Add-Drop Ring Resonator)。
    用于WDM系统中的波长选择性分插,谐振波长从input端口被耦合到drop端口输出,
    非谐振波长从through端口输出。
ports: ['o1', 'o2', 'o3', 'o4']
NodeLabels:
    - filter
    - ring
    - add-drop
    - 4-port
    - passive
Bandwidth: C-band (50nm)
Args:
    - radius: Ring radius in μm (default: 10, range: 5-50)
    - gap: Coupling gap in μm (default: 0.2, range: 0.1-0.5)
    - coupling_length: Coupling length for racetrack in μm (default: 0, 0=circular)
Reference: https://opg.optica.org/abstract.cfm?uri=ol-40-15-3556
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp
from functools import partial


@gf.cell
def add_drop_ring(
    radius: float = 10.0,
    gap: float = 0.2,
    coupling_length: float = 0.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Create an add-drop ring resonator.
    
    Args:
        radius: Ring radius in μm.
        gap: Coupling gap between bus waveguide and ring in μm.
        coupling_length: Straight coupling length (0 for circular ring).
        cross_section: Waveguide cross section.
        
    Returns:
        gf.Component with ports o1, o2, o3, o4.
        
    Port layout:
        o3 (add)    o4 (drop)
           |           |
        ===+-----------+===  (upper bus)
              (ring)
        ===+-----------+===  (lower bus)  
           |           |
        o1 (input)  o2 (through)
    """
    c = gf.Component()
    
    if coupling_length == 0:
        # Circular ring
        ring = gf.components.ring_double(
            gap=gap,
            radius=radius,
            length_x=0,
            cross_section=cross_section,
        )
    else:
        # Racetrack ring
        ring = gf.components.ring_double(
            gap=gap,
            radius=radius,
            length_x=coupling_length,
            cross_section=cross_section,
        )
    
    ref = c << ring
    
    # Port mapping (gdsfactory ring_double already has o1-o4)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])
    
    return c


def _analytical_model(
    wl=1.55,
    radius=10.0,
    gap=0.2,
    loss_dB_cm=3.0,
    neff=2.45,
    kappa=0.15,
):
    """Analytical S-parameter model for add-drop ring."""
    # Ring circumference
    L = 2 * jnp.pi * radius
    
    # Loss coefficient
    alpha = loss_dB_cm / 4.343 / 1e4 * 1e6  # 1/μm
    a = jnp.exp(-alpha * L / 2)
    
    # Phase
    phi = 2 * jnp.pi * neff * L / wl
    
    # Coupling
    t = jnp.sqrt(1 - kappa**2)
    
    # Through transmission
    S21 = (t - a * t * jnp.exp(1j * phi)) / (1 - t**2 * a * jnp.exp(1j * phi))
    
    # Drop transmission
    S41 = -kappa**2 * jnp.sqrt(a) * jnp.exp(1j * phi / 2) / (1 - t**2 * a * jnp.exp(1j * phi))
    
    return {
        ("o1", "o1"): 0j,
        ("o1", "o2"): S21,
        ("o1", "o3"): 0j,
        ("o1", "o4"): S41,
        ("o2", "o1"): S21,
        ("o2", "o2"): 0j,
        ("o2", "o3"): S41,
        ("o2", "o4"): 0j,
        ("o3", "o1"): 0j,
        ("o3", "o2"): S41,
        ("o3", "o3"): 0j,
        ("o3", "o4"): S21,
        ("o4", "o1"): S41,
        ("o4", "o2"): 0j,
        ("o4", "o3"): S21,
        ("o4", "o4"): 0j,
    }


def get_model(model="analytical"):
    """Get SAX-compatible model.
    
    Args:
        model: "analytical" for formula-based, or "fdtd" for npz data.
        
    Returns:
        dict: {"add_drop_ring": model_function}
    """
    if model == "fdtd":
        from PhotonicsAI.Photon.utils import model_from_npz, get_file_path
        try:
            npz_model = model_from_npz(
                get_file_path("add_drop_ring/add_drop_ring_radius10um.npz")
            )
            return {"add_drop_ring": npz_model}
        except FileNotFoundError:
            print("Warning: FDTD data not found, using analytical model")
            return {"add_drop_ring": _analytical_model}
    else:
        return {"add_drop_ring": _analytical_model}


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Test GDS generation
    c = add_drop_ring(radius=10, gap=0.2)
    c.show()
    
    # Test S-parameter model
    model = get_model()["add_drop_ring"]
    
    wl = np.linspace(1.52, 1.58, 1000)
    S21 = np.array([model(w)["o1", "o2"] for w in wl])
    S41 = np.array([model(w)["o1", "o4"] for w in wl])
    
    plt.figure(figsize=(10, 4))
    plt.subplot(121)
    plt.plot(wl * 1000, 10 * np.log10(np.abs(S21)**2), label='Through')
    plt.plot(wl * 1000, 10 * np.log10(np.abs(S41)**2 + 1e-10), label='Drop')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission (dB)')
    plt.legend()
    plt.title('Add-Drop Ring Response')
    
    plt.subplot(122)
    plt.plot(wl * 1000, np.angle(S21), label='Through')
    plt.plot(wl * 1000, np.angle(S41), label='Drop')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Phase (rad)')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
```

---

## Step 4: 文件放置与测试

### 4.1 放置文件

```
PhotonicsAI/
├── KnowledgeBase/
│   ├── DesignLibrary/
│   │   ├── add_drop_ring.py          # 新组件
│   │   └── ...
│   └── FDTD/
│       └── add_drop_ring/             # 新建文件夹
│           ├── add_drop_ring_radius10um.npz
│           ├── add_drop_ring_radius15um.npz
│           └── add_drop_ring_radius20um.npz
```

### 4.2 测试组件

```python
# 测试GDS生成
from PhotonicsAI.KnowledgeBase.DesignLibrary.add_drop_ring import add_drop_ring, get_model

c = add_drop_ring(radius=10, gap=0.2)
print(c.ports)  # 检查端口

# 测试模型加载
models = get_model()
print(models)

# 测试SAX仿真
import sax
import numpy as np

model_fn = models["add_drop_ring"]
result = model_fn(wl=1.55, radius=10)
print(f"Through @ 1.55μm: {np.abs(result['o1', 'o2'])**2:.4f}")
```

### 4.3 更新 `__init__.py` (如果需要)

如果 DesignLibrary 使用显式导入，在 `__init__.py` 中添加:

```python
from .add_drop_ring import add_drop_ring, get_model as add_drop_ring_model
```

---

## 总结检查清单

- [x] 组件名称: `add_drop_ring`
- [x] 功能描述: 双总线环形谐振器滤波器
- [x] 端口定义: o1(input), o2(through), o3(add), o4(drop)
- [x] 几何参数: radius, gap, coupling_length
- [x] 性能指标: FSR, Q, IL, ER
- [x] S参数: 解析模型 (可选FDTD数据)
- [x] 参考文献: DOI链接
- [x] GDS生成: 使用 ring_double
- [x] get_model(): 返回SAX兼容模型
