"""Registered separate classical and physical kernel verification."""
from pathlib import Path
import importlib.util
import json
import sys
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent_matrix_runtime',P/'sources.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)

def main():
    pins=S.authenticated_inputs()
    oracle=S.load('independent_classical_matrix',P/'classical_oracle.py')
    verifier=S.load('independent_physical_matrix',P/'independent_physical.py')
    with S.physical_runtime():
        from seven_product import SevenProduct
        result=verifier.run(SevenProduct,oracle)
    print(json.dumps(dict(status='PASS_INDEPENDENT_SEVEN_PRODUCT',pins=pins,result=result),sort_keys=True,indent=2))
if __name__=='__main__':main()
