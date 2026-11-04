"""Actual private-copy changes, tested against specified semantic controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json,shutil,subprocess,sys

HERE=Path(__file__).resolve().parent
FAULTS=[
 ("settlement.py","best + int(not any(sums[mask]))","best + 1","partition backtracking"),
 ("settlement.py","field.mul[field.neg[a]][row[target]]","field.mul[a][row[target]]","settlement witness"),
 ("settlement.py","field.mul[field.neg[u[i]]][field.inv[u[root]]]","field.mul[u[i]][field.inv[u[root]]]","settlement witness"),
 ("settlement.py","values.append(tuple(field.neg[z] for z in target_value))","values.append(tuple(0 for z in target_value))","nonzero partition total"),
 ("settlement.py","len(active) - len(blocks)","len(active) - len(blocks) + 1","settlement witness"),
 ("algorithms.py","int(sums[state] == zero)","1","small field anchor"),
 ("algorithms.py","return pairs + min((a+2*b)//5,(3*a+b)//5)","return pairs + max((a+2*b)//5,(3*a+b)//5)","small field anchor"),
 ("monomial.py","mask != len(ways) - 1","mask != 0","monomial order anchor"),
 ("monomial.py","ways[mask] += ways[mask ^ bit]","ways[mask] += 2*ways[mask ^ bit]","monomial order anchor"),
 ("monomial.py","field.axpy(row, a, w)","field.axpy(row, 0, w)","parameter coverage"),
 ("monomial.py","len(values)*comb(n, plus)","n*comb(n, plus)","ternary scalar anchor"),
 ("settlement.py","abs(imbalance + 2)","abs(imbalance - 2)","ternary scalar anchor"),
 ("orbit_oracle.py","(1,f.mul[u][b],f.mul[u][w])","(1,b,w)","projective types"),
 ("orbit_oracle.py","return (0,f.mul[inv][b],f.mul[inv][w])","return (0,0,0)","projective types"),
 ("orbit_oracle.py","2**(m-counts[0])","2**m","free orbit weight"),
 ("literal.py","det = f.neg[det]","det = det","literal determinant sign"),
 ("families.py","target=2*r+n if upper else max(r,n)","target=r+n if upper else max(r,n)","envelope attainment"),
 ("families.py","else max(r,n)","else r+n","envelope attainment"),
 ("EXAMPLES.json",'"minimum": 3','"minimum": 2',"small word fixture anchors"),
 ("source/6710-PROOF.md","Counting common-image full guards with row dependencies","Changed precursor proof","retained source bytes"),
]


def run(root, optimized, expected):
    argv=[sys.executable,"-I",*(["-O"] if optimized else []),"-W","error","-B",str(root/"verify.py"),"--controls"]
    proc=subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding="utf8",timeout=25)
    if expected is None:
        if proc.returncode or json.loads(proc.stdout)["status"]!="PASS_SETTLEMENT_CONTROLS":
            raise ValueError("unmodified control: "+proc.stderr[-400:])
    elif not proc.returncode or ("ValueError: "+expected) not in proc.stderr:
        raise ValueError(f"wrong rejection for {expected}: {proc.returncode} {proc.stderr[-600:]}")


def main():
    with TemporaryDirectory(prefix="guard-settlement-faults-") as tmp:
        root=Path(tmp)/"package"
        shutil.copytree(HERE,root,copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        for optimized in (False,True):
            run(root,optimized,None)
        for name,old,new,expected in FAULTS:
            f=root/name
            data=f.read_bytes()
            if data.count(old.encode())!=1:
                raise ValueError("fault site not unique: "+old)
            f.write_bytes(data.replace(old.encode(),new.encode()))
            for optimized in (False,True):
                run(root,optimized,expected)
            f.write_bytes(data)
        for optimized in (False,True):
            run(root,optimized,None)
    print(json.dumps(dict(status="PASS_SETTLEMENT_MUTATIONS",faults=len(FAULTS),
                          rejections=2*len(FAULTS),private_controls=4)))


if __name__=="__main__":
    main()
