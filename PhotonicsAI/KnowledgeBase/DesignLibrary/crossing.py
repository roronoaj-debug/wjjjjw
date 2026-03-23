"""This is a waveguide crossing.

---
Name: waveguide crossing
Description: This is a waveguide crossing
ports: 1x1
NodeLabels:
    - passive
Bandwidth: 100 nm
Args:
    -length: straight length (um)
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import sax_models_removed

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
def crossing(
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """The component."""
    c = gf.Component()
    ref = c << gf.components.crossing(cross_section="strip")
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])
    c.flatten()
    return c


def get_model(model="fdtd"):
    """Return a placeholder now that SAX models were removed."""
    return sax_models_removed("crossing")


if __name__ == "__main__":
    component = crossing()
    print(component.get_netlist())
