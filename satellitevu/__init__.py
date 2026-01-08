from .auth import Auth
from .client import Client

import warnings

warnings.warn(
    "The 'satellitevu' package is deprecated and will no longer be maintained. "
    "Please migrate to 'satvu-api-sdk' instead. "
    "See https://github.com/SatelliteVu/satvu-api-sdk.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["Auth", "Client"]
