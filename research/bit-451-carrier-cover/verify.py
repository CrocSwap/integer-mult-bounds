# SPDX-License-Identifier: Apache-2.0
"""Rebuild the credited binary supplier, sharpen its cover proof and run the rational consumer."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ARCHIVE = "5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3"
BASE_RECEIPT = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
BRIDGE = "inputs/framework/research/p104-shared-native-helper-splits/retained/compiler/bit-audit/retained/DELAYED-COVER-BRIDGE.md"
CAP = "0.00387992804364799"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check(condition, why):
    if not condition:
        raise ValueError(why)


def extract(work):
    archive = HERE / "source7863.tar.gz"
    check(digest(archive) == ARCHIVE, "predecessor archive")
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        check(len({m.name for m in members}) == len(members), "duplicate archive path")
        check(sum(m.size for m in members) < 2**29, "archive size")
        for m in members:
            p = PurePosixPath(m.name)
            check(not p.is_absolute() and '..' not in p.parts and p.parts[0] == "package-sanitized"
                  and (m.isdir() or m.isfile()), "unexpected archive member")
        tar.extractall(work, filter="data")
    root = work / "package-sanitized"
    seen = set()
    for line in (root / "SHA256SUMS").read_text().splitlines():
        checksum, key = line.split("  ", 1)
        check(key not in seen and digest(root / key) == checksum, key)
        seen.add(key)
    check(len(seen) == 202, "predecessor file census")
    return root


def supplier(base):
    check(base["raw_crossing"] == ["0.003879928046154","0.003879928046155"], "native raw interval")
    H = base["uniform"]["H"]
    old = base["cover_and_stock"]
    check(H == 1202400000000000 and base["uniform"]["N"] == f"2^{H}", "physical carrier")
    check(old["q_condition"] == "odd prime q > 2^52*N^5 avoiding frozen finite catalogue witnesses",
          "physical prime contract")
    check(base["native"]["native_calls"] == 36 and base["native"]["owned_nonzero_CLEAR"] == 3554
          and base["native"]["dual_nonzero_retirement"] == 3554, "signed binary program")
    bad = Q(old["bad_surcharge_upper"])
    check(bad == Q(64,2**52), "full bad-class bound")
    d = Q(1, H*2**44)
    # For x>0, exp(x)>1+x; ln(2)=integral_1^2 1/t dt>1/2.
    good_inverse_lower = 1 + H*d/2
    multiplier = (1+bad) / good_inverse_lower
    check(multiplier < 1 and 1+bad > 1, "strict complete covered moment and zero-loss control")
    uniform = Q(base["separation"]["trial"]) - Q(base["uniform"]["uniform_loss"])
    check(uniform - Q(old["loss"]) == Q(old["covered"]), "old cover control")
    covered = uniform-d
    previous = Q(old["seed"])
    rho = Q(old["rho"])
    stages = []
    for old_stage in old["stages"]:
        bound = (1-rho)*covered+rho*previous
        accepted = Q((bound*10**24).__floor__()-1,10**24)
        check(previous < accepted < bound < covered and accepted < rho < 1-accepted, "strict ordinary stage")
        check(accepted > Q(old_stage["claim"]), "old-stage control")
        stages.append(str(accepted))
        previous = accepted
    check(len(stages) == 7 and previous > Q(CAP), "final installed cap")
    old_limit = Q(base["raw_crossing"][1])-Q(base["uniform"]["uniform_loss"])-Q(old["loss"])
    return dict(loss=str(d), complete_multiplier_upper=str(multiplier), covered=str(covered),
                stages=stages,installed=CAP, old_fixed_loss_ceiling=str(old_limit))


COVER_HASHES = {
    "APPLICATION.json": "e0a28d730e5a63070221a170c3e5e10abdf4ed552d67fbd47d1f4ec157b736ad",
    "AUDIT.json": "51963b588680e3150b97b156a461c9002368c40752b73bc4a6b03f94aca97c0b",
}


def consumer(root, result, component, *, cap=CAP, expected_claim="0.00387992804356",
             expected_hashes=COVER_HASHES):
    check(component["installed"] == cap, "supplier-consumer binding")
    source = root/"source-7830/review/independent.py"
    check(digest(source) == "a2366b60cb4cd535fbcbce2a834cdf2ed4b9daba3e7025c7403e6abcd598a7ca", "consumer verifier")
    spec = importlib.util.spec_from_file_location("credited_review",source)
    r = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = r
    spec.loader.exec_module(r)
    inputs = root/"inputs"
    check(r.authenticate(inputs,False) == (20,127), "consumer input lock")
    r.ORDINARY = component["installed"]
    result.mkdir()
    app,audit = r.replay_application(inputs,result)
    r.compare_fixed_application(inputs,app,audit)
    r.rational_orientations(inputs,app)
    paid,target,_ = r.native_rational(app)
    r.directed_invoice(paid,target,r.RATIONAL_BRACKET,r.TARGET)
    claim = app["application"]["claim"]
    tested = audit["outer"]["finite_compiler"]["tested"]
    checks = audit["outer"]["outer_checks"]
    r.rational_outer(app,audit,paid,target,Q(cap),dict(claim=claim,sharp_outer=checks))
    check((checks["strict_count"],checks["functional_count"]) == (54,4), "complete outer conditions")
    before = json.loads((root/"consumer-replay/CONSUMER.json").read_bytes())
    check(app["premises"] == before["premises"] == audit["premises"], "premises and consumer")
    check(Q(claim) > Q(component["old_fixed_loss_ceiling"]), "separation from old finite envelope")
    check(Q(tested)-Q(claim)==Q(7,10**14) and Q(tested)<Q(cap), "strict consumer allowance")
    check(Q(before["claim"]) == Q("0.00387992804346") and Q(claim) == Q(expected_claim),
          "benchmark and new claim")
    for name, expected in expected_hashes.items():
        check(digest(result/name) == expected,"independent replay mismatch: "+name)
    damaged = paid.copy()
    damaged[1] += 1
    controls = [
        (lambda: r.directed_invoice(damaged,target,r.RATIONAL_BRACKET,r.TARGET),
         "directed signs at raw crossing endpoints"),
        (lambda: r.outer_margins(Q(claim),Q(1,10**14),Q(claim)+Q(4,10**14)-Q(1,10**15)),
         "all strict and functional outer conditions"),
    ]
    for run,expected_error in controls:
        try:
            run()
        except ValueError as error:
            check(str(error)==expected_error,"unexpected control failure")
        else:
            raise ValueError("corruption accepted")
    hashes = {path.relative_to(result).as_posix(): digest(path)
              for path in result.rglob("*") if path.is_file()}
    binding = dict(cap=cap,claim=claim,tested=tested,output_sha256=hashes)
    (result/"receipt.json").write_text(json.dumps(binding,sort_keys=True)+"\n")
    return dict(claim=claim,tested=tested,delta=str(Q(claim)-Q(before["claim"])),
                percent_gain=str(100*(Q(claim)-Q(before["claim"]))/Q(before["claim"])))


def main():
    check(sys.version_info[:2]==(3,12) and __debug__, "use CPython 3.12 with assertions")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[name]="1"
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        root = extract(work)
        check(digest(root/BRIDGE)=="9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443",
              "delayed-cover proof pin")
        subprocess.run([sys.executable,"-IB",root/"replay_451.py"],cwd=root,check=True)
        rebuilt = root/"replay/BIT-451.json"
        check(digest(rebuilt)==BASE_RECEIPT==digest(root/"BIT-451.json"),"complete predecessor control")
        component = supplier(json.loads(rebuilt.read_bytes()))
        print("PASS_ORIGINAL_451_SUPPLIER_AND_ACTUAL_CARRIER_COVER",flush=True)
        out = consumer(root,work/"candidate",component)
        replay = work/"proof.json"
        subprocess.run([sys.executable,"-IB",HERE/"audit.py",root,replay,"--consumer",work/"candidate"],check=True)
        independent = json.loads(replay.read_bytes())
        independent.pop("seconds")
        check(independent == json.loads((HERE/"RESULT.json").read_bytes()),"independent complete receipt")
        print("PASS_COMPLETE_SIGNED_APPLICATION",json.dumps(out,sort_keys=True),flush=True)


if __name__ == "__main__":
    main()
