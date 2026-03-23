"""This is an adiabatic directional coupler with two input and two output ports.

---
Name: directional_coupler
Description: >
    This is an adiabatic directional coupler with two input and two output ports.
    Can be used for 50:50 power splitting. The device is optimized for 1480 nm.
ports: 2x2
NodeLabels:
    - passive
Bandwidth: 50 nm
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import \
    sax_models_removed

# from PhotonicsAI.Photon.utils import validate_cell_settings


# {'cross_section': 'strip', 'dx': 10, 'dy': 4, 'gap': 0.236, 'length': 20}


@gf.cell
def _directional_coupler_adiabatic() -> gf.Component:
    _args = locals()

    c = gf.Component()
    coupler = gf.components.coupler_adiabatic()
    coupler_r = c << coupler
    c.add_port("o1", port=coupler_r.ports["o1"])
    c.add_port("o2", port=coupler_r.ports["o2"])
    c.add_port("o3", port=coupler_r.ports["o3"])
    c.add_port("o4", port=coupler_r.ports["o4"])
    c.flatten()
    return c


def get_model(model: str = "fdtd") -> dict:
    return sax_models_removed("_directional_coupler_adiabatic")


if __name__ == "__main__":
    c = _directional_coupler_adiabatic()

    print(c.get_netlist())
