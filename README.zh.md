# PhIDO

PhIDO（Photonics Intelligent Design and Optimization）是一个基于 Web（Streamlit）的光子集成电路智能设计与优化平台，使用大模型（LLM）辅助从需求提取、器件选择、原理图/DSL 生成、GDS版图输出到设计输出校验（DRC）校验的端到端流程。


> **📚 Getting Started**: 针对更细节的指导请查看 [GETTING_STARTED.md](GETTING_STARTED.md) 该综合指南包含实用示例、故障排除提示以及两种工作流程模式的详细说明。

---


## 🏗️ Project Structure

```
PhIDO/
├── PhotonicsAI/                    # Main application package
│   ├── Photon/                     # Core application modules
│   │   ├── webapp.py              # Streamlit web application (main entry point)
│   │   ├── llm_api.py             # LLM API integrations and model configurations
│   │   ├── utils.py               # Utility functions for circuit processing
│   │   ├── prompts.yaml           # LLM prompts and system instructions
│   │   ├── templates.yaml         # Circuit templates and configurations
│   │   ├── DemoPDK.py             # Demo Process Design Kit
│   │   ├── drc/                   # Design Rule Checking module
│   │   │   ├── drc.py             # DRC execution engine
│   │   │   └── drc_script.drc     # KLayout DRC script
│   │   └── CIRCUIT_wdd0.yaml      # Example circuit configuration
│   ├── KnowledgeBase/             # Design knowledge and components
│   │   ├── DesignLibrary/         # Photonic component library
│   │   │   ├── mzi_1x1_heater_tin_cband.py  # MZI with TiN heaters
│   │   │   ├── mzi_2x2_heater_tin_cband.py  # 2x2 MZI with heaters
│   │   │   └── ...                # Other photonic components
│   │   └── FDTD/                  # Finite Difference Time Domain simulation data
│   └── config.py                  # Application configuration
├── GETTING_STARTED.md             # Comprehensive tutorial and user guide
├── GETTING_STARTED_EXAMPLE_OUTPUTS/  # Example outputs for tutorial prompts
│   ├── Level 1 Prompt/            # Single component example outputs
│   ├── Level 2 Prompt/            # Two components example outputs
│   ├── Level 3 Prompt/            # Multiple components example outputs
│   └── Level 4 Prompt/            # Complex system example outputs
├── requirements.txt               # Complete environment dependencies
├── Makefile                      # Build and run commands
├── Testbench.xlsx                # Contains 102 testbench prompts
└── README.md                     # This file
```
## 🚀 安装
### 前提要求
1. **系统依赖**（Ubuntu / Debian）
：
```bash
sudo apt-get update
sudo apt-get install -y graphviz libgraphviz-dev pkg-config klayout \
  build-essential python3-dev swig
```

或者在Windows系统上，请确保安装了Ubuntu子系统（WSL）并执行上述命令，或手动安装相应依赖。


2. **环境与安装**（建议 Python 3.12）

建议使用 Python 3.12 虚拟环境（如 venv 或 conda），并安装仓库内 requirements.txt 所列依赖。

推荐步骤：

```bash
# 创建并激活虚拟环境（如 myvenv）
python3 -m venv ~/myvenv
source ~/myvenv/bin/activate

# 升级 pip 并安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

如需开发/调试 Streamlit Web 应用，可用如下命令启动：

```bash
python -m streamlit run PhotonicsAI/Photon/webapp.py --server.address 127.0.0.1 --server.port 8501
```

如遇依赖冲突或导入错误，请确保 requirements.txt 与 pyproject.toml 的 gdsfactory/kfactory 版本一致（推荐 gdsfactory==8.18.1, kfactory==0.21.7）


### 在根目录下创建 Log 文件
创建一个`log`文件夹在`PhIDO-Release/PhotonicsAI/`目录下


## 配置（环境变量）
 创建一个 `.env` 文件在项目根目录，填写你的 API 密钥：
按当前需求，仅需配置智谱：

```bash
ZHIPU_API_KEY='your-zhipu-api-key'
```

如果后续需要其它模型，可再补充相应 Key。



## 🤖 后续可添加模型
PhIDO 通过`llm_api.py` 支持多种大模型, 大模型的选择在`webapp.py` 初始被定义 `webapp.py` ，用户可以选择在每一步都使用不同的大模型，提供商的 API Key 需在环境变量中配置：


### 智谱 (Zhipu / GLM) Models
- **glm-4** - 最新的 GLM-4 文本/对话模型，适用于一般生成与推理任务 `glm-4`
- **chatglm_turbo** - 更快的对话模型，延迟更低 `chatglm_turbo`
- **Environment Variable**: `ZHIPU_API_KEY` (兼容 `ZHIPUAI_API_KEY`)

**注意** `ZHIPU_API_KEY` **必须设置因为其他模型依赖于智谱进行实体提取结果的格式化。**







## 🏃‍♂️启动
在开始之前：
```bash
export PYTHONPATH='.'
python -m streamlit run PhotonicsAI/Photon/webapp.py --server.address 127.0.0.1 --server.port 8501
# 或使用 Makefile
make run
```

浏览器访问 `http://localhost:8501`。远程部署可使用 `--server.address 0.0.0.0` 并开放/转发端口。

