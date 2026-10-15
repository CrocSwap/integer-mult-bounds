"""inventory of the package in $FILLPKG (default pkg): per-call width counts and paid profile"""
import os,json,collections
_pk=os.environ.get('FILLPKG') or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..')   # package root
_pv=json.load(open(os.path.join(_pk,'new/BORROW-PROVIDERS.json')))
_g=_pv['gauge44']
PER=dict(collections.Counter(_g['widths']));PAID={int(k):v for k,v in _g['actual_paid_profile'].items()}
