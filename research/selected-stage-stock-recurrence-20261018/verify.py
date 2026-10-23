#!/usr/bin/env python3
"""Check the selected stage-one stock-factorization source boundary."""
from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_SELECTED_STAGE_STOCK_RECURRENCE " + message)


def read(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def main() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        raw = read(row["path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input hash " + row["path"])

    tar_bytes = read("research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz")
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as archive:
        member = archive.extractfile("code/assemble.py")
        require(member is not None, "PR1087 assembler member")
        archived_assembler = member.read()
    selected_assembler = read("research/gauge44-slots-t16/code/assemble.py")
    require(archived_assembler == selected_assembler, "selected assembler equals pinned archive member")
    assembler = archived_assembler.decode("utf-8")
    require("check_moment('complex',H,73,owner['live'],b,5120,False)" in assembler,
            "selected complex producer width m=73")
    require("a=(1-s)*s+s*old" in assembler,
            "selected outer chain first-stage recurrence")
    require("for _ in range(7):" in assembler and "cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cut)))" in assembler,
            "selected native branch has seven recorded stages")

    assembly = json.loads(read("research/community-frontier1094-audit/ASSEMBLY.json"))
    record = json.loads(read("certificates/selected-result.json"))
    require(record["kappa"] == "836330098538459/500000000000000000", "selected kappa pin")
    require(assembly["kappa"] == record["kappa"], "selected assembly record")
    require(len(assembly["bootstrap"]) == 7, "selected native stage count")
    require(assembly["binding"] == "complex", "selected binding side")

    owner = json.loads(read("research/gauge44-slots-t16/evidence/audit/OWNERS-AND-PROFILE.json"))
    invoice = json.loads(read("research/gauge44-slots-t16/evidence/audit/PREFIX-AND-INVOICE.json"))
    audit_code = read("research/gauge44-slots-t16/code/audit_allcold.py").decode("utf-8")
    invoice_code = read("research/gauge44-slots-t16/code/invoice_allcold.py").decode("utf-8")
    require(owner["actual_73column_sigmas"] == 7870, "selected sigma-map count")
    require("actual_73column_sigmas=len(r['sigmas'])" in audit_code,
            "sigma-like field is a map count")
    stock_identity = invoice["physical_stock_identity"]
    require(stock_identity == {
        "data_and_owner_families": 7168,
        "local_helpers": 492,
        "private_centres": 8,
        "coefficient_work": 2,
    }, "selected finite stock identity")
    require(sum(stock_identity.values()) == invoice["physical"] == 7670,
            "selected finite physical stock sum")
    require("physical_stock_identity=dict(data_and_owner_families=live,local_helpers=helpers" in invoice_code,
            "invoice producer identity")

    rows = read("research/five-stage-source527-banks/proof/three-stage-cover-rows.tex").decode("utf-8")
    require("47\\lceil\\log_2\\max(2,n)\\rceil+O(1)" in rows, "depth slope 47 and unquantified additive term")
    require("W(w)^{D(n)}" in rows and "inherited old-leaf" in rows,
            "parent reserve factorization")
    require("logarithmic reserve" in rows and "log_qS(e,w)=O(w\\log e)" in rows,
            "qualitative reserve only")
    fit_note = read("research/bootstrap-cutoff-time-space-split/README.md").decode("utf-8")
    require("w = ⌈e^s⌉" in fit_note and "log_q S(e,w) = O(w log e)" in fit_note,
            "selected atom-width domain and fit target")

    pr387 = read("research/bootstrap-depth-audit/sources/pr387/PROOF.md").decode("utf-8")
    pr185 = read("research/bootstrap-depth-audit/sources/pr387/bootstrap-sources/research/community-round8-audit/pr185-proof-reviewed.md").decode("utf-8")
    require("For j=1,...,6 define A_j" in pr387 and "fixed depth" in pr387
            and "a_j=(1-s)s+s*a_(j-1)" in pr387,
            "retained stopped-stage family")
    require("new ordinary leaves need no *external* extra stock" in pr185,
            "completed inner external reserve is zero")
    require("252 is not asserted to be the new leaf's actual internal reserve" in pr185,
            "252 is only retained slack")

    historical = read("research/five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md").decode("utf-8")
    selected_audit = read("research/selected-bootstrap-stock-audit/README.md").decode("utf-8")
    require("T(n,w)<=sum_r c_r*T(r*floor(n/120),w)+C*n" in historical,
            "historical m=120 candidate")
    require("57,604w*ceil(log2(max(2,n)))" in historical and "m=120" in selected_audit and "W=23,683" in selected_audit,
            "historical 57,604 scope")
    require("sigma_j=sigma_0+j*57604" in selected_audit,
            "no selected 57,604 substitution")

    result = json.loads(read("research/selected-bootstrap-stock-audit/RESULT.json"))
    require(result["source_boundary"]["inherited_old_leaf_reserve_coefficient"] is None,
            "numerical old-leaf coefficient remains open")
    require(result["source_boundary"]["actual_stage_stock_coefficients"] is None,
            "numerical selected stage coefficient remains open")
    print("PASS_SELECTED_STAGE_STOCK_RECURRENCE_STRUCTURE native_stage=1 depth_slope=47 inner_external_stock=0 row_divisor=unquantified old_leaf_coefficient=unquantified")


if __name__ == "__main__":
    main()
