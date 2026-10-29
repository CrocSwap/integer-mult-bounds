# regenerate core{i}.cnf from cores_v.json + core{i}_frames.json; print sha256 (compare with data/cnf_sha256.txt)
import sys,os,json,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from core import build
from e8lib import frames
D=os.environ['DATA']; cores=json.load(open(D+'/cores_v.json'))
for i in [int(x) for x in sys.argv[1:]]:
    U=sorted(cores[i]); FRs=[tuple(F) for F in json.load(open(D+'/core%d_frames.json'%i))]
    build(U,FRs,frames(U),(0,2),'core%d.cnf'%i)
    print('core%d'%i,hashlib.sha256(open('core%d.cnf'%i,'rb').read()).hexdigest())
