"""This is a grating coupler used for I/O to the PIC.

---
Name: _gc
Description: This is a grating coupler used for I/O to the PIC.
ports: 1x0
NodeLabels:
    - passive
    - 1x1
Bandwidth: 100 nm
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, LayerSpec

from PhotonicsAI.KnowledgeBase.DesignLibrary._simulation_removed import \
    sax_models_removed


@gf.cell
def _gc(
    polarization: str = "te",
    taper_length: float = 16.6,
    taper_angle: float = 40.0,
    wavelength: float = 1.554,
    fiber_angle: float = 15.0,
    grating_line_width: float = 0.343,
    neff: float = 2.638,
    nclad: float = 1.443,
    n_periods: int = 30,
    big_last_tooth: bool = False,
    layer_slab: LayerSpec | None = "SLAB90",
    slab_xmin: float = -1.0,
    slab_offset: float = 2.0,
    spiked: bool = True,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    c = gf.Component()

    xs_wg = gf.cross_section.cross_section(width=0.4, offset=0, layer=(1, 0))
    coupler = c << gf.components.grating_coupler_elliptical_uniform(
        n_periods=32,
        period=0.63,
        fill_factor=0.5,
        taper_length=18.427,
        taper_angle=52,
        spiked=False,
        cross_section=xs_wg,
        layer_slab=False,
    )
    # coupler.drotate(90)

    taper_wg = c << gf.components.taper(length=12, width1=0.5, width2=0.4)

    slab90 = c << gf.components.rectangle(size=(33.587, 43.15), layer=(3, 0))
    slab90.dmove((10.158, -21.575))
    # slab90.drotate(90)

    taper_wg.connect("o2", coupler.ports["o1"])

    c.add_port("o1", port=taper_wg.ports["o1"])

    c.flatten()
    return c


def get_model(model="fdtd"):
    return sax_models_removed("_gc")


if __name__ == "__main__":
    from pprint import pprint

    c = gf.Component()

    ref1 = c << _gc()
    # ref1.dmirror()

    pprint(c.get_netlist())
