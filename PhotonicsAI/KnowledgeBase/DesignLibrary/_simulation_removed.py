"""Helpers for legacy simulation hooks removed from the runtime."""


def sax_models_removed(component_name: str) -> dict:
    """Return a placeholder model map for components whose SAX models were removed."""

    def _removed_model(*args, **kwargs):
        raise RuntimeError(
            f"SAX simulation support has been removed for {component_name}."
        )

    return {component_name: _removed_model}