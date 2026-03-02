
import gdsfactory as gf

@gf.cell
def auto_si_phase_shifter_ThermallyInducedRefr_388(
    length: float = 561.0,
    heater_width: float = 2.0,
) -> gf.Component:
    """Auto-generated Thermo-optic Phase Shifter from: Thermally Induced Refractive Index Trimming of Visible-LightSiliconNitride Waveguides Using SuspendedHeaters
    Source: https://arxiv.org/abs/2504.21262
    """
    c = gf.Component()
    # 带加热器的直波导
    ref = c << gf.components.straight_heater_metal(
        length=length,
        heater_width=heater_width
    )
    c.add_ports(ref.ports)
    return c
