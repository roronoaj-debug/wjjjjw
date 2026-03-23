"""This is a multimode interferometer with one input and two output ports.

---
Name: mmi1x2
Description: >
    This multimode interferometer has one input and two output ports.
    It functions as a beamsplitter or power splitter, dividing the input equally between the two outputs.
    Each output receives half of the input power, ensuring balanced splitting.
ports: 1x2
NodeLabels:
    - passive
    - 1x2
Bandwidth: 50 nm
Args:
    -width: input and output straight width. Defaults to cross_section width.
    -width_taper: interface between input straights and mmi region.
    -length_taper: into the mmi region.
    -length_mmi: in x direction.
    -width_mmi: in y direction.
    -gap_mmi:  gap between tapered wg.
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import sax_models_removed
from PhotonicsAI.Photon.utils import get_file_path, model_from_npz


@gf.cell
def _mmi1x2(
    length_mmi: float = 12.8,
    width_mmi: float = 3.8,
    gap_mmi: float = 0.25,
    length_taper: float = 10.0,
    width_taper: float = 1.4,
) -> gf.Component:
    _args = locals()

    c = gf.Component()
    m = gf.components.mmi1x2(**_args)
    coupler_r = c << m
    c.add_port("o1", port=coupler_r.ports["o1"])
    c.add_port("o2", port=coupler_r.ports["o2"])
    c.add_port("o3", port=coupler_r.ports["o3"])
    c.flatten()
    return c


def get_model(model="fdtd"):
    return sax_models_removed("_mmi1x2")


# class mmi1x2:

#     def __init__(self, config=None):
#         default_config = {'wl0': 1.55,
#                         #   'pol':'TE',
#                           'coupling': 0.5}
#         if config is None:
#             config = default_config
#         else:
#             config = {**default_config, **config}

#         self.config = config
#         self.component = None
#         self.model = None

#         _ = self.config_to_geometry()
#         self.component = self.get_component()
#         self.model = {'mmi1x2': self.get_model_ana}

#     def config_to_geometry(self):
#         """
#         Provides mapping from design config to geometric settings of gdsfacotory component.
#         """
#         self.wl0 = self.config['wl0']
#         # self.pol = config['pol']
#         self.coupling = self.config['coupling']
#         x_to_y = lambda x: 20*x + 2 # dummy mapping
#         self.length = x_to_y(self.coupling)
#         return None

if __name__ == "__main__":
    component = _mmi1x2(width_mmi=10)
    print(component.get_netlist())
