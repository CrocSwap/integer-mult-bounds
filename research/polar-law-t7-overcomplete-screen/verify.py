"""Replay for research/polar-law-t7-overcomplete-screen.

Reruns every stage of search.py and asserts the results match CERTIFICATE.json,
then prints PASS_POLAR_T7_OVERCOMPLETE_SCREEN. Stdlib only; exact arithmetic.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cert_path = os.path.join(HERE, "CERTIFICATE.json")
    want = json.load(open(cert_path, encoding="utf-8"))
    fails = []
    got = {"python": sys.version.split()[0]}
    stages = ["controls", "t7t8", "searches", "overfull", "overpunc"]
    for st in stages:
        print("== replay stage %s ==" % st)
        search.compute(st, fails, got)
    if fails:
        print("CONTROL FAILURES:", fails)
        return 1
    for key in ("controls", "t7t8_full", "t7t8_searches", "overcomplete_full", "overcomplete_punctures"):
        if got.get(key) != want.get(key):
            print("MISMATCH in certificate key:", key)
            for sub in sorted(set(got.get(key, {})) | set(want.get(key, {}))):
                if got.get(key, {}).get(sub) != want.get(key, {}).get(sub):
                    print("  first differing entry:", sub)
                    print("   got :", json.dumps(got.get(key, {}).get(sub), sort_keys=True)[:400])
                    print("   want:", json.dumps(want.get(key, {}).get(sub), sort_keys=True)[:400])
            return 1
        print("MATCH %s (%d entries)" % (key, len(got.get(key, {}))))
    print("PASS_POLAR_T7_OVERCOMPLETE_SCREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
