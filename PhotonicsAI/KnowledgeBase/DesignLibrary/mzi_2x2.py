"""Alias wrapper: provide a short name `mzi_2x2` that maps to an existing implementation.

This avoids editing existing code paths that expect the short name in DOT labels.
"""
from PhotonicsAI.KnowledgeBase.DesignLibrary.mzi_2x2_pn_diode import (
    mzi_2x2_pn_diode,
    get_model as _get_model_target,
)


def mzi_2x2(*args, **kwargs):
    """Alias constructor that forwards to mzi_2x2_pn_diode."""
    return mzi_2x2_pn_diode(*args, **kwargs)


def get_model(model="fdtd"):
    """Delegate get_model to the underlying implementation so import_models works."""
    return _get_model_target(model=model)
