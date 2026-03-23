"""This is a multimode interferometer with two input and two output ports.

---
Name: mmi2x2
Description: A multimode interferometer with two input and two output ports.
ports: 2x2
NodeLabels:
    - passive
    - 2x2
Bandwidth: 50 nm
Args:
    -width: input and output straight width. Defaults to cross_section width.
    -width_taper: interface between input straights and mmi region.
    -length_taper: into the mmi region.
    -length_mmi: in x direction.
    -width_mmi: in y direction.
    -gap_mmi: gap between tapered wg.
"""

import gdsfactory as gf

# from PhotonicsAI.Photon.utils import validate_cell_settings
from gdsfactory.typings import CrossSectionSpec

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import sax_models_removed

# args = {
#     'functional': {
#         'wl0': {'default': 1.55, 'range': (1.0, 2.0)},
#         'coupling': {'default': 0.5, 'range': (0, 1)}
#     },
#     'geometrical': {
#         'length_taper': {'default': 10., 'range': (5.0, 15.0)},
#         'length_mmi':   {'default': 5.5, 'range': (5.0, 50.0)},
#         'width_mmi':    {'default': 2.5, 'range': (2.0, 6.0)},
#         'gap_mmi':      {'default': 0.25, 'range': (0.2, 0.3)},
#     }
# }


@gf.cell
def _mmi2x2(
    width: float | None = None,
    width_taper: float = 1.0,
    length_taper: float = 10.0,
    length_mmi: float = 5.5,
    width_mmi: float = 2.5,
    gap_mmi: float = 0.25,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    _args = locals()

    c = gf.Component()
    m = gf.components.mmi2x2(**_args)
    coupler_r = c << m

    c.add_port("o1", port=coupler_r.ports["o1"])
    c.add_port("o2", port=coupler_r.ports["o2"])
    c.add_port("o3", port=coupler_r.ports["o3"])
    c.add_port("o4", port=coupler_r.ports["o4"])

    c.flatten()
    return c


# def get_params(settings={}):
#     """
#     Generates the output configuration based on the settings.

#     Parameters:
#     settings (dict): A dictionary containing settings.

#     Returns:
#     dict: A dictionary containing the mapped geometrical parameters and direct output parameters.
#     """

#     validated_settings = validate_cell_settings(settings, args)

#     def wl_mapper(wl):
#         length_mmi = 20*wl + 2
#         return length_mmi

#     def coupling_mapper(coupling):
#         width_mmi = 2 + 2 * coupling
#         return width_mmi

#     output_params = {}

#     # handle all functional parameters first
#     # output_params['length_mmi'] = wl_mapper(validated_settings['functional']['wl0'])
#     # output_params['width_mmi'] = coupling_mapper(validated_settings['functional']['coupling'])

#     # Add remaining geometrical parameters
#     for arg in validated_settings['geometrical']:
#         if arg not in output_params:
#             output_params[arg] = validated_settings['geometrical'][arg]

#     return output_params


def get_model(model="fdtd"):
    return sax_models_removed("_mmi2x2")


if __name__ == "__main__":
    component = _mmi2x2(length_mmi=100)
    print(component.get_netlist())