## 常见问题

- pygraphviz 构建失败：先安装上面的系统依赖，再重试 `pip install -r requirements.txt`。
- `ModuleNotFoundError: No module named 'kfactory.routing.generic'`：

```bash
pip install kfactory==0.21.7
```

- 导入问题：确保执行过 `export PYTHONPATH='.'`。
- 日志：如需记录，创建项目下 `log/` 目录。



更多例子见 `GETTING_STARTED.md` 与 `GETTING_STARTED_EXAMPLE_OUTPUTS/`。

### 基于模板的设计
1. **启动应用** 并选择 “Step-by-Step Workflow（逐步执行模式）”
2. **选择模板**（例如 “MZI with TiN heaters”）
3. **自定义参数**（长度、宽度、加热器规格等）
4. **根据模板生成电路 DSL**
5. **生成版图并运行仿真**
6. **执行 DRC 校验**，确保满足制造要求

### 自定义电路设计
1. **启动应用** 并选择 “Automatic Workflow（自动工作流）”
2. **输入电路描述**（例如 “Design a 2x2 Mach-Zehnder interferometer with heaters”）
3. **按照引导流程完成每一步**
4. **检查生成的原理图与版图**
5. **查看 DRC 结果**，确认是否存在违规
6. **导出结果**，用于流片或进一步分析

## 🔧 开发

### 项目结构详情

- **`webapp.py`**：Streamlit 主程序，包含 UI 组件与工作流逻辑
- **`llm_api.py`**：支持多家模型提供商的 LLM 接口层
- **`utils.py`**：电路处理、DOT 图生成与数据处理的工具函数
- **`prompts.yaml`**：不同 LLM 任务与工作流步骤的结构化提示词
- **`templates.yaml`**：电路模板与组件配置
- **`drc/`**：与 KLayout 集成的 DRC 模块
- **`KnowledgeBase/`**：光子组件库与仿真数据

### 新增组件

若要添加新的光子器件：

1. 在 `KnowledgeBase/DesignLibrary/` 中创建组件文件
2. 定义组件几何结构与参数
3. 添加用于仿真的 S 参数模型
4. 在 `templates.yaml` 中更新对应模板
5. 在 `prompts.yaml` 中补充相关提示词

### 扩展 DRC 规则

若要添加新的 DRC 规则：

1. 在 `drc/drc_script.drc` 中编写规则定义
2. 更新图层定义与约束条件
3. 使用示例版图进行测试
4. 在 `webapp.py` 中更新 DRC 报告逻辑

### 新增 LLM 模型

若要支持新的 LLM 模型：

1. 在 `llm_api.py` 中添加模型配置
2. 在 `webapp.py` 中更新模型选择逻辑
3. 添加对应的环境变量说明
4. 使用合适的提示词进行验证

## 🐛 故障排查

### 常见问题

1. **GDS 图层编号报错**：PhIDO 会自动处理图层编号过大的情况。
2. **DRC 失败**：请检查 KLayout 是否正确安装，以及 DRC 脚本配置是否完整。
3. **LLM API 报错**：确认 API Key 是否正确配置，并检查模型服务可用性。
4. **组件导入错误**：确保所有依赖均已正确安装。

### 环境设置
如果 `pygraphviz` 构建失败：
```bash
sudo apt-get update
sudo apt-get install -y build-essential
sudo apt-get install -y python3-dev
sudo apt-get install -y swig
```
然后重新执行 `pip install -r requirements.txt`。

若运行 PhIDO 时出现导入问题：
```bash
export PYTHONPATH='.'
```

### 启动错误

若出现以下错误：
```bash
ModuleNotFoundError: No module named 'kfactory.routing.generic'
```
执行：
```bash
pip install kfactory==0.21.1
```
忽略 pip 与 gdsfactory 8.8.5 的依赖冲突提示。

### 日志错误

若出现日志相关报错，请在 `PhIDO-Release/PhotonicsAI` 下创建 `log` 文件夹。

## 🤝 贡献
1. Fork 本仓库
2. 创建功能分支
3. 实现改动
4. 如有必要补充测试
5. 发起 Pull Request

## 🙏 致谢

- 使用 Streamlit 构建 Web 界面
- 集成多家 LLM 提供商
- 借助 GDSFactory 生成光子版图
- 使用 SAX 进行电路仿真
- 使用 KLayout 完成 DRC 校验
- 通过模板快速构建原型

