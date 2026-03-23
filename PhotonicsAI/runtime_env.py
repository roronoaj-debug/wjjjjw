"""Runtime environment helpers for portable local execution."""

import os


def configure_ca_certificates() -> None:
    """Populate CA-related environment variables when certifi is available."""
    try:
        import certifi
        ca_bundle = certifi.where()
    except Exception:
        return

    if not ca_bundle:
        return

    os.environ.setdefault("SSL_CERT_FILE", ca_bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)
    os.environ.setdefault("GIT_SSL_CAINFO", ca_bundle)