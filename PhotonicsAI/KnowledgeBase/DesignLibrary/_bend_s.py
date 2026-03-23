"""This is a s-bend using bezier curves.

---
Name: bend_s
Description: This is an s-bend using bezier curves.
ports: 1x1
NodeLabels:
    - passive
    - 1x1
Bandwidth: 100 nm
Args:
    -size: in x (length) and y (height) direction.
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import \
    sax_models_removed


@gf.cell
def _bend_s(
    size: tuple[float, float] = (40.0, 26.0),
) -> gf.Component:
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.bend_s(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.flatten()
    return c


def get_model(model="fdtd"):
    return sax_models_removed("bend_s")


# class bend_s:

#     def __init__(self, config=None):
#         default_config = {'wl0': 1.55,
#                         #   'pol': 'TE',
#                           'size_xy':(10, 4)}
#         if config is None:
#             config = default_config
#         else:
#             config = {**default_config, **config}

#         self.config = config
#         self.component = None
#         self.model = None

#         _ = self.config_to_geometry()
#         self.component = self.get_component()
#         self.model = {'bezier': self.get_model_ana}

#     def config_to_geometry(self):
#         self.wl0 = self.config['wl0']
#         # self.pol = self.config['pol']
#         self.size_xy = self.config['size_xy']
#         return None


if __name__ == "__main__":
    c = _bend_s()
    print(c.get_netlist())
