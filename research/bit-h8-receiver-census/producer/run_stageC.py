"""Stage C: all 3^9 = 19,683 receiver choices for PR589's puncture set (the repo's p111-receiver-census counted only
R; here every word is priced).  Resumable (results_C.jsonl), log progress_C.log.  usage: run_stageC.py [workers]"""
import itertools, json, os, sys, time, ctypes
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
RES, LOG = os.path.join(BASE, "results_C.jsonl"), os.path.join(BASE, "progress_C.log")
P = [10, 15, 51, 53, 56, 66, 72, 89, 111]
BASELINE_UNTUNED = 0.0034629756599990342


def low_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def work(choice):
    import one
    sel = dict(zip(P, choice))
    try:
        r = one.evaluate(P, 552, sel, 50)
    except Exception as e:
        r = {"P": P, "status": "error:" + repr(e)[:120]}
    r["receivers"] = sel
    r["choice"] = list(choice)
    return r


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    done = set()
    if os.path.exists(RES):
        for l in open(RES):
            try:
                done.add(tuple(json.loads(l)["choice"]))
            except ValueError:
                pass
    jobs = [c for c in itertools.product((1, 2, 3), repeat=9) if c not in done]
    log("start: 19683 receiver choices, %d done, %d to do" % (len(done), len(jobs)))
    best, t0, n = None, time.time(), 0
    with Pool(workers, initializer=low_priority) as pool, open(RES, "a") as out:
        for r in pool.imap_unordered(work, jobs, chunksize=4):
            out.write(json.dumps(r) + "\n"); out.flush(); n += 1
            if r.get("kappa") and (best is None or r["kappa"] > best["kappa"]):
                best = r
                log("new best untuned kappa %.12f (PR555 untuned %.12f) R %d receivers %s profile %s" % (
                    r["kappa"], BASELINE_UNTUNED, r["R"], r["receivers"], r["profile"]))
            if n % 200 == 0 or n == len(jobs):
                el = time.time() - t0
                log("%d/%d | best %.12f | %.0f min elapsed, ETA %.0f min" % (n, len(jobs), best["kappa"] if best else 0,
                                                                         el / 60, el / n * (len(jobs) - n) / 60))
    log("finished")


if __name__ == "__main__":
    main()
