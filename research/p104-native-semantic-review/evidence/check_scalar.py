"""Only the current native word through the selected6030 independent engine.

No historical suite, native compiler, caller, interval, or price run. The
retained Matarener interpreter retains its credit; this is its exact current
source-bound application. Charted rational rows are not an arbitrary width-one
operator-sum tensorization or a discharge of the framework assumptions.
"""
from pathlib import Path
from hashlib import sha256
from contextlib import redirect_stdout
from io import StringIO
import argparse
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('map_compare',HERE/'compare_maps.py')
B=importlib.util.module_from_spec(spec);sys.modules[spec.name]=B;spec.loader.exec_module(B)


def run():
    B.authenticate();w=B.read('inputs/CURRENT-WORD.json.gz');M=B.load('selected6030_scalar','scalar.py')
    with redirect_stdout(StringIO()):
        paid,helpers,spans,receipt=M.replay(w,'exact6702-current-only')
    bad=json.loads(json.dumps(w));bad['program'][0][3]='1/2'
    try:
        with redirect_stdout(StringIO()):M.replay(bad,'wrong_actual_first_compensation_sign')
    except ValueError as error:control=str(error)
    else:raise ValueError('actual compensation-sign fault accepted')
    return {'schema':'independent-current-native-scalar-application/1',
        'status':'PASS_CURRENT_NATIVE_ALL_SCALAR_ENDPOINTS_AND_OWNERSHIP',
        'source_word_sha256':sha256((HERE/'inputs/CURRENT-WORD.json.gz').read_bytes()).hexdigest(),
        'independent_engine_sha256':sha256((HERE/'vendor/scalar.py').read_bytes()).hexdigest(),
        'replay':receipt,'changed_compensation_sign_rejected':control,
        'all_current_endpoint_rows':w['public']+w['owned_fields'],
        'historical_words_replayed':0,
        'scope':'One complete current18577-event word only, via the exact independent engine used by6030 admission. No native/caller/compiler/price/history suite. Charted rational native identity and chronological ownership; global quantified framework assumptions and external scientific decision remain unchanged.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    r=run();raw=json.dumps(r,sort_keys=True,indent=2)+'\n';path=HERE/'SCALAR.json'
    if a.write:path.write_text(raw)
    else:B.need(path.read_text()==raw,'read-only scalar receipt')
    print(json.dumps({'status':r['status'],'endpoint_rows':r['all_current_endpoint_rows'],
                      'events':r['replay']['events']},sort_keys=True))
