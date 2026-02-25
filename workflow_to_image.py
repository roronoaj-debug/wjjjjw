"""
将Mermaid流程图HTML转换为PNG/SVG图片

依赖：
- pip install pillow playwright
- playwright install chromium
"""

import subprocess
import sys
from pathlib import Path

def convert_html_to_image(html_path, output_path, format='png'):
    """
    使用Playwright将HTML转换为图片
    
    Args:
        html_path: HTML文件路径
        output_path: 输出图片路径
        format: 'png' 或 'pdf'
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要安装 playwright: pip install playwright")
        print("然后运行: playwright install chromium")
        return False
    
    html_path = Path(html_path).resolve()
    output_path = Path(output_path).resolve()
    
    print(f"📄 读取HTML: {html_path}")
    print(f"🎨 转换为{format.upper()}...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": 1600, "height": 1200},
                device_scale_factor=2  # 高DPI
            )
            
            # 加载HTML
            page.goto(f'file://{html_path}')
            
            # 等待Mermaid渲染完成
            page.wait_for_selector('.mermaid svg', timeout=30000)
            
            # 导出为图片
            if format.lower() == 'png':
                page.screenshot(path=output_path, full_page=True)
            elif format.lower() == 'pdf':
                page.pdf(path=output_path)
            
            browser.close()
        
        print(f"✅ 成功生成: {output_path}")
        print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

def convert_using_cli(html_path, output_path):
    """
    尝试使用命令行工具转换
    """
    # 尝试使用 wkhtmltoimage
    try:
        cmd = ['wkhtmltoimage', str(html_path), str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ 使用wkhtmltoimage成功生成: {output_path}")
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ wkhtmltoimage转换失败: {e}")
    
    return False

if __name__ == '__main__':
    html_file = Path(__file__).parent / 'workflow_diagram.html'
    
    # 输出路径
    png_file = html_file.parent / 'PhIDO_Workflow_Diagram.png'
    pdf_file = html_file.parent / 'PhIDO_Workflow_Diagram.pdf'
    
    if not html_file.exists():
        print(f"❌ HTML文件不存在: {html_file}")
        sys.exit(1)
    
    # 优先使用Playwright
    print("\n------- 尝试使用Playwright转换 -------")
    success_png = convert_html_to_image(html_file, png_file, 'png')
    
    if success_png:
        print("\n🎉 PNG转换成功!")
    else:
        print("\n💡 尝试使用CLI工具...")
        success_cli = convert_using_cli(html_file, png_file)
        if not success_cli:
            print("""
❌ 自动转换失败，请手动操作：

方法1 - 使用浏览器（推荐）：
  1. 用Chrome/Edge打开: workflow_diagram.html
  2. 右键 → 打印 → 另存为PDF
  3. 或使用截图工具截取

方法2 - 使用命令行工具：
  # 安装wkhtmltoimage
  # Windows: choco install wkhtmltopdf
  # Mac: brew install wkhtmltopdf
  # Linux: apt-get install wkhtmltopdf
  
方法3 - 安装依赖后重试：
  pip install playwright
  playwright install chromium
  python workflow_to_image.py
            """)
            sys.exit(1)
