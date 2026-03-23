"""This is a design for a germanium photodetector.

---
Name: Germanium photodetector (PD)
Description: This is a design for a germanium photodetector
ports: 1x1
NodeLabels:
    - active
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
def photodetector(
    length: float = 40.0,
) -> gf.Component:
    """The component."""
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.ge_detector_straight_si_contacts(**_args)
    c.add_port("o1", port=ref.ports["o1"])

    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("photodetector")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()
    ref = c << photodetector(length=100)
    c.add_port("o1", port=ref.ports["o1"])

    pprint(c.get_netlist())
