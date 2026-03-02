import time
import json
import os
import re
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import gdsfactory as gf

# ==================== 配置区域 ====================

# 目标输出目录 (DesignLibrary)
# 假设脚本在 scripts/ 目录下，向上两级找到 PhotonicsAI
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "PhotonicsAI", "KnowledgeBase", "DesignLibrary"))

# 关键词配置
DEVICE_keywords = {
    # --- Active Devices ---
    "ge_pd": [
        "Germanium photodetector bandwidth",
        "GePD waveguide integrated",
    ],
    "si_modulator": [
        "Silicon Mach-Zehnder modulator",
        "silicon travelling wave modulator",
    ],
    "si_phase_shifter": [
        "thermo-optic phase shifter silicon",
        "silicon photonic heater",
    ],
    
    # --- Passive Devices (Si & SiN MMI) ---
    "mmi1x2": [
        "1x2 MMI silicon photonics splitter",
        "multimode interferometer 1x2 design",
    ],
    "mmi2x2": [
        "2x2 MMI coupler silicon",
        "multimode interferometer 2x2",
    ],
    
    # --- Crossings & Couplers ---
    "waveguide_crossing": [
        "silicon waveguide crossing loss",
    ],
    "directional_coupler": [
        "silicon directional coupler design",
        "directional coupler splitting ratio",
    ],
    
    # --- IO Couplers ---
    "grating_coupler": [
        "silicon grating coupler efficiency",
        "focusing grating coupler design",
    ],
    "edge_coupler": [
        "spot size converter silicon photonics",
        "inverse taper coupling efficiency",
    ],
    
    # --- Polarization ---
    "pbs_pbr": [
        "polarization beam splitter silicon",
        "polarization rotator integrated photonics",
    ]
}

MAX_RESULTS_PER_KEYWORD = 10  # 增加检索数量

# ==================== 组件代码模板 ====================

TEMPLATES = {
    # ================= Active Devices =================
    "ge_pd": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length: float = {length},
    width: float = {width},
) -> gf.Component:
    """Auto-generated Ge Photodetector from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 模拟 GePD 结构 (PIN结)
    # 实际应用中需指定 doping layers
    ref = c << gf.components.straight_pin(length=length, cross_section="rib")
    c.add_ports(ref.ports)
    return c
''',

    "si_modulator": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length_phase_shifter: float = {length},
) -> gf.Component:
    """Auto-generated MZM Modulator from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 模拟 Mach-Zehnder Modulator
    mzm = gf.components.mzi(
        delta_length=0,
        length_x=length_phase_shifter,
        splitter=gf.components.mmi1x2,
        combiner=gf.components.mmi1x2
    )
    ref = c << mzm
    c.add_ports(ref.ports)
    return c
''',
    
    "si_phase_shifter": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length: float = {length},
    heater_width: float = 2.0,
) -> gf.Component:
    """Auto-generated Thermo-optic Phase Shifter from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 带加热器的直波导
    ref = c << gf.components.straight_heater_metal(
        length=length,
        heater_width=heater_width
    )
    c.add_ports(ref.ports)
    return c
''',

    # ================= Passive Devices =================
    "mmi1x2": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length_mmi: float = {length_mmi},
    width_mmi: float = {width_mmi},
    gap_mmi: float = {gap_mmi},
    width_taper: float = {width_taper},
    length_taper: float = {length_taper},
) -> gf.Component:
    """Auto-generated 1x2 MMI from: {title}
    Source: {link}
    """
    c = gf.Component()
    ref = c << gf.components.mmi1x2(
        length_mmi=length_mmi,
        width_mmi=width_mmi,
        gap_mmi=gap_mmi,
        width_taper=width_taper,
        length_taper=length_taper,
    )
    c.add_ports(ref.ports)
    return c
