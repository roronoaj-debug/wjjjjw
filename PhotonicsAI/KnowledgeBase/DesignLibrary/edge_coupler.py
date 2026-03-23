"""This is a design for an inverse taper edge coupler to couple light onto the chip.

---
Name: Edge coupler
Description: This is a design for an inverse taper edge coupler to couple light onto the chip.
ports: 1x1
NodeLabels:
    - passive
Bandwidth: 100 nm
Args:
    -length: straight length (um)
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import (
    sax_models_removed,
)

# import pickle

# from PhotonicsAI.Photon.utils import validate_cell_settings

# args = {
#     'functional': {
#     },
#     'geometrical': {
#         'length':   {'default': 10., 'range': (0.1, 20000.0)},
#     }
# }


@gf.cell
def edge_coupler(
    length: float = 10.0,
    width1: float = 0.2,
    width2: float = 0.5,
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """The component."""
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.edge_coupler_silicon(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("edge_coupler")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()
    ref = c << edge_coupler(length=100)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    pprint(c.get_netlist())
