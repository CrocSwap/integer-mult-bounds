"""Registered fixed-tape exact matrix product replay."""
from pathlib import Path
import importlib.util
import json
import sys
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('seven_product_runtime_sources',P/'sources.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)

def main():
    pins=S.authenticated_inputs()
    with S.physical_runtime():
        import kernel_checks
        result=kernel_checks.run()
    print(json.dumps(dict(status='PASS_PHYSICAL_SEVEN_PRODUCT',pins=pins,result=result),sort_keys=True,indent=2))
if __name__=='__main__':main()
