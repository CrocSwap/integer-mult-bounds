"""A rank-one length certificate for the #7000/#7004 caller's two sign branches."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import json

root=Path(__file__).resolve().parent
p=root/"PR7000-CALLER.json"
caller=json.loads(p.read_bytes())
code=(root/"jclib_6936.py").read_text()
ns={"__file__":str(root/"jclib_6936.py")}
exec(code[:code.index("CONST =")]+code[code.index("PM ="):code.index("# ---------------------------------------------------------------- own resynthesis")],ns)
prime=ns["PM"]
stages=caller["stages"]
variables={j:1 for j in range(1,stages+1)}
for sign in (1,prime-1):
    matrix=ns["replay_matrix"](caller,sign,variables)
    assert all(value==(sign if i==j else 0) for i,row in enumerate(matrix) for j,value in enumerate(row))

result={}
for tag,typ in caller["types"].items():
    n=typ["roles"]
    assert all(row[0]%2==1 for row in typ["diagonal"])
    native=sum(e[0]=="J" for e in caller["events"])
    query=sum(e[0]==tag and e[1]=="QUERY" for e in caller["events"])
    minimum=n+1-2*native
    assert minimum==3 and query==4
    result[tag]={"roles":n,"ports":len(typ["ports"]),"native_calls":native,"current_queries":query,
                 "minimum_queries_with_current_HOST_factorization":minimum,
                 "maximum_removed_queries":query-minimum}
price=json.loads((root/"PR7004-QUERY-FAMILY-TARGET-PRICE.json").read_text())
for k,rows in price["target_prices"].items():
    m=F(rows["complex"]["signed_moment"][1])
    maximum=sum(r["ports"]*r["maximum_removed_queries"] for r in result.values())
    assert m+maximum<0
    print(k,"optimistic margin after both removable query slots",float(m+maximum))
with (root/"PR7000-QUERY-COUNT-SIGN-LOWER-BOUND.json").open("x") as out:
    json.dump({"source_sha256":sha256(p.read_bytes()).hexdigest(),"types":result,
               "proof":[
                   "Specialize D_j=1 and compare the complete q=-1 map to the q=1 map. Both targets are scalar signs on all 38 roles, so their relative map is -I.",
                   "Ordinary ADD, SWAP, SCALE and LAMBDA events agree between the two signs. Each QUERY shear changes its coefficient sign; its relative factor is a rank-one transvection.",
                   "At a J event each branch consists of two elementary sign-sensitive shears and sign-independent D_j factors. Factoring the two signed full products by telescoping yields a product of conjugates of these elementary relative factors.",
                   "A product of rank-one transvections giving -I in dimension n needs at least n+1 factors: rank(M-I) forces at least n independent directions, and with exactly n the first updated row in that basis keeps diagonal coefficient +1 to the end.",
                   "Therefore each branch needs at least 39 sign-sensitive transvections. With 18 native events contributing at most two each, at least three QUERY events remain per branch."
               ],
               "scope":"Fixed 38-role targets and native factorization, with even ordinary operators. New native macros, extra degrees of freedom, changed targets or further physical relations may fall outside the bound."},out,indent=2)
print("PASS_7000_SIGN_QUERY_FLOOR",result)
