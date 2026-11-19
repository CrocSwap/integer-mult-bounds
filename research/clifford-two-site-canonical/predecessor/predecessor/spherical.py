"""Independent polar-graph verification of the canonical answer on repeated coordinates."""
from fractions import Fraction
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def spherical_solution():
    rows = json.loads((HERE/"source"/"width13-spectrum.json").read_text())["rows"]
    shell_sizes = [1]
    down = [2**i-1 for i in range(5)]
    up = [2*(16-2**i) for i in range(5)]
    stay = [30-a-b for a,b in zip(up,down,strict=True)]
    for i in range(4):
        shell_sizes.append(shell_sizes[-1]*up[i]//down[i+1])
    size = sum(shell_sizes)
    if shell_sizes != [1,30,280,960,1024]:
        raise ValueError("Incorrect polar-graph shells")
    rhs = [Fraction(16,4**13)*Fraction(-1,64)**i for i in range(5)]
    answer = [Fraction(0)]*5
    eigensystem = []
    for theta in [30,13,3,-5,-15]:
        u = [Fraction(1)]
        for i in range(4):
            prev = down[i]*u[i-1] if i else 0
            u.append(((theta-stay[i])*u[i]-prev)/up[i])
        if down[-1]*u[-2]+stay[-1]*u[-1] != theta*u[-1]:
            raise ValueError("Incorrect radial eigenvector")
        degree = Fraction(size,sum(k*x*x for k,x in zip(shell_sizes,u,strict=True)))
        matching = [Fraction(*row["eigenvalue"]) for row in rows if row["quotient_degree"]==degree]
        if len(matching) != 1:
            raise ValueError(("Nonunique quotient representation",degree))
        scalar = matching[0]
        coeff = degree/size*sum(k*x*y for k,x,y in zip(shell_sizes,rhs,u,strict=True))
        for i in range(5):
            answer[i] += coeff*u[i]/scalar
        eigensystem.append((theta,int(degree),scalar,tuple(u)))
    if sum(d for _,d,_,_ in eigensystem)!=size or any(v==0 for v in answer):
        raise ValueError("Radial decomposition or unexpectedly empty shell")
    mass = Fraction(20643840,16)*sum(k*x*y for k,x,y in zip(shell_sizes,answer,rhs,strict=True))
    if not 0 < mass < 1:
        raise ValueError("Repeated coordinate projection must be proper and nonzero")
    return tuple(answer),mass,eigensystem



def compare():
    from canonical import profile, radial_matrix
    weights, mass, eigensystem = spherical_solution()
    if tuple(a/16 for a in weights) != profile():
        raise ValueError("Independent canonical coefficient profiles disagree")
    if mass != Fraction(478566778595,5856573836677349376):
        raise ValueError("Projection mass mismatch")
    matrix = radial_matrix()
    for theta,degree,scalar,u in eigensystem:
        result = [sum(x*y for x,y in zip(row,u,strict=True)) for row in matrix]
        if result != [scalar*v for v in u]:
            raise ValueError(("Geometric and character Gram actions disagree",theta,degree))
    print("PASS all five radial eigenspaces, canonical profile, exact projection mass",mass)


if __name__ == "__main__":
    compare()
