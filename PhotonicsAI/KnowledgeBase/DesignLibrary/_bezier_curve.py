"""This is a bend (or generally arc shaped) waveguide.

---
Name: bezier_curve
Description: |
    This is a bend (or generally arc shaped) waveguide.
    The function maps a radii and and an angle to a 4 control points that implements the Bezier Curve.
ports: 1x1
NodeLabels:
    - passive
    - 1x1
Bandwidth:
"""

import math

import gdsfactory as gf

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import \
    sax_models_removed


@gf.cell
def _bezier_curve(radius: float = 10, angle: float = 90) -> gf.Component:
    """This is a bezier curve.

    https://stackoverflow.com/questions/30277646/svg-convert-arcs-to-cubic-bezier
    """
    c = gf.Component()
    rad_angle = ((angle - 180) * math.pi) / 180

    x1 = radius
    y1 = 0

    x2 = radius
    y2 = radius * (4 / 3) * math.tan(rad_angle / 4)

    x3 = radius * (
        math.cos(rad_angle) + (4 / 3 * math.tan(rad_angle / 4) * math.sin(rad_angle))
    )
    y3 = radius * (
        math.sin(rad_angle) - (4 / 3 * math.tan(rad_angle / 4) * math.cos(rad_angle))
    )

    x4 = radius * math.cos(rad_angle)
    y4 = radius * math.sin(rad_angle)

    ref = c << gf.components.bezier(
        control_points=((x1, y1), (x2, y2), (x3, y3), (x4, y4)),
        npoints=201,
        with_manhattan_facing_angles=True,
    )

    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.flatten()
    return c


def get_model(model="fdtd"):
    return sax_models_removed("_bezier_curve")


# class bezier_curve:

#     def __init__(self, config=None):
#         default_config = {'radius': 10, 'angle': 90}
#         if config is None:
#             config = default_config
#         else:
#             config = {**default_config, **config}

#         self.config = config
#         self.component = None
#         self.model = None

#         _ = self.config_to_geometry()
#         self.component = self.get_component()
#         self.model = {'bezier_curve': self.get_model_ana}

#     def config_to_geometry(self):
#         # self.wl0 = self.config['wl0']
#         # self.pol = self.config['pol']
#         self.radius = self.config['radius']
#         self.angle = self.config['angle']
#         return None


if __name__ == "__main__":
    c = _bezier_curve(radius=10, angle=90)

    print(c.get_netlist())
