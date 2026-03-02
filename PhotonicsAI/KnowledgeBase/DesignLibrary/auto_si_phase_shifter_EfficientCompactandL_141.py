
import gdsfactory as gf

@gf.cell
def auto_si_phase_shifter_EfficientCompactandL_141(
    length: float = 100.0,
    heater_width: float = 2.0,
) -> gf.Component:
    """Auto-generated Thermo-optic Phase Shifter from: Efficient, Compact and Low LossThermo-OpticPhaseShifterinSilicon
    Source: https://arxiv.org/abs/1410.3616
    """
    c = gf.Component()
    # 带加热器的直波导
    ref = c << gf.components.straight_heater_metal(
        length=length,
        heater_width=heater_width
    )
    c.add_ports(ref.ports)
    return c
