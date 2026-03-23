"""This is a laser with tunable wavelength.

---
Name: laser
Description: This is a laser with tunable wavelength
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
def laser(
    length: float = 10.0,
    npoints: int = 2,
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """The component."""
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.straight(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("laser")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()
    ref = c << laser(length=100)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])

    pprint(c.get_netlist())
