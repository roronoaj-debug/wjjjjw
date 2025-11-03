# 环境与依赖安装

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

如遇依赖冲突或导入错误，请确保 requirements.txt 与 pyproject.toml 的 gdsfactory/kfactory 版本一致（推荐 gdsfactory==8.18.1, kfactory==0.21.7）。
# PhIDO: AI-Powered Photonic Circuit Designer

PhIDO (Photonics Intelligent Design and Optimization) is an intelligent web application that automates the design of photonic integrated circuits using Large Language Models (LLMs). The application provides both automatic guided workflows and step-by-step execution modes for circuit design, from specification to layout generation and Design Rule Checking (DRC).

[Paper preprint](https://arxiv.org/abs/2508.14123)

> **📚 Getting Started**: For hands-on tutorials and detailed step-by-step instructions on using PhIDO, see [GETTING_STARTED.md](GETTING_STARTED.md). This comprehensive guide includes practical examples, troubleshooting tips, and detailed explanations of both workflow modes.

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

## 🚀 Installation

### Prerequisites

1. **System Dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install graphviz libgraphviz-dev pkg-config klayout
   sudo apt-get install -y build-essential python3-dev swig
   ```

2. **Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  
   ```

### Install Dependencies

```bash
pip install -r requirements.txt
```
After this is done, do:
```bash
pip install kfactory==0.21.1
```
Ignore the pip dependency resolver conflict with gdsfactory 8.8.5.

### Setup Log Directory
Create a `log` folder under `PhIDO-Release/PhotonicsAI/`

## ⚙️ Configuration

Create a `.env` file in the project root with your API keys:

```bash
# Required for OpenAI models (GPT-4, GPT-4o, O1)
OPENAI_API_KEY='your-openai-api-key'

# Required for Anthropic Claude models
ANTHROPIC_API_KEY='your-anthropic-api-key'

# Required for Google Gemini models
GOOGLEGENAI_API_KEY='your-google-api-key'

# Required for DeepSeek-R1
DEEPSEEK_API_KEY='your-deepseek-api-key'

# Required for models hosted on NVIDIA NIM
NVIDIA_API_KEY='your-nvidia-nim-api-key'

# Required for 智谱 (Zhipu) models
# Prefer ZHIPU_API_KEY; ZHIPUAI_API_KEY is also accepted for compatibility
ZHIPU_API_KEY='your-zhipu-api-key'
# ZHIPUAI_API_KEY='your-zhipu-api-key'
```

## 🤖 Supported LLM Models

PhIDO supports multiple LLM providers through the `llm_api.py` module, LLM selection is configured at the beginning of `webapp.py` script. The user may run different LLMs at each step of PhIDO, provided that the models' API keys are configured within the environmental variables:

### OpenAI Models
- **GPT-4o** - General purpose reasoning `gpt-4o`
- **o1** - (Default) Specialized for reasoning tasks `o1`
- **o3-mini** - Faster reasoning model `o3-mini`
- **Environment Variable**: `OPENAI_API_KEY`

### Anthropic Models
- **Claude-3-7-Sonnet-20250219** - Balanced performance and speed `claude-3-7-sonnet-latest`
- **Claude-4.0-Opus** - Advanced reasoning capabilities `claude-opus-4-20250514`
- **Environment Variable**: `ANTHROPIC_API_KEY`

### Google Models
- **Gemini-2.5-Pro** - Advanced reasoning and code generation `gemini-2.5-pro`
- **Gemini-1.5-Pro** - General purpose reasoning `gemini-1.5-pro`
- **Gemini-1.5-Flash** - Fast response model `gemini-1.5-flash`
- **Gemini-2.0-Flash** - Latest flash model `gemini-2.0-flash`
- **Environment Variable**: `GOOGLEGENAI_API_KEY`

### NVIDIA Models (via NVIDIA NIM API)
- **nvidia/llama-3.1-nemotron-ultra-253b-v1** - Large-scale reasoning `nvidia/llama-3.1-nemotron-ultra-253b-v1`
- **nvidia/nemotron-4-340b-instruct** - Alternative Nemotron model (Deprecated on NIM) `nvidia/nemotron-4-340b-instruct`
- **Environment Variable**: `NVIDIA_API_KEY` 

### DeepSeek Models
- **DeepSeek-Reasoner** - Specialized reasoning model `deepseek-reasoner`
- **Environment Variable**: `DEEPSEEK_API_KEY` 

### 智谱 (Zhipu / GLM) Models
- **glm-4** - 最新的 GLM-4 文本/对话模型，适用于一般生成与推理任务 `glm-4`
- **chatglm_turbo** - 更快的对话模型，延迟更低 `chatglm_turbo`
- **Environment Variable**: `ZHIPU_API_KEY` (兼容 `ZHIPUAI_API_KEY`)

**Note that** `OPENAI_API_KEY` **must be set in addition to any other model api key as PhIDO uses GPT models for formatting entity extraction results via pydantic.**
Other models not listed above but offered by API providers above may also work but have not been tested. 

## 🔄 Workflow Modes

PhIDO provides two distinct workflow modes to accommodate different user preferences and use cases:

### 1. Automatic Workflow (Guided Mode)
A fully automated, step-by-step process that guides users through the entire circuit design pipeline.

**Workflow Steps:**
1. **Entity Extraction**: Analyzes user input to extract circuit requirements, components, and specifications
2. **Component Selection**: Matches extracted entities with available photonic components from the knowledge base
3. **Schematic Generation**: Creates a circuit DSL (Domain Specific Language) representation with component connections
4. **Layout & Simulation**: Generates GDS layout files and performs circuit simulations
5. **Design Rule Checking (DRC)**: Validates layout against manufacturing design rules using KLayout

**Features:**
- Automatic progression between steps
- Real-time feedback and status updates
- Error handling and recovery
- Integrated validation at each stage
- Template-based circuit generation
- DRC integration for manufacturing readiness

### 2. Step-by-Step Workflow (Independent Mode)
Allows users to execute individual workflow steps with custom inputs and manual control.

**Available Steps:**
- **Entity Extraction**: Run with custom circuit descriptions
- **Component Selection**: Execute with predefined templates or custom components
- **Schematic Generation**: Generate circuit DSL from custom inputs
- **Layout & Simulation**: Create layouts and run simulations independently
- **DRC Validation**: Run design rule checks on generated layouts

**Features:**
- Manual step execution
- Custom input capabilities
- Detailed step-by-step control
- Individual result inspection
- Template-based processing
- DRC results display and analysis

## 🎯 Key Features

### Circuit Design Automation
- **Intelligent Component Matching**: AI-powered selection of photonic components based on specifications
- **Automatic Routing**: Smart connection generation between components
- **Layout Generation**: GDS file creation for fabrication
- **Simulation Integration**: Circuit performance analysis using SAX
- **Template Workflows**: Pre-defined circuit templates with customizable parameters

### Design Rule Checking (DRC)
- **KLayout Integration**: Automated DRC using industry-standard KLayout
- **Manufacturing Validation**: Checks for minimum feature sizes, spacing, and design rules
- **Error Reporting**: Detailed DRC violation reports with visual feedback
- **Layer Compatibility**: Handles GDS layer number limitations gracefully

### Knowledge Base Integration
- **Component Library**: Extensive photonic component database including:
  - MZI (Mach-Zehnder Interferometer) variants with heaters
  - Directional couplers and splitters
  - Waveguides and bends
  - Active components with TiN heaters
- **FDTD Simulations**: Pre-computed electromagnetic simulations
- **Design Templates**: Reusable circuit configurations
- **Process Design Kit**: Manufacturing-ready component definitions

### User Experience
- **Interactive Web Interface**: Streamlit-based responsive UI
- **Real-time Feedback**: Live progress updates and status indicators
- **Error Recovery**: Graceful handling of failures with retry mechanisms
- **Export Capabilities**: Multiple output formats (GDS, YAML, PNG)
- **Token Usage Tracking**: Monitor LLM API usage and costs
- **Runtime Performance**: Track workflow execution times

## 🏃‍♂️ Running the Application

Before starting:
```bash
export PYTHONPATH='.'
```
Set ```./PhIDO-Release``` as a PYTHONPATH environmental variable.

### Quick Start
```bash
make run
```

### Manual Start
```bash
streamlit run PhotonicsAI/Photon/webapp.py
```

## 📊 Example Usage

For detailed tutorials with step-by-step instructions and practical examples, see [GETTING_STARTED.md](GETTING_STARTED.md).

### Template-Based Design
1. **Start the application** and select "Step-by-Step Workflow"
2. **Choose a template** (e.g., "MZI with TiN heaters")
3. **Customize parameters** (length, width, heater specifications)
4. **Generate circuit DSL** from template
5. **Create layout** and run simulations
6. **Validate with DRC** for manufacturing readiness

### Custom Circuit Design
1. **Start the application** and select "Automatic Workflow"
2. **Enter a circuit description** (e.g., "Design a 2x2 Mach-Zehnder interferometer with heaters")
3. **Follow the guided process** through all steps
4. **Review generated schematics** and layouts
5. **Check DRC results** for any violations
6. **Export results** for fabrication or further analysis

## 🔧 Development

### Project Structure Details

- **`webapp.py`**: Main Streamlit application with UI components and workflow logic
- **`llm_api.py`**: LLM integration layer supporting multiple providers and models
- **`utils.py`**: Utility functions for circuit processing, DOT graph generation, and data handling
- **`prompts.yaml`**: Structured prompts for different LLM tasks and workflow steps
- **`templates.yaml`**: Circuit templates and component configurations
- **`drc/`**: Design Rule Checking module with KLayout integration
- **`KnowledgeBase/`**: Photonic component library and simulation data

### Adding New Components

To add new photonic components:

1. Create component file in `KnowledgeBase/DesignLibrary/`
2. Define component geometry and parameters
3. Add S-parameter models for simulation
4. Update component templates in `templates.yaml`
5. Add corresponding prompts in `prompts.yaml`

### Extending DRC Rules

To add new design rules:

1. Modify `drc/drc_script.drc` with new rule definitions
2. Update layer definitions and constraints
3. Test with sample layouts
4. Update DRC reporting in `webapp.py`

### Adding New LLM Models

To add support for new LLM models:

1. Add the model configuration in `llm_api.py`
2. Update the model selection in `webapp.py`
3. Add corresponding environment variables
4. Test with appropriate prompts

## 🐛 Troubleshooting

### Common Issues

1. **GDS Layer Number Errors**: PhIDO automatically handles large layer numbers with fallback strategies
2. **DRC Failures**: Check KLayout installation and DRC script configuration
3. **LLM API Errors**: Verify API keys and model availability
4. **Component Import Errors**: Ensure all dependencies are installed correctly

### Environment Setup
If pygraphviz fails to build .whl file, try:
```bash
sudo apt-get update
sudo apt-get install -y build-essential
sudo apt-get install -y python3-dev
sudo apt-get install -y swig
```
and rerun ```requirements.txt``` pip install.

If you encounter import issues during running of PhIDO:
```bash
export PYTHONPATH='.'  
```

### Startup Error

If you encounter the error below:
```bash
ModuleNotFoundError: No module named 'kfactory.routing.generic'
```
do
```bash
pip install kfactory==0.21.1
```
Ignore the pip dependency resolver conflict with gdsfactory 8.8.5.

### Log Error

If you encounter a logger error, create a ```log``` folder under ```PhIDO-Release/PhotonicsAI```.

## 🤝 Contributing

## 📢 发布说明（2025-11-03）

本次更新聚焦于端到端稳定性提升与常见错误的自愈处理，核心变化如下：

- 修复与改进
   - 参数过滤与兼容：在生成 GDSFactory netlist 时，对每个实例的设置项做“允许参数白名单”过滤（基于 PDK 反射与 DesignLibrary 函数签名双重推断），自动剔除组件不接受的参数（如 `waveguide_width`），避免 `TypeError: unexpected keyword argument`。
   - 端口与命名映射：从 DOT 节点标签中解析 DSL 节点 id，建立 DOT→DSL 映射，修复顶层 `ports` 使用 DOT 名（如 `C1`）而实例名为 DSL 名（如 `N1`）导致的构建失败（`'C1' not in ['N1']`）。
   - 端口数量兜底：若从 DOT 未能推断到≥2个外部端口，自动回退暴露至少两个端口（优先选用首/尾节点），避免 SAX 报错 `at least 2 ports need to be defined`。
   - 结构化输出解析更稳健：优先严格 JSON 解析，失败再走 YAML 兜底；自动剥离 Markdown 代码围栏，遇到包含冒号的叙述性字段自动加引号或转为 block scalar，降低 YAML 解析失败概率。
   - DOT 清洗与布局兜底：清理 DOT 中的代码围栏/注释，补齐/配平大括号；解析失败时将无效 DOT 存入 `build/invalid_dot_*.dot` 以便诊断；坐标提取失败时回退到线性布置，保证后续流程不中断。
   - 端口解析健壮性：开放端口提取允许端点中包含额外冒号（如方位后缀），避免 `too many values to unpack`。

- 稳定性与体验
   - 组件选择阶段：操作按钮（提交/自动选择/重置）始终可见，不因模板缺失而阻塞流程。
   - 放置与别名：根据 DOT label 中的 DSL id 建立别名坐标，大小写不敏感匹配，避免 `KeyError`（如 `A` vs `N1`）。
   - netlist 转换：对缺失 `placement` 的节点提供回退坐标，避免 `KeyError: 'placement'`。

- 使用提示
   - 启动：
      - 本地：`streamlit run PhotonicsAI/Photon/webapp.py`
      - 远程访问：建议使用 `--server.address 0.0.0.0 --server.port 8501` 并开放/转发端口。
   - API Key：`.env` 中配置 `ZHIPU_API_KEY`；`OPENAI_API_KEY` 可选（部分步骤用作严格结构化解析）。

- 兼容性
   - 对现有 DSL/模板保持向后兼容；如需让 `mzi_2x2_heater_tin_cband` 支持可调宽度，可在组件中新增参数（例如 `width`），当前默认宽度不变。

- 已知问题
   - 若 LLM 输出夹带自然语言/Markdown，仍可能触发兜底路径；建议使用纯 JSON/DOT 输出以发挥最佳稳定性。
   - 生成的无效 DOT 会保存在 `build/invalid_dot_*.dot`，可用于后续提示工程与清洗策略优化。

更多细节请参考 `PhotonicsAI/Photon/utils.py` 与 `PhotonicsAI/Photon/llm_api.py` 的注释与实现。

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Streamlit for the web interface
- Powered by various LLM providers (OpenAI, Anthropic, Google, NVIDIA)
- Uses GDSFactory for photonic layout generation
- Integrates with SAX for circuit simulations
- KLayout for Design Rule Checking
- Template-based workflows for rapid prototyping
