"""Replay the unchanged original CNF methods without NumPy or a SAT solver.

Only the two optional-library import nodes are removed from an in-memory AST.
The solver constructor is intercepted after it receives the complete formula.
No source file is edited. All original clause-construction methods execute.
"""
import ast
import hashlib
from pathlib import Path

import encoding

ROOT = Path(__file__).resolve().parent


class StopAfterEncoding(Exception):
    pass


class OrderedPattern(set):
    def __iter__(self):
        return iter(sorted(set.__iter__(self)))


def compare(dimension, expected_hash):
    source = ROOT/"vendor/pr620/minrank_sat.py"
    tree = ast.parse(source.read_text(), filename=str(source))
    body, removed = [], []
    for node in tree.body:
        if isinstance(node, ast.Import) and len(node.names) == 1 and node.names[0].name == "numpy" and node.names[0].asname == "np":
            removed.append("numpy")
        elif isinstance(node, ast.ImportFrom) and node.module == "pysat.solvers" and [(n.name,n.asname) for n in node.names] == [("Cadical153",None)]:
            removed.append("pysat.solvers.Cadical153")
        else:
            body.append(node)
    encoding.need(removed == ["numpy","pysat.solvers.Cadical153"], "original import contract")
    tree.body = body
    results = []

    def capture(bootstrap_with):
        digest = hashlib.sha256()
        for row in bootstrap_with:
            digest.update((" ".join(map(str,row))+" 0\n").encode("ascii"))
        encoding.need(digest.hexdigest() == expected_hash, "original CNF differs from new encoding")
        results.append({"dimension":dimension,"clauses":len(bootstrap_with),
                        "clause_payload_sha256":digest.hexdigest(),"exact_clause_sequence_equal":True})
        raise StopAfterEncoding

    namespace = {"np":None,"Cadical153":capture}
    exec(compile(tree,str(source),"exec"),namespace)
    rows,gram,live,baseline,pattern,clique,labels = encoding.geometry()
    try:
        namespace["solve_asym"](111,OrderedPattern(pattern),baseline,dimension,
                                "none" if dimension == 8 else "neB0",clique)
    except StopAfterEncoding:
        pass
    encoding.need(len(results) == 1, "original encoder interception failed")
    return results[0]
