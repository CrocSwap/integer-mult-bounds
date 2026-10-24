"""Portable source-bound replay of the fixed-projection-height Clifford floor."""
from pathlib import Path
import gzip,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
raw=source.read_bytes()
if hashlib.sha256(raw).hexdigest()!='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05':
 raise ValueError('pinned compressed source hash')
payload=json.loads(gzip.decompress(raw))
ns={'__name__':'dimension_floor_checker','__file__':str(HERE/'check.py')}
exec(compile((HERE/'check.py').read_bytes(),str(HERE/'check.py'),'exec'),ns)
result=ns['verify'](payload)
result['negative_controls']=ns['controls'](payload)
cal={'__name__':'rank_calibration'}
exec(compile((HERE/'calibrate.py').read_bytes(),str(HERE/'calibrate.py'),'exec'),cal)
result['small_lagrangian_calibration']=cal['calibrate']()
paths={}
for direction,evidence in result['directions'].items():
 paths[direction]={key:evidence.pop(key) for key in ('paths','zero_entrance_helpers')}
path_raw=json.dumps(paths,sort_keys=True,separators=(',',':')).encode()
if path_raw!=gzip.decompress((HERE/'PATHS.json.gz').read_bytes()):
 raise ValueError('frozen path receipt differs from reconstructed source')
result['path_receipt_sha256']=hashlib.sha256(path_raw).hexdigest()
expected=json.loads((HERE/'RESULT.json').read_bytes())
# JSON round-trip normalizes integer histogram keys without changing evidence.
if json.loads(json.dumps(result))!=expected:raise ValueError('frozen result differs from reconstructed source evidence')
print('PASS_PRODUCTIVE_HELPER_DIMENSION_FLOOR: both orientations, 50 disjoint paid paths each, 358 rigid helpers, 18459 chart-pair calibrations, 8 rejected corruptions')
