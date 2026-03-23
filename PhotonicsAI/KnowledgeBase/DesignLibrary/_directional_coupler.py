"""This is a directional coupler with two input and two output ports.

---
Name: directional_coupler
Description: >
    A directional coupler with two input and two output ports.
    Can be used for power splitting.
ports: 2x2
NodeLabels:
    - passive
Bandwidth: 50 nm
Args:
    -gap: between straights in um.
    -length: of coupling region in um.
    -dy: port to port vertical spacing in um.
    -dx: length of bend in x direction in um.
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import sax_models_removed

# from PhotonicsAI.Photon.utils import validate_cell_settings


# {'cross_section': 'strip', 'dx': 10, 'dy': 4, 'gap': 0.236, 'length': 20}


@gf.cell
def _directional_coupler(
    length: float = 20.0,
    dy: float = 4.0,
    dx: float = 10.0,
) -> gf.Component:
    _args = locals()

    c = gf.Component()
    coupler = gf.components.coupler(**_args)
    coupler_r = c << coupler
    c.add_port("o1", port=coupler_r.ports["o1"])
    c.add_port("o2", port=coupler_r.ports["o2"])
    c.add_port("o3", port=coupler_r.ports["o3"])
    c.add_port("o4", port=coupler_r.ports["o4"])

    c.flatten()
    return c


def get_model(model: str = "fdtd") -> dict:
    return sax_models_removed("_directional_coupler")


if __name__ == "__main__":
    component = _directional_coupler(dx=100, dy=40)
    print(component.get_netlist())
