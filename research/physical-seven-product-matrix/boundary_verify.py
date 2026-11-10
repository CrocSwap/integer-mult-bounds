"""Registered complete inherited caller and exact-kernel integration replay."""
from pathlib import Path
import importlib.util
import json
import sys
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
spec=importlib.util.spec_from_file_location('boundary_runtime_sources',P/'sources.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)

def main():
    pins=S.authenticated_inputs()
    sys.path[:0]=[str(ROOT/'research/physical-boundary-pages'),
                  str(ROOT/'research/physical-two-column-boundary-kernel')]
    S.load('boundary_fraction_oracle',ROOT/'research/physical-boundary-pages/verify.py')
    with S.physical_runtime():
        import boundary_checks
        cases=[boundary_checks.case(8,4,6),boundary_checks.case(1,1,1)]
    print(json.dumps(dict(status='PASS_FAST_BOUNDARY_CALLER',pins=pins,cases=cases),sort_keys=True,indent=2))
if __name__=='__main__':main()
