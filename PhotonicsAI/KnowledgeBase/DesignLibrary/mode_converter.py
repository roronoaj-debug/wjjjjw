"""This is a mode converter cell that converts the mode from TE0 to TE1.

---
Name: Mode Converter
Description: Converts the mode from TE0 to TE1
ports: 2x2
NodeLabels:
    - passive
Bandwidth: 100 nm
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
def mode_converter(
    gap: float = 0.3,
    length: int = 10,
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """The component."""
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.mode_converter(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])

    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("mode_converter")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()
    ref = c << mode_converter()
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])

    pprint(c.get_netlist())
