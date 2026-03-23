"""This is a directional coupler with an Euler curvature. Typically used to design ring resonators.

---
Name: coupler_ring
Description: This is a directional coupler with an Euler curvature. Typically used to design ring resonators.
ports: 2x2
NodeLabels:
    - passive
    - 2x2
Bandwidth: 100 nm
Args:
    -gap: spacing between parallel coupled straight waveguides
    -radius: radius of the 90 degree bends
    -length_x: length of the parallel coupled straight waveguides 
"""

import gdsfactory as gf
from PhotonicsAI.KnowledgeBase.DesignLibrary import _directional_coupler, bend_euler, straight
from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import (
    sax_models_removed,
)

@gf.cell
def coupler_ring(
    gap: float = 0.2,
    radius: float = 10.0,
    length_x: float = 4,
    bend: gf.typings.ComponentSpec = "bend_euler",
    straight: gf.typings.ComponentSpec = "straight",
    cross_section: gf.typings.CrossSectionSpec = "strip",
) -> gf.Component:
    """This is a directional coupler with an Euler curvature. Typically used to design ring resonators"""
    # geometrical_params = get_params(settings)
    _args = locals()

    c = gf.Component()
    ref = c << gf.components.coupler_ring(**_args)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])

    c.flatten() 
    return c


def get_model(model="fdtd"):
    """Return placeholder models after SAX support removal."""
    return sax_models_removed("coupler_ring")


if __name__ == "__main__":
    c = gf.Component()
    ref = c << coupler_ring(radius=10)
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])

    print(c.get_netlist())
