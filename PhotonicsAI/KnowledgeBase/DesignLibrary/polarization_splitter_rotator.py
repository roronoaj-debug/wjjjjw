"""This is a polarization splitter rotator used (1) separate TE and TM polarized light.

---
Name: Polarization splitter rotator (PSR)
Description: >
This is a polarization splitter rotator used (1) separate TE and TM polarized light
and (2) convert the TM polarized light to TE polarized light.
ports: 1x2
NodeLabels:
    - passive
Bandwidth: 70 nm
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
def polarization_splitter_rotator(
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """The component."""
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.polarization_splitter_rotator(
        width_taper_in=(0.54, 0.69, 0.83),
        length_taper_in=(4, 44),
        width_coupler=(0.9, 0.404),
        length_coupler=7,
        gap=0.15,
        width_out=0.54,
        length_out=14.33,
        dy=5,
        cross_section="strip",
    )
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("polarization_splitter_rotator")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()
    ref = c << polarization_splitter_rotator()
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])

    pprint(c.get_netlist())
