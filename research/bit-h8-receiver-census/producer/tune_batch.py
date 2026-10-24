"""Tune a list of receiver choices for PR589's set with tools/tune_one.py, 2 at a time; summary in tuned/batch.log."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
P = "10,15,51,53,56,66,72,89,111"
sels = json.load(open(sys.argv[1]))
tag = sys.argv[2]


def run(i):
    out = os.path.join(HERE, "..", "tuned", "%s-%02d" % (tag, i))
    subprocess.run([sys.executable, "-B", os.path.join(HERE, "tune_one.py"), P, json.dumps(sels[i]), out],
                   stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
    r = json.load(open(out + "-result.json"))
    with open(os.path.join(HERE, "..", "tuned", "batch.log"), "a") as f:
        f.write("%s-%02d R %d moves %d base %.12f tuned %.12f receivers %s\n" % (
            tag, i, r["R"], r["moves"], r["base_kappa"], r["tuned_kappa"], r["receivers"]))


with ThreadPoolExecutor(2) as ex:
    list(ex.map(run, range(len(sels))))
