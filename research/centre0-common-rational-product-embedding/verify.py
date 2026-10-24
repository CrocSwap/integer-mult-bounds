"""Source-bound finite certificate; JoyboyBrian, Codex assistance, Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
import gzip, hashlib, json
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
NATIVE="research/native-involutive-dual/"
AUDIT="research/actual-centre0-source-audit/evidence/outputs/seven-mode-producer-feasibility-20261023/"
def need(ok,msg):
    if not ok: raise ValueError(msg)
def load():
    pins=json.loads((P/'SOURCES.json').read_text())
    for row in pins['files']:
        if row.get('usage')=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'], 'source hash: '+row['path'])
    r=[[Q(x) for x in row] for row in json.loads((ROOT/(NATIVE+'R.json')).read_bytes())]
    word=json.loads(gzip.decompress((ROOT/(NATIVE+'INVOLUTIVE-WORD.json.gz')).read_bytes()))
    audit=json.loads((ROOT/(AUDIT+'CORRECTED-DERIVATION.json')).read_bytes())
    return r,word,audit
def main():
    r,word,audit=load(); need(len(r)==8 and all(len(v)==112 for v in r),'R dimensions')
    j=word['selected_ports']; need(j==[0,7,20,23,86,93,108,111],'actual selected ports')
    p=[[r[k][i]/4 if i in j else Q(0) for k in range(8)] for i in range(112)]
    u=[[r[k][i]/4-12*p[i][k] for k in range(8)] for i in range(112)]
    for k in range(8):
        for l in range(8):
            need(sum(r[k][i]*r[l][i] for i in range(112))==56*(k==l),'RRt')
            need(sum(r[k][i]*p[i][l] for i in range(112))==(k==l),'RP')
            need(sum(r[k][i]*u[i][l] for i in range(112))==2*(k==l),'RU')
    g=[[Q(i==j)-sum(u[i][k]*r[k][j] for k in range(1,8)) for j in range(112)] for i in range(112)]
    for i in range(112):
        for j in range(112):
            need(Q(word['F'][i][j])==Q(i==j)-sum(u[i][k]*r[k][j] for k in range(8)), 'original F')
            need(g[i][j]==Q(audit['F_actual'][i][j]), 'published centre0 G')
    need(g[0][1]==Q(11,2) and g[1][0]==Q(-1,2),'nonzero transpose witness')
    receipt={'source_dimensions':[8,112], 'compared_entries':12544,
             'transpose_witness':['11/2','-1/2'], 'transpose_rank_upper':14,
             'minimum_allowed_N':128, 'minimum_nonzero_product_rank':64,
             'new_kappa':None, 'claim':'common Gaussian-rational record charts only'}
    want=json.loads((P/'RESULT.json').read_text())
    need(json.dumps(receipt,sort_keys=True)==json.dumps(want,sort_keys=True),'typed receipt')
    print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
