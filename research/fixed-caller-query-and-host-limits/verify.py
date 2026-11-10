"""Replay the submitted, bounded negative checks in a disposable copy."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("suite", choices=("caller", "idle", "host"))
suite = parser.parse_args().suite
hashes = json.loads((root / "SHA256.json").read_text())
for path, expected in hashes.items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected, path

checks = {
    "caller": [
        ("screen_7000_central_query_rank", "PR7000-CENTRAL-QUERY-SIGN-RANK"),
        ("screen_7000_query_host_contacts", "PR7000-QUERY-HOST-TRANSPORT-CONTACTS"),
        ("price_7004_query_families", "PR7004-QUERY-FAMILY-TARGET-PRICE"),
        ("certify_7000_sign_query_floor", "PR7000-QUERY-COUNT-SIGN-LOWER-BOUND"),
    ],
    "idle": [
        ("construct_7002_chronological_idle_groups", "PR7002-CHRONOLOGICAL-IDLE-GROUPS"),
        ("construct_7002_noncoordinate_idle", "PR7002-NONCOORDINATE-IDLE-WORD"),
        ("search_7002_idle_projector_order", "PR7002-IDLE-PROJECTOR-ORDER-SEARCH"),
        ("price_7002_75_job_composition", "PR7002-75-JOB-COMPOSITION-PRICE"),
    ],
    "host": [
        ("screen_6824_mixed_first_order", "PR6824-MIXED-FIRST-ORDER-HOST-CONTACTS"),
        ("screen_6824_two_edit_mixed", "PR6824-TWO-EDIT-MIXED-CANCELLATION"),
        ("screen_6824_dark_two_contact", "PR6824-TWO-CONTACT-DARK-REACHABILITY"),
        ("certify_6824_two_add_obstruction", "PR6824-TWO-ADD-HOST-OBSTRUCTION"),
    ],
}
with TemporaryDirectory(prefix="fixed-caller-replay-") as temp:
    work = Path(temp) / "replay"
    shutil.copytree(root / "replay", work)
    for script, receipt in checks[suite]:
        subprocess.run([sys.executable, "-B", str(work / f"{script}.py")], cwd=work, check=True)
        name = receipt + ".json"
        got = json.loads((work / name).read_text())
        want = json.loads((root / "expected" / name).read_text())
        assert got == want, f"Replay changed {name}"
        if receipt == "PR7000-CENTRAL-QUERY-SIGN-RANK":
            assert [v["fixed_interval_query_lower_bound"] for v in got["branches"].values()] == [4, 4]
        if receipt == "PR7000-QUERY-HOST-TRANSPORT-CONTACTS":
            assert got["tested_pairs"] == 300 and got["matches"] == []
        if receipt == "PR7002-75-JOB-COMPOSITION-PRICE":
            assert got["jobs_per_port"] == 75
            assert got["tests"]["1/200"]["remaining_rank_one_equivalents"] == 815
print(f"PASS_FIXED_CALLER_NEGATIVE_{suite.upper()}")