''',

    "mmi2x2": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length_mmi: float = {length_mmi},
    width_mmi: float = {width_mmi},
    gap_mmi: float = {gap_mmi},
    width_taper: float = {width_taper},
    length_taper: float = {length_taper},
) -> gf.Component:
    """Auto-generated 2x2 MMI from: {title}
    Source: {link}
    """
    c = gf.Component()
    ref = c << gf.components.mmi2x2(
        length_mmi=length_mmi,
        width_mmi=width_mmi,
        gap_mmi=gap_mmi,
        width_taper=width_taper,
        length_taper=length_taper,
    )
    c.add_ports(ref.ports)
    return c
''',

    "waveguide_crossing": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: {title}
    Source: {link}
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
''',

    "directional_coupler": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length: float = {length},
    gap: float = {gap},
) -> gf.Component:
    """Auto-generated Directional Coupler from: {title}
    Source: {link}
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
''',

    "grating_coupler": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    period: float = 0.63,
    fill_factor: float = 0.5,
) -> gf.Component:
    """Auto-generated Grating Coupler from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 聚焦型光栅耦合器
    ref = c << gf.components.grating_coupler_elliptical(
        period=period,
        fill_factor=fill_factor
    )
    c.add_ports(ref.ports)
    return c
''',

    "edge_coupler": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    width_tip: float = 0.15,
    length_taper: float = {length},
) -> gf.Component:
    """Auto-generated Edge Coupler (SSC) from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 倒锥形耦合器 (Inverse Taper)
    ref = c << gf.components.taper(
        width1=width_tip,
        width2=0.5,
        length=length_taper
    )
    c.add_ports(ref.ports)
    return c
''',
    
    "pbs_pbr": '''
import gdsfactory as gf

