"""This is a 1x1 Mach-Zehnder interferometer (MZI) with 50-50 directional couplers.

---
Name: MZI 1x1 - Thermo-optic (mzi_1x1_heater_doped_si_cband)
Description: >
    This is a 1x1 Mach-Zehnder interferometer (MZI) with 50-50 directional couplers.
    Integrated in both arms of the MZI are doped heaters.
ports: 1x1
NodeLabels:
    - modulator
    - active
    - amplitude modulation (AM)
aka: amplitude modulator, Mach-Zehnder interferometer, MZI
Technology : Thermo-optic effect (TO)
Design wavelength: 1450-1650 nm
Optical Bandwidth: 200 nm
Polarization: TE/TM
Modulation bandwidth/Switching speed: 200 KHz
Insertion loss: 2 dB
Extinction ratio: 25 dB
Drive voltage/power: 0.75 V
Footprint Estimate: 435.6um x 464.2um
Args:
    -length: straight length heater (um)
    -delta_length: path length difference (um). bottom arm vertical extra length.
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary import (
    _mmi1x2,
    bend_euler,
    heater_doped_si_cband,
    straight,
)


@gf.cell
def mzi_1x1_heater_doped_si_cband(
    delta_length: float = 10, length: float = 320
) -> gf.Component:
    """The component."""
    c = gf.Component()

    xs_1550 = gf.cross_section.cross_section(width=0.5, offset=0, layer="WG")

    mmi1x2 = _mmi1x2._mmi1x2()
    ref = c << gf.components.mzi(
        delta_length=delta_length,
        length_y=129.175,
        length_x=length,
        straight_x_top=heater_doped_si_cband.heater_doped_si_cband,
        straight_x_bot=heater_doped_si_cband.heater_doped_si_cband,
        splitter=mmi1x2,
        combiner=mmi1x2,
        cross_section=xs_1550,
    )

    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    return c


def get_model(model="fdtd"):
    """Get the model for the edge coupler."""
    m1 = _mmi1x2.get_model(model=model)
    m2 = straight.get_model(model=model)
    m3 = bend_euler.get_model(model=model)
    m4 = heater_doped_si_cband.get_model(model=model)
    combined_dict = m1 | m2 | m3 | m4
    return combined_dict


if __name__ == "__main__":
    c = gf.Component()
    ref = c << mzi_1x1_heater_doped_si_cband()
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    print(c.get_netlist())
