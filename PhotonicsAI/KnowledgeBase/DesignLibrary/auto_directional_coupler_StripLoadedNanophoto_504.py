
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_StripLoadedNanophoto_504(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Strip-Loaded Nanophotonic Interfaces for Resonant Coupling and Single-Photon Routing
    Source: https://arxiv.org/abs/2408.02372
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
