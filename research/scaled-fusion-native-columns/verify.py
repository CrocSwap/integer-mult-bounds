"""Compare full forward and inverse matrices without a Pauli shortcut."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from common import authenticate,need
from columns import circuit_column,closed_column,adjoint,normalize


def recipe_circuit(recipe):
    def monomial(r):
        need(len(r['matrix_rows']) == len(r['quadratic_rows']) == len(r['linear_Z4']) == 9,
             'Nine-bit monomial')
        return [['D',r['quadratic_rows'],r['linear_Z4']],['P',r['matrix_rows']],
                ['X',r['offset']],['phase',r['phase']]]
    rank = recipe['rank']
    need(type(rank) is int and 0 < rank <= 9,'Positive native rank')
    return monomial(recipe['right'])+[['C',1 << i,1] for i in range(rank)]+monomial(recipe['left'])


def digest(columns):
    # Include every zero position and the exact denominator in each column.
    h = sha256()
    for values,den in columns:
        h.update(json.dumps([den,[values.get(i,(0,0)) for i in range(512)]],separators=(',',':')).encode()+b'\n')
    return h.hexdigest()


def mismatch(circuit,expected,column):
    need(circuit_column(circuit,column) != expected[column],'Mutation must change a checked column')


def main():
    word,specs = authenticate()
    process = subprocess.run([sys.executable,'-I','-B',str(P/'produce.py')],capture_output=True,text=True,check=True)
    need(not process.stderr,'Clean source producer stderr')
    records = json.loads(process.stdout)
    if '--write' in sys.argv: (P/'RECIPES.json').write_text(json.dumps(records,indent=2,sort_keys=True)+'\n')
    else: need(records == json.loads((P/'RECIPES.json').read_text()),'Exact source recipes')
    need([(r['old'],r['new']) for r in records] == [(243,127),(240,127)],'Only the two new transports')
    receipts = [];controls = 0
    for record,item in zip(records,specs):
        a,b = record['old'],record['new']
        need(record['role'] == item['role'] and record['recipe']['rank'] == 5,'Source role and paid rank')
        circuit = recipe_circuit(record['recipe'])
        need(circuit == record['circuit'],'Literal compiled recipe')
        expected = [closed_column(word['frames'][a],word['frames'][b],j) for j in range(512)]
        actual = [circuit_column(circuit,j) for j in range(512)]
        need(actual == expected,'All exact forward columns including absolute phase')
        need(all(len(v) == 32 for v,d in expected),'Rank-five column supports')
        inverse = [dict() for _ in range(512)]
        common = max(d for v,d in expected)
        for column,(values,den) in enumerate(expected):
            for row,(u,v) in values.items(): inverse[row][column] = (u << (common-den),-v << (common-den))
        inverse = [normalize(v,common) for v in inverse]
        back = [circuit_column(adjoint(circuit),j) for j in range(512)]
        need(back == inverse,'All exact adjoint columns')
        bad = deepcopy(record['recipe']);bad['left']['phase'] = (bad['left']['phase']+1) % 4
        mismatch(recipe_circuit(bad),expected,0);controls += 1
        bad = deepcopy(record['recipe']);bad['rank'] = 4
        mismatch(recipe_circuit(bad),expected,0);controls += 1
        diagonal = [0]*9;diagonal[3] = 2
        bad = [['D',[0]*9,diagonal]]+circuit
        need(circuit_column(bad,0) == expected[0],'The nonzero-column fault evades column zero')
        mismatch(bad,expected,8);controls += 1
        mismatch(adjoint(circuit),expected,0);controls += 1
        receipts.append(dict(old=a,new=b,rank=5,forward_columns=512,inverse_columns=512,
                             forward_hash=digest(expected),inverse_hash=digest(inverse),
                             forward_nonzero_entries=sum(len(v) for v,d in expected),
                             denominators=sorted({d for v,d in expected})))
    result = dict(status='PASS_SCALED_FUSION_NATIVE_COLUMNS',maps=receipts,
                  exact_complex_positions=2*2*512*512,negative_controls=controls,
                  compiler_source_sha256=sha256((P/'inputs/clifford_exact.py').read_bytes()).hexdigest(),
                  scope='Two finite native matrices and their tensor implication; no whole caller admission or new kappa')
    if '--write' in sys.argv: (P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else: need(result == json.loads((P/'RESULT.json').read_text()),'Exact native audit receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__': main()
