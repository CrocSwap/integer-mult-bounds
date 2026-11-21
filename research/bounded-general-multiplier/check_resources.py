"""Independently check the low machine, stock cut, source pins and length controller."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from low_catalogue import low_directory, right_table, pivot_table
from resources import BIT_H, OLD_BIT_H, COMPLEX_H, OLD_COMPLEX_H, bill, group_size, exact_stock


def require(check, reason):
    if not check:
        raise ValueError(reason)


def test_low():
    from streaming_routes import regular
    directory = low_directory(2)
    require(len(directory) == group_size(2,3) == 48, "GL2 count")
    require(all((a*d-b*c) % 3 for a,b,c,d in directory), "Independent determinant")
    # Removing holes after only the first row of a column scale loses a genuine result.
    require(regular((1,1,1,2),2) and not regular((2,1,1,2),2) and regular((2,1,2,2),2),
            "Intermediate singular-matrix counterexample")
    words = [("swap",0,1,0),("scale",1,0,2),("add",0,1,1),("add",1,0,2)]
    for kind,i,j,value in words:
        mat = [[1,0],[0,1]]
        if kind == "swap":
            mat = [[0,1],[1,0]]
        elif kind == "scale":
            mat[i][i] = value
        else:
            mat[i][j] = value
        table = right_table(directory,2,(kind,i,j,value))
        for k, row in enumerate(directory):
            out = tuple(sum(row[a*2+t]*mat[t][b] for t in range(2)) % 3
                        for a,b in product(range(2), repeat=2))
            require(directory[table[k]] == out, "Bad full low right action")
    choices = list(pivot_table(directory,2,([0,1],[0,1])))
    for g,i in zip(directory,choices,strict=True):
        a,b,c,d = g
        determinant = (a*d-b*c) % 3
        require(((-b*c,a*d)[i]*pow(determinant,-1,3))%3 != 0, "Selected nonunit diagonal")
    for n in (1,2,3):
        q = 3
        for e in (1,3,10,37,200):
            r = exact_stock(n+1,4,q,e)
            w,depth = r["width"],r["depth"]
            require((w-1)**250 < e <= w**250 and
                    (n+1)**(depth-2)*w >= e, "Integer stock guard")
            require(r["stock"] == (4*group_size(n+1,q)*q**((n+1)**2*(w-1)))**depth,
                    "Stock dropped a high fibre")
    return len(directory),choices.count(1)


def check_shape():
    from multiply import geometry
    result = bill()
    z = result["square_first"]
    s,w,b = z["s"],z["width"],z["b"]
    require((6*b+1).bit_length() == s and geometry.number_of_axes(6*b,w-1) == 0
            and geometry.number_of_axes(6*b,w) == 1, "Controller binding")
    # Determine the best possible length in every previous s-plateau via bit lengths.
    for j in range(1,s+1):
        hi = min(((1<<j)-2)//6, b-1)
        lo = max(1,((1<<(j-1))+4)//6)
        if hi < lo:
            continue
        u = 65536*j**3
        require(hi < u or hi-u+3 < hi.bit_length(), "An earlier plateau opened")
    m,k = z["multiplier"],z["shift"]
    require(m == b and k+3 == w and b-1 == k + m.bit_length()-1, "Wrong first n")
    # With n=b*2**(w-3), 4n/b=2**(w-1). Adding one opens exactly one axis.
    require(Fraction(4*m,b)==4, "First boundary strictness")
    require(result["N_reduction_log2"] == [OLD_BIT_H-BIT_H,OLD_COMPLEX_H-COMPLEX_H], "Carrier")
    require(result["new_eager_setup_log2log2_upper"] < result["old_low_output_log2log2_floor"],
            "Eager cover upper/lower overlap")
    require(result["new_streamed_setup_log2_upper"].bit_length() == 63, "Streamed setup bound")
    return z


def check_pins():
    pins=json.loads((HERE/"SOURCES.json").read_text())
    for row in pins["retained_files"]:
        require(sha256((HERE/row["path"]).read_bytes()).hexdigest() == row["sha256"],row["path"])
    return len(pins["retained_files"])


if __name__ == "__main__":
    low,bad = test_low()
    z = check_shape()
    print("low_types",low,"alternate_low_types",bad,"first_n",z["multiplier"],"* 2^",z["shift"],"+ 1")
    print("source_files",check_pins())
    print("PASS_GENERAL_RESOURCES")
