"""Independent exact reverse-covector check of the fixed 457..575 interval.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
No source evaluator or matrix arithmetic is imported from either predecessor.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys


SOURCE_SHA = "c5b6c5236462ae84e5431a791a2f8ce795774342f13e11c4af35689092a8af30"
ORIGINAL_BLOB = "5a71ca9f80ced1aeb8a68e97516cab52eb72a52a"
NEW_BLOB = "cf55f4271009a06ad192a070d330a4466b6d44fa"
ROWS = (0, 1, 19)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def pullback(events, output, q, roles):
    """Apply the transpose of each literal map in reverse chronological order.

    LAMBDA_s=(1+s*i)/2 + (1-s*i)*q^2/2 specializes to 1 at either sign.
    The only IDLE_ONE in the interval is D9, specialized to 1. There is
    no assumption on the other D_j and none occurs in this interval.
    """
    require(q in (-1, 1), "two legal sign specializations")
    cov = [Fraction(0) for _ in range(roles)]
    cov[output] = Fraction(1)
    for row in reversed(events):
        require(row[0] == "A", "fixed interval has only A operations")
        op, d = row[1:3]
        if op in ("ADD", "QUERY"):
            s, c = row[3:5]
            c = Fraction(c) if op == "ADD" else Fraction(q if c % 2 else 1)
            old_dest = cov[d]
            cov[s] += c * old_dest
        elif op == "SCALE":
            cov[d] *= Fraction(row[3])
        elif op == "QSELF":
            cov[d] *= q if row[3] % 2 else 1
        elif op == "SWAP":
            s = row[3]
            cov[d], cov[s] = cov[s], cov[d]
        elif op == "LAMBDA":
            require(row[3] in (-1, 1), "literal lambda sign")
        elif op == "IDLE_ONE":
            require(row[3] == [9], "only D9 is specialized")
        else:
            raise ValueError("unexpected interval operation " + op)
    return cov


def determinant3(m):
    a, b, c = m
    return (a[0]*(b[1]*c[2]-b[2]*c[1])
            - a[1]*(b[0]*c[2]-b[2]*c[0])
            + a[2]*(b[0]*c[1]-b[1]*c[0]))


def response(events, roles):
    plus = [pullback(events, row, 1, roles) for row in ROWS]
    minus = [pullback(events, row, -1, roles) for row in ROWS]
    delta = [[a-b for a,b in zip(p,m)] for p,m in zip(plus,minus)]
    minor = [[row[col] for col in ROWS] for row in delta]
    return plus, minus, delta, minor


def sparse(cov):
    return {str(i): str(x) for i,x in enumerate(cov) if x}


def main(folder):
    old_bytes = (folder/"data/caller_efree.json").read_bytes()
    new_bytes = (folder/"QUERY-ONLY-CALLER.json").read_bytes()
    require(sha256(old_bytes).hexdigest() == SOURCE_SHA, "exact original SHA256")
    require(git_blob(old_bytes) == ORIGINAL_BLOB, "exact original Git blob")
    require(git_blob(new_bytes) == NEW_BLOB, "exact public attainment Git blob")
    old = json.loads(old_bytes); new = json.loads(new_bytes)
    require(old["roles"] == new["roles"] == 76, "complete public role inventory")
    before = old["events"][457:576]
    require(len(before) == 119 and before[0] == ["A", "QSELF", 0, -1]
            and before[-1] == ["A", "QSELF", 19, -1], "original exact endpoints")
    after = new["events"][457:680]
    require(len(after) == 223 and old["events"][:457] == new["events"][:457]
            and old["events"][576:] == new["events"][680:], "same replacement boundaries")
    require(Counter(e[1] for e in after)["QUERY"] == 3
            and not any(e[1] == "QSELF" for e in after), "attainment uses three literal queries")
    plus, minus, delta, minor = response(before, 76)
    require(minor == [[-2,-4,0],[0,-2,0],[0,0,2]] and determinant3(minor) == 8,
            "nonzero actual response minor")
    new_plus, new_minus, _, new_minor = response(after, 76)
    require((plus, minus, minor) == (new_plus, new_minus, new_minor),
            "all six complete covectors agree with the public attainment")
    controls = []
    for label, word, charged in (("original", before, ("QSELF","QUERY")),
                                 ("attainment", after, ("QUERY",))):
        for index,row in enumerate(word):
            if row[1] in charged:
                changed = word[:index]+word[index+1:]
                mutated_minor = response(changed, 76)[3]
                require(determinant3(mutated_minor) == 0, "deleted charged site loses rank-three witness")
                controls.append(dict(word=label, local_index=index, operation=row,
                                     minor=[[str(x) for x in r] for r in mutated_minor], determinant="0"))
    result = dict(
        source_sha256=SOURCE_SHA, source_git_blob=ORIGINAL_BLOB,
        attainment_git_blob=NEW_BLOB, interval_start=457, interval_stop_exclusive=576,
        replacement_stop_exclusive=680, outputs=list(ROWS), inputs=list(ROWS),
        specialization="q=+1 and q=-1, D9=1; all other D_j absent from interval",
        plus_covectors=[sparse(v) for v in plus], minus_covectors=[sparse(v) for v in minus],
        full_response_covectors=[sparse(v) for v in delta],
        minor=[[str(x) for x in row] for row in minor], determinant="8",
        original_opcodes=dict(Counter(e[1] for e in before)),
        attainment_opcodes=dict(Counter(e[1] for e in after)),
        all_six_attainment_covectors_match=True, deleted_query_controls=controls,
        scope="Exact reverse-covector source check, not a full formal replacement identity or physical admission.",
        credit="Separate shared-context AI review for @CubeJerry; no human or proof-kernel independence claimed.")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
