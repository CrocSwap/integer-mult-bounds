from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "paid-controller"))
from portable import WORKBENCH, output_path, source_name
"""All-stage active-pressure obstruction for the rank1851 fullshell hybrid."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,hashlib
SOURCE=WORKBENCH / 'paid-controller/unfused/verify.py'
s=importlib.util.spec_from_file_location('unfused_bound',SOURCE);bound=importlib.util.module_from_spec(s);s.loader.exec_module(bound)
bound.c.FRONTIER=F(1612722852614221,10**18)
def main():
 result=bound.certify(30960,16,1851,0)
 try:bound.certify(30960,16,815,0)
 except ValueError as error:bound.c.require('Active climbs alone' in str(error),'Expected negative control')
 else:raise ValueError('The cheaper815-center control must not be rejected by this bound')
 out=dict(status='PASS_EXACT_ALL_ODD_STAGES',result=result,negative_control='Rank815 without added center cost is not rejected by this sufficient obstruction',source=dict(path=source_name(SOURCE),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()))
 output_path('continuation/endpoint-costs/HYBRID-BOUND.json').write_text(json.dumps(out,indent=2)+'\n')
 print(result['global_necessary_kappa_upper_bound_interval_scaled_1e18']);print('Lmin',result['first_odd_stage_with_positive_deficit'],'normalized active pressure',float(F(result['normalized_active_pressure_lower_bound_at_frontier'])),'delta',float(F(result['normalized_deficit_strict_upper_bound'])))
if __name__=='__main__':main()
