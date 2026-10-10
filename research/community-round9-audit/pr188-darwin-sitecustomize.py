"""Maintainer audit only: retain CPU limits, omit unsupported Darwin RLIMIT_AS."""
import resource, sys
_original_setrlimit = resource.setrlimit
def _portable_setrlimit(which, limits):
    if sys.platform == "darwin" and which == resource.RLIMIT_AS:
        print("MAINTAINER ADAPTER: RLIMIT_AS omitted on Darwin; no address-space cap claimed", file=sys.stderr)
        return
    return _original_setrlimit(which, limits)
resource.setrlimit = _portable_setrlimit
