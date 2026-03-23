"""This is a bend (or generally arc shaped) waveguide, with an Euler curvature.

---
Name: bend_euler
Description: This is a bend (or generally arc shaped) waveguide, with an Euler curvature.
ports: 1x1
NodeLabels:
    - passive
    - 1x1
Bandwidth: 100 nm
Args:
    -radius: in um. Defaults to cross_section_radius.
    -angle: total angle of the curve.
    -npoints: Number of points used per 360 degrees.
"""

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import sax_models_removed

# from PhotonicsAI.Photon.utils import validate_cell_settings

# args = {
#     'functional': {
#     },
#     'geometrical': {
#         'radius':   {'default': 10., 'range': (2.0, 200.0)},
#         'angle':    {'default': 90, 'range': (90, 180)},
#         'p':        {'default': 0.5, 'range': (0, 1)},
#     }
# }


@gf.cell
def bend_euler(
    radius: float = 10.0,
    angle: float = 90.0,
    p: float = 0.5,
    npoints: int = 500,
    width: float = 0.5,
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """This is a bend (or generally arc shaped) waveguide, with an Euler curvature."""
    # geometrical_params = get_params(settings)
    _args = locals().copy()

    c = gf.Component()
    ref = c << gf.components.bend_euler(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.info["radius"] = radius
    c.info["angle"] = angle
    c.info["width"] = width

    # c = c.flatten() # this gives an error!
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

#     output_params = {}

#     # Add remaining geometrical parameters
#     for arg in validated_settings['geometrical']:
#         if arg not in output_params:
#             output_params[arg] = validated_settings['geometrical'][arg]

#     return output_params


def get_model(model="fdtd"):
    """Return a placeholder now that SAX models were removed."""
    return sax_models_removed("bend_euler")


if __name__ == "__main__":
    component = bend_euler(radius=100)
    print(component.get_netlist())
