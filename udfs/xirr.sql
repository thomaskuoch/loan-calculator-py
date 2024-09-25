create or replace function xirr(
    dates array,
    cashflows array
)
returns float
language python
runtime_version=3.9
handler='xirr'
packages = ('pyxirr==0.10.3')
as $$
from pyxirr import xirr as _xirr


def xirr(*args, **kwargs):
    return _xirr(*args, **kwargs)
$$;