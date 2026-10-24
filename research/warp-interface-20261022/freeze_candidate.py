"""Freeze discovery bytes and derive the actual emitted-word canonical record."""
from collections import Counter
from hashlib import sha256
import gzip,json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def main():
    names=['CANDIDATE.json','CANDIDATE-WORD.json.gz','free_warp_milp.py','warp_merge.py','free_warp_contacts.py']
    hashes={name:sha256((HERE/name).read_bytes()).hexdigest() for name in names}
    frozen=HERE/'DISCOVERY-FREEZE.json'
    if frozen.exists():
        if json.loads(frozen.read_text())['sha256']!=hashes:raise ValueError('Frozen discovery bytes changed')
    else:frozen.write_text(json.dumps({'status':'FROZEN_UNVERIFIED_CANDIDATE','sha256':hashes},indent=2,sort_keys=True)+'\n')
    data=json.loads(gzip.decompress((HERE/'CANDIDATE-WORD.json.gz').read_bytes()));choice=json.loads((HERE/'CANDIDATE.json').read_text());source=data['canonical']
    canonical={k:source[k] for k in ['frames','start','final','ports','h','v','warps']}
    for w in canonical['warps']:
        recipe=choice['warp_recipes'].get(str(w['op']))
        if recipe:
            if w['G_columns']!=recipe['G_columns']:raise ValueError('Actual new native G binding')
            w['from_frame'],w['to_frame']=recipe['input'],recipe['output']
    prof=Counter(e[5] for e in data['programs']['forward'] if e[0]=='climb');prof.update(e[4] for e in data['programs']['forward'] if e[0]=='center')
    canonical['local_profile']=dict(prof)
    canonical['warp_edges']=sorted({(1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]) for e in data['programs']['forward'] if e[0]=='warp'})
    payload={'canonical':canonical,'programs':data['programs'],'discovery_word_sha256':hashes['CANDIDATE-WORD.json.gz'],
             'scope':'Actual emitted word; obsolete source A/B/cleanup metadata deliberately omitted, not regenerated from old G signatures.'}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    (HERE/'ACTUAL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    (HERE/'ACTUAL-WORD-FREEZE.json').write_text(json.dumps({'status':'FROZEN_PENDING_NATIVE_PHASE_ADMISSION','canonical_payload_sha256':sha256(raw).hexdigest(),
        'compressed_sha256':sha256((HERE/'ACTUAL-WORD.json.gz').read_bytes()).hexdigest(),'discovery_sha256':hashes},indent=2,sort_keys=True)+'\n')
    print('FROZEN_ACTUAL_WORD',sha256(raw).hexdigest(),dict(prof))


if __name__=='__main__':main()
