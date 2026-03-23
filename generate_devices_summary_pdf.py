#!/usr/bin/env python3
"""
生成光子器件库PDF摘要
Generate PDF summary of photonic devices library
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime

def create_pdf_summary(output_filename="OptiAi_Photonic_Devices_Summary.pdf"):
    """创建光子器件库PDF摘要"""
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 存储所有元素
    elements = []
    
    # 样式
    styles = getSampleStyleSheet()
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # 副标题样式
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # 类别标题样式
    category_style = ParagraphStyle(
        'CategoryTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#d32f2f'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # 标题
    elements.append(Paragraph("OptiAi Photonic Devices Library", title_style))
    elements.append(Paragraph("光子器件设计库 - 新增器件清单与分类", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # 日期
    date_str = datetime.now().strftime("%Y年%m月%d日")
    elements.append(Paragraph(f"Generated: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # 定义表格样式
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ])
    
    # 1. 射频/微波光子器件
    elements.append(Paragraph("📡 射频/微波光子器件 (RF Photonics)", category_style))
    rf_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['SOI Microwave Phase Shifter', 'soi_microwave_phase_shifter.py', 'IEEE Photonics Journal', 'DC-40+ GHz, 0-360°'],
        ['Photonic Microwave Mixer', 'photonic_microwave_mixer.py', 'JLT 2020', 'Frequency conversion, SFDR'],
        ['Si₃N₄ RF Beamformer', 'rf_beamformer_sin.py', 'IEEE', 'K-band, 2D beam control'],
        ['Ring-Assisted MZM', 'ring_assisted_mzm.py', 'arXiv:2110.02737', '+18dB SFDR'],
    ]
    rf_table = Table(rf_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    rf_table.setStyle(table_style)
    elements.append(rf_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. 高速调制器
    elements.append(Paragraph("⚡ 高速调制器 (High-Speed Modulators)", category_style))
    mod_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['High-Power LN MZM', 'high_power_ln_mzm.py', 'arXiv:2210.14785', '110GHz, 110mW'],
        ['PAM-4 Modulator', 'pam4_mzm.py', 'JLT 2019', '100+ Gb/s, 4-level'],
        ['Segmented MZM', 'segmented_mzm_distributed_driver.py', 'IEEE (UCSB)', '5-segment + 45nm CMOS'],
        ['Hybrid Si/LN MZM', 'hybrid_ln_mzm.py', 'arXiv', 'High-bandwidth EO'],
        ['SOH Modulator', 'soh_modulator.py', 'IEEE', 'Organic high-speed'],
        ['Plasmonic Modulator', 'plasmonic_modulator.py', 'Multiple refs', 'Ultra-compact, >100GHz'],
        ['2μm MZM', 'mzm_2um.py', 'Photonics Research 2021', 'Extended wavelength'],
    ]
    mod_table = Table(mod_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    mod_table.setStyle(table_style)
    elements.append(mod_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 3. 可编程/可重构器件
    elements.append(Paragraph("🔄 可编程/可重构器件 (Programmable Photonics)", category_style))
    prog_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['MEMS Latching PPIC', 'mems_latching_ppic.py', 'arXiv:2601.06578', 'Zero-hold power'],
        ['MEMS Latching MZI', 'mems_latching_mzi.py', 'IEEE', 'Non-volatile switch'],
        ['MZI Lattice Filter', 'mzi_lattice_filter.py', 'Multiple refs', 'FIR/IIR filtering'],
        ['MEMS Ring DWDM', 'mems_ring_dwdm.py', 'IEEE', 'Tunable DWDM'],
        ['PCM 7-bit Ring', 'pcm_ring_7bit.py', 'arXiv:2412.07447', '127 levels, Sb₂S₃'],
        ['PCM Tunable Ring', 'pcm_tunable_ring.py', 'Multiple refs', 'Phase-change tuning'],
    ]
    prog_table = Table(prog_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    prog_table.setStyle(table_style)
    elements.append(prog_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 4. 耦合器/分束器
    elements.append(Paragraph("🔗 耦合器/分束器 (Couplers & Splitters)", category_style))
    coupler_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['Inverse Design MMI', 'inverse_design_mmi.py', 'IEEE', 'Topology optimized'],
        ['FAQUAD Coupler', 'faquad_coupler.py', 'IEEE/Optica', 'Fast quasi-adiabatic'],
        ['SWG Adiabatic Coupler', 'swg_adiabatic_coupler.py', 'Opt. Letters 2018', '>100nm bandwidth'],
        ['III-V/Si Laser Coupler', 'hybrid_iii_v_laser_coupler.py', 'IEEE JSTQE 2015', '>90% efficiency'],
        ['III-V/Si Coupler', 'iii_v_si_coupler.py', 'Multiple refs', 'Heterogeneous integration'],
        ['LNOI MMI Splitter', 'lnoi_mmi_splitter.py', 'IEEE 2023', '50:50, EO compatible'],
        ['Bent DC', 'bent_dc.py', 'IEEE', 'Compact, low loss'],
    ]
    coupler_table = Table(coupler_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    coupler_table.setStyle(table_style)
    elements.append(coupler_table)
    
    # 新页面
    elements.append(PageBreak())
    
    # 5. 偏振器件
    elements.append(Paragraph("🎯 偏振器件 (Polarization Devices)", category_style))
    pol_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['Bragg Grating PBS', 'bragg_grating_pbs.py', 'IEEE', 'Shape optimized, broadband'],
        ['Silicon PBS', 'si_pbs.py', 'Multiple refs', 'TE/TM separation'],
        ['SWG Mode Mux', 'swg_mode_mux.py', 'Multiple refs', 'Mode conversion'],
    ]
    pol_table = Table(pol_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    pol_table.setStyle(table_style)
    elements.append(pol_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 6. 滤波器/谐振器
    elements.append(Paragraph("🔬 滤波器/谐振器 (Filters & Resonators)", category_style))
    filter_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['Athermal DWDM Filter', 'athermal_dwdm_filter.py', 'Heliyon 2022', '6th-order, polarization-insensitive'],
        ['SiN Ring Interleaver', 'sin_ring_interleaver.py', 'IEEE', 'Flat-top response'],
        ['CROW Switch', 'crow_switch.py', 'arXiv:2402.10673', 'Kerr symmetry breaking'],
        ['ScAlN Ring', 'scaln_ring.py', 'arXiv', 'CMOS-compatible piezoelectric'],
        ['LNOI Ring', 'lnoi_ring.py', 'Multiple refs', 'EO tuning'],
    ]
    filter_table = Table(filter_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    filter_table.setStyle(table_style)
    elements.append(filter_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 7. 光源/激光器
    elements.append(Paragraph("💡 光源/激光器 (Light Sources)", category_style))
    laser_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['GaAs Ring Laser', 'gaas_ring_laser.py', 'IEEE', 'III-V integration'],
        ['Visible ECL', 'ecl_visible.py', 'arXiv', '637nm, quantum applications'],
        ['Si₃N₄ Squeezed Ring', 'si3n4_squeezed_ring.py', 'arXiv', '-4.7dB squeezing'],
    ]
    laser_table = Table(laser_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    laser_table.setStyle(table_style)
    elements.append(laser_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 8. 计算/传感器件
    elements.append(Paragraph("📊 计算/传感器件 (Computing & Sensing)", category_style))
    compute_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['QUBO Photonic Solver', 'qubo_photonic_solver.py', 'arXiv:2407.04713', '16-channel, 2 TFLOP/s'],
        ['Multi-beam OPA', 'multibeam_opa.py', 'arXiv:2510.13608', 'OWC, 54Gbps/user'],
        ['Mid-IR Gas Sensor', 'midir_gas_sensor.py', 'IEEE Sensors 2020', 'Chalcogenide glass, 3-10μm'],
        ['FBG Interrogator', 'fbg_interrogator.py', 'Multiple refs', 'Fiber sensing'],
    ]
    compute_table = Table(compute_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    compute_table.setStyle(table_style)
    elements.append(compute_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 9. 特殊环境/新型器件
    elements.append(Paragraph("🌡️ 特殊环境/新型器件 (Special & Novel Devices)", category_style))
    special_data = [
        ['Device Name', 'File', 'Paper Source', 'Key Parameters'],
        ['Cryogenic AlN MZM', 'cryogenic_aln_mzm.py', 'Nature Photonics', '4K compatible, piezoelectric'],
        ['SAW SiN Modulator', 'saw_sin_modulator.py', 'arXiv', 'Thermo-elastic acousto-optic'],
        ['Visible SiN MMI', 'sin_visible_mmi.py', 'Multiple refs', '637nm, visible light'],
        ['TFLN Crossing', 'tfln_crossing.py', 'Multiple refs', 'Thin-film lithium niobate'],
        ['Graphene WDM Receiver', 'graphene_wdm_receiver.py', 'arXiv', '4×16Gbps, 67GHz'],
    ]
    special_table = Table(special_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
    special_table.setStyle(table_style)
    elements.append(special_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # 统计汇总
    elements.append(Paragraph("统计汇总 / Summary Statistics", category_style))
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=20
    )
    elements.append(Paragraph("• <b>新增器件总数 (Total New Devices):</b> ~45", summary_style))
    elements.append(Paragraph("• <b>涵盖论文 (Papers Covered):</b> ~35", summary_style))
    elements.append(Paragraph("• <b>器件类别 (Device Categories):</b> 10", summary_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 页脚信息
    elements.append(Spacer(1, 0.3*inch))
    footer_text = """
    <para align=center>
    <font size=8 color="#666666">
    OptiAi - Photonic Integrated Device Ontology<br/>
    Design Library Summary | Generated from DesignLibrary/<br/>
    For more information, visit the OptiAi repository
    </font>
    </para>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # 生成PDF
    doc.build(elements)
    print(f"✅ PDF生成成功: {output_filename}")
    return output_filename


if __name__ == "__main__":
    # 生成PDF
    output_file = create_pdf_summary()
    
    # 打印文件大小
    if os.path.exists(output_file):
        size_kb = os.path.getsize(output_file) / 1024
        print(f"📄 文件大小: {size_kb:.2f} KB")
        print(f"📂 保存位置: {os.path.abspath(output_file)}")
