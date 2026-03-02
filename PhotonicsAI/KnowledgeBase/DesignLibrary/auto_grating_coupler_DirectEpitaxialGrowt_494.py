
import gdsfactory as gf

@gf.cell
def auto_grating_coupler_DirectEpitaxialGrowt_494(
    period: float = 0.63,
    fill_factor: float = 0.5,
) -> gf.Component:
    """Auto-generated Grating Coupler from: Direct Epitaxial Growth and Deterministic Device Integration of high-quality Telecom O-Band InGaAs Quantum Dots on Silicon Substrate
    Source: https://arxiv.org/abs/2512.10073
    """
    c = gf.Component()
    # 聚焦型光栅耦合器
    ref = c << gf.components.grating_coupler_elliptical(
        period=period,
        fill_factor=fill_factor
    )
    c.add_ports(ref.ports)
    return c
