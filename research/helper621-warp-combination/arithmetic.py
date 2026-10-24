"""Recompute the helper621 complete arithmetic certificate; read-only by default.

Reuses the attributed PR4610 arithmetic engine, with its path and compiler-gap adjustments
recorded in VENDOR.json. Apache-2.0. Substantial OpenAI assistance.
"""
from pathlib import Path
from fractions import Fraction
import argparse,gzip,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PAID={'1':2202,'2':414,'3':505,'4':134,'5':36,'8':8}
HELPERS={'4':28,'7':8,'8':47,'9':325}
HEAD='4b4c75bc0fd64d3eee54029e8d2fab834251fca6'
def need(ok,message):
    if not ok:raise ValueError(message)
def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_hash(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run(native):
    # Match the JSON receipt representation for direct calls from verify_native.
    native=json.loads(json.dumps(native))
    need(native.get('status')=='PASS_HELPER621_NATIVE_AND_ABSOLUTE_PHASE','Fresh native and absolute-phase certificate required')
    need(native.get('predecessor_head')==HEAD,'Predecessor head mismatch')
    need(native['paid']==PAID and native['helpers']==HELPERS,'Changed complete paid/helper profile')
    need(set(native['native'])=={'forward','backward'},'Both native directions required')
    for direction,allowance,prefix in [('forward',158120,'457'),('backward',158168,'169')]:
        rec=native['native'][direction]
        need(rec['paid_profile']==PAID and rec['independent_persistent_columns']==632,'Direction profile and independent inputs')
        need(rec['scalar_frames_checked'] and rec['arbitrary_owned_C0_cleared'],'Scalar frames and owned restoration')
        need(rec['real_scalar_allowance']==allowance and rec['max_formal_prefix_l1']==prefix,'Fresh scalar prefix allowance')
        need(rec['max_denominator']==({'forward':32,'backward':64}[direction]),'Fresh dyadic coefficient denominator bound')
        need(rec['second_literal']['independent_borrowed_input_fields']==632,'Second independent literal replay')
    for relative,expected in read(HERE/'DEPENDENCIES.json').items():
        path=ROOT/relative
        need(path.resolve().is_relative_to(ROOT) and digest(path)==expected,'Inherited arithmetic dependency pin: '+relative)
    vendor=HERE/'vendor/price_profile_4610.py';pin=read(HERE/'VENDOR.json')
    need(pin['predecessor_head']==HEAD and digest(vendor)==pin['vendored_sha256'],'Vendored arithmetic source pin')
    spec=importlib.util.spec_from_file_location('helper621_inherited_arithmetic',vendor)
    engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
    result=engine.run(native,Fraction('.003021569'))
    need(result['kappa']=='3021569/1000000000','Requested whole saving')
    need(result['local_paid']==PAID and result['local_helpers']==HELPERS,'Arithmetic input binding')
    need(result['rank_mass_surplus']==752 and result['productive_fields']==10928 and result['paid_calls']==64422,'Full controller inventory')
    result['gain_over_PR4610']=str(Fraction('.003021569')-Fraction('.00302152'))
    result['native_data_sha256']=canonical_hash(native)
    dependencies=['research/fresh-helper-boundary/native.py', 'research/higher-moment-strictification/verify.py', 'research/joint-helper-lattice/CONTROLLER.json', 'research/joint-helper-lattice/native_joint.py', 'research/joint-helper-lattice/verify.py', 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference/joint_pair_dag.py', 'research/kappa-rebuild/architecture/mixed_target_probe.py', 'research/kappa-rebuild/bit/complex_controller_factor.py', 'research/kappa-rebuild/bit/mixed_productive_bit.py', 'research/kappa-rebuild/complex/full-identity-certificates/RESULT.json', 'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'research/query-thinned-controllers/RESULT.json', 'research/query-thinned-controllers/controller.py']
    paths={Path(__file__).resolve(),vendor,*(ROOT/path for path in dependencies)}
    result['source_sha256']={path.relative_to(ROOT).as_posix():digest(path) for path in sorted(paths)}
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--native',type=Path,default=HERE/'NATIVE-RESULT.json.gz');parser.add_argument('--out',type=Path,default=HERE/'ARITHMETIC.json');parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run(read(args.native))
    if args.write:args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(read(args.out)==result,'Recomputed arithmetic differs from frozen receipt; no files were changed')
    print(json.dumps({k:result[k] for k in ('status','kappa','gain_over_PR4610','raw_root_interval','paid_calls')},indent=2))
