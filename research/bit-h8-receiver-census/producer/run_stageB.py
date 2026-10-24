"""Stage B: for the TOP puncture sets of stage A (by kappa), try random receiver choices (as PR555 discovery/search.py)
and keep the best word per P.  Control: PR589's own P is always included.  Resumable (results_B.jsonl), log progress_B.log.
usage: py -3.12 tools/run_stageB.py TOP DRAWS [workers]"""
import json, os, sys, time, random, ctypes
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
RES = os.path.join(BASE, "results_B.jsonl")
LOG = os.path.join(BASE, "progress_B.log")
SEED, NODEOPT = 552, 50
SHIPPED = [10, 15, 51, 53, 56, 66, 72, 89, 111]
BASELINE = 0.003464248972023964


def low_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def work(job):
    import one
    P, draw = job
    sel = None
    if draw > 0:
        rr = random.Random(1000003 * draw + sum(p << (i * 7) for i, p in enumerate(P)))
        sel = {p: rr.choice((1, 2, 3)) for p in P}
    try:
        r = one.evaluate(P, SEED, sel, NODEOPT)
    except Exception as e:
        r = {"P": P, "status": "error:" + repr(e)[:120]}
    r["draw"] = draw
    r["receivers"] = sel
    return r


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    top, draws = int(sys.argv[1]), int(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    A = [json.loads(l) for l in open(os.path.join(BASE, "results_A.jsonl"))]
    A = [r for r in A if r.get("kappa")]
    A.sort(key=lambda r: -r["kappa"])
    Ps = [r["P"] for r in A[:top]]
    if SHIPPED not in Ps:
        Ps.append(SHIPPED)
    done = set()
    if os.path.exists(RES):
        for l in open(RES):
            r = json.loads(l); done.add((tuple(r["P"]), r["draw"]))
    jobs = [(P, d) for P in Ps for d in range(draws + 1) if (tuple(P), d) not in done]
    log("start: %d sets x %d draws, %d jobs to do" % (len(Ps), draws + 1, len(jobs)))
    best, t0, n = None, time.time(), 0
    with Pool(workers, initializer=low_priority) as pool, open(RES, "a") as out:
        for r in pool.imap_unordered(work, jobs, chunksize=2):
            out.write(json.dumps(r) + "\n"); out.flush(); n += 1
            if r.get("kappa") and (best is None or r["kappa"] > best["kappa"]):
                best = r
                log("new best kappa %.12f (baseline %.12f, %s) R %d P %s receivers %s" % (
                    r["kappa"], BASELINE, "BEATS" if r["kappa"] > BASELINE else "below", r["R"], r["P"], r["receivers"]))
            if n % 100 == 0 or n == len(jobs):
                el = time.time() - t0
                log("%d/%d | best %.12f | %.0f min elapsed, ETA %.0f min" % (n, len(jobs), best["kappa"] if best else 0,
                                                                         el / 60, el / n * (len(jobs) - n) / 60))
    log("finished")


if __name__ == "__main__":
    main()
