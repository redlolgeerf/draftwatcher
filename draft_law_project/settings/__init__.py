from .base import *
try:
    from .local import *
    INSTALLED_APPS += LOCAL_APPS
except ImportError:
    pass
