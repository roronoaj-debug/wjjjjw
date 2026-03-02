
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_CoherentTunnelingbyA_117(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Coherent Tunneling by Adiabatic Passage inSiliconNitride based Integrated Waveguide Structures
    Source: https://arxiv.org/abs/2512.09436
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
