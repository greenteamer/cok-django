"""
Template context processors for the whole site.
"""

from . import identity as site_identity


def identity(request):
    """Expose `config/identity.py` to every template as `identity`."""
    return {"identity": site_identity.as_dict()}