@gf.cell
def {func_name}(
    length: float = {length},
) -> gf.Component:
    """Auto-generated PBS/PBR from: {title}
    Source: {link}
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
'''
}

# ==================== 爬虫辅助函数 ====================

def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # 调试时可注释掉
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_params_with_llm(text, device_type):
    """(可选) 使用 OpenAI GPT-4 提取精准参数
    需要设置环境变量 OPENAI_API_KEY 或直接在代码中填入
    """
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY") # 或者填入 "sk-..."
        if not api_key:
            return None
            
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        You are an expert in silicon photonics PDK development. 
        Extract key geometry parameters for a "{device_type}" device from the following text.
        
        Return a JSON object ONLY, with keys matching standard GDSFactory parameters:
        - For MMI: length_mmi, width_mmi, gap_mmi, width_taper, length_taper
        - For Ring: radius, gap, length_x
        - For Directional Coupler: length, gap
        - For Modulator: length
        - For GePD: length, width
        
        If a parameter is not explicitly found, estimate a standard value for a 220nm SOI platform (C-band).
        Do not include markdown formatting like ```json.
        
        Text:
        {text[:4000]}
        """
        
        response = client.chat.completions.create(
            model="gpt-4-turbo", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
        
    except ImportError:
        print("OpenAI library not installed. Run `pip install openai`.")
        return None
    except Exception as e:
        print(f"LLM Extraction failed: {e}")
        return None

def extract_params_heuristic(text, device_type):
    """启发式参数提取 (默认回退方案)"""
    
    # 1. 尝试使用 LLM (如果配置了 API Key)
    llm_params = extract_params_with_llm(text, device_type)
    if llm_params:
        print(f"  [LLM] Successfully extracted params for {device_type}")
        return llm_params
        
    print(f"  [Heuristic] Falling back to regex extraction...")
    params = {}
    
    # 简单的正则匹配
    #寻找类似 "length: 10 um" 或 "length of 10um" 的模式
    length_match = re.search(r'length.*?(\d+\.?\d*)', text, re.IGNORECASE)
    width_match = re.search(r'width.*?(\d+\.?\d*)', text, re.IGNORECASE)
    gap_match = re.search(r'gap.*?(\d+\.?\d*)', text, re.IGNORECASE)
    radius_match = re.search(r'radius.*?(\d+\.?\d*)', text, re.IGNORECASE)

    # 默认值 (防止生成失败，保证代码可运行)
    # 在真实场景中，如果提取失败应该跳过或标记
    # 这里我们为每种新设备添加了默认参数
    defaults = {
        # Active
        "ge_pd": {"length": 20.0, "width": 1.0},
        "si_modulator": {"length": 1000.0}, # 1mm default for modulators
        "si_phase_shifter": {"length": 100.0},
        
        # Passive
        "mmi1x2": {"length_mmi": 10.0, "width_mmi": 4.0, "gap_mmi": 0.25, "width_taper": 1.0, "length_taper": 5.0},
        "mmi2x2": {"length_mmi": 25.0, "width_mmi": 6.0, "gap_mmi": 0.25, "width_taper": 1.0, "length_taper": 5.0},
        "waveguide_crossing": {"width": 0.5},
        "directional_coupler": {"length": 20.0, "gap": 0.2},
        "grating_coupler": {"period": 0.63, "fill_factor": 0.5},
        "edge_coupler": {"length": 150.0},
        "pbs_pbr": {"length": 30.0},
        
        # Old
        "ring_resonator": {"radius": 10.0, "gap": 0.2, "length_x": 0.0, "length_y": 0.0},
        "y_branch": {"length": 15.0}
    }
    
    p = defaults.get(device_type, {}).copy()
    
    # 通用的参数提取逻辑
    if length_match: 
        # MMI 的长度通常叫 length_mmi
        if "mmi" in device_type: p["length_mmi"] = float(length_match.group(1))
        # 其他设备通常叫 length
        else: p["length"] = float(length_match.group(1))
        
    if width_match:
        if "mmi" in device_type: p["width_mmi"] = float(width_match.group(1))
        else: p["width"] = float(width_match.group(1))
        
    if gap_match:
        if "mmi" in device_type: p["gap_mmi"] = float(gap_match.group(1))
        else: p["gap"] = float(gap_match.group(1))

    return p

# ==================== 代码生成 ====================

def generate_component_file(paper_info):
    """根据爬取的论文信息生成 .py 文件"""
    device_type = paper_info['device_type']
    if device_type not in TEMPLATES:
        return None
        
    # 提取参数
    params = extract_params_heuristic(paper_info['full_text'], device_type)
    
    # 生成唯一函数名 (去除非法字符)
    safe_title = re.sub(r'[^a-zA-Z0-9]', '', paper_info['title'])[:20]
    func_name = f"auto_{device_type}_{safe_title}_{random.randint(100,999)}"
    filename = f"{func_name}.py"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # 填充模板
    try:
        code = TEMPLATES[device_type].format(
            func_name=func_name,
            title=paper_info['title'],
            link=paper_info['link'],
            **params
        )
        
        # 确保目录存在
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
            
        print(f"[SUCCESS] Generated: {filename}")
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to generate code for {paper_info['title']}: {e}")
        return None

# ==================== 爬虫逻辑 (ArXiv Demo) ====================

def search_arxiv(driver, keyword, device_type):
    results = []
    # ArXiv 搜索 URL
    url = f"https://arxiv.org/search/?searchtype=all&query={keyword.replace(' ', '+')}&start=0"
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        articles = soup.find_all('li', class_='arxiv-result')
        if not articles:
            print(f"  No results for keyword: {keyword}")
            return []
            
        for article in articles[:MAX_RESULTS_PER_KEYWORD]:
            try:
                title = article.find('p', class_='title').get_text(strip=True)
                
                abstract_span = article.find('span', class_='abstract-full')
                if not abstract_span: # 尝试找 short
                    abstract_span = article.find('span', class_='abstract-short')
                
                abstract = abstract_span.get_text(strip=True) if abstract_span else ""
                
                link_tag = article.find('p', class_='list-title').find('a')
                link = link_tag['href'] if link_tag else "N/A"
                
                full_text = f"{title} {abstract}"
                
                results.append({
                    "source": "arxiv",
                    "title": title,
                    "link": link,
                    "abstract": abstract,
                    "full_text": full_text,
                    "device_type": device_type
                })
            except Exception as inner_e:
                # print(f"  Skipping one article: {inner_e}")
                continue
    except Exception as e:
        print(f"  ArXiv connection error: {e}")
        
    return results

# ==================== 主流程 ====================

def main():
    print("=== Auto-PDK Generator Started ===")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"Creating directory: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)
    
    driver = init_driver()
    all_papers = []

    try:
        for device_type, keywords in DEVICE_keywords.items():
            print(f"\nSearching for {device_type}...")
            for kw in keywords:
                papers = search_arxiv(driver, kw, device_type)
                all_papers.extend(papers)
                print(f"  Found {len(papers)} papers for '{kw}'")
    
    finally:
        try:
            driver.quit()
        except:
            pass

    print(f"\nProcessing {len(all_papers)} papers for code generation...")
    
    generated_count = 0
    for paper in all_papers:
        filepath = generate_component_file(paper)
        if filepath:
            generated_count += 1

    print("\n" + "="*50)
    print(f"COMPLETE: Generated {generated_count} new components in DesignLibrary.")
    print(f"Location: {OUTPUT_DIR}")
    print("="*50)

if __name__ == "__main__":
    main()
