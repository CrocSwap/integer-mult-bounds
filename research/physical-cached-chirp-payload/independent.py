"""Source certificates and separately implemented half-angle/physical checks."""
from pathlib import Path
import importlib.util
import json
import sys
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent_chirp_loader',P/'sources.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)

def main():
    pins=S.authenticated_inputs()
    C=S.load('independent_certified_chirp_tables',P/'chirp_tables.py')
    checks=S.load('certified_chirp_source_checks',P/'source_checks.py')
    review=S.load('independent_chirp_source_review',P/'chirp_source_review.py')
    physical=S.load('independent_chirp_physical_review',P/'chirp_physical_review.py')
    source=checks.run(C,S.interval_source())
    separate=review.run(C,S.interval_source)
    bundle=C.prepare((8,4),(7,3),1,10,oracle=S.interval_source())
    with S.physical_runtime():actual=physical.run(bundle)
    print(json.dumps(dict(status='PASS_INDEPENDENT_CACHED_CHIRP',pins=pins,
                         source=source,separate_source=separate,physical=actual),
                     sort_keys=True,indent=2))
if __name__=='__main__':main()
