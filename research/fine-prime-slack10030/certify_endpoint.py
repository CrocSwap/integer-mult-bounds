"""Bind the independent endpoint certificate to the unchanged native supplier."""
import json,sys,hashlib
from pathlib import Path
from fractions import Fraction as Q
from moment_interval import v,src,moment,BITS
P=Path(__file__).resolve().parent
source=json.loads((P/'inputs/SOURCE-SPEC.json').read_text())
spec=json.loads((P/'inputs/SPEC.json').read_text())
assert {k:x for k,x in source.items() if k!='expected'}=={k:x for k,x in spec.items() if k!='expected'}
assert {k:x for k,x in source['expected'].items() if k!='complex_lower'}=={k:x for k,x in spec['expected'].items() if k!='complex_lower'}
assert Q(spec['expected']['complex_lower'])==Q(src['complex_lower'])
assert source['expected']['global_profile']==src['global_profile']
assert source['expected']['live']==int(src['live'])
result=v.run()
assert result['status']=='PASS_T74_K554_ROOT_ENCLOSURE_INDEPENDENT'
result['status']='PASS_INDEPENDENT_ENDPOINT_BRACKET_AND_BINDING'
result['source_spec_sha256']=hashlib.sha256((P/'inputs/SOURCE-SPEC.json').read_bytes()).hexdigest()
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
