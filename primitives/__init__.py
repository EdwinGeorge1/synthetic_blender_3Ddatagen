# project-root/primitives/__init__.py

from .box      import BoxWrapper
from .cylinder import CylinderWrapper

_FACTORIES = {
    'box':      BoxWrapper,
    'cylinder': CylinderWrapper,
}

def get_wrapper(name: str):
    """
    Return an instance of the requested primitive wrapper.
    Raises ValueError if unknown.
    """
    try:
        return _FACTORIES[name]()
    except KeyError:
        raise ValueError(f"Unknown primitive: {name!r}")
