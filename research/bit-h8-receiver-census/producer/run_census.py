"""Stage A census: every admissible puncture set P (P552.json), shipped plan seed 552, default receivers.
Resumable: results are appended to results_A.jsonl one line per word; finished P are skipped on restart.
Live progress in progress_A.log.  usage: py -3.12 tools/run_census.py [workers]"""
import json, os, sys, time, ctypes
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
RES = os.path.join(BASE, "results_A.jsonl")
LOG = os.path.join(BASE, "progress_A.log")
SEED, NODEOPT = 552, 50


def low_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL
    except Exception:
        pass


def work(P):
    import one
    try:
        return one.evaluate(P, SEED, None, NODEOPT)
    except Exception as e:  # keep the census going; record the failure
        return {"P": P, "seed": SEED, "status": "error:" + repr(e)[:120]}


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    sets = json.load(open(os.path.join(BASE, os.environ.get("PSETS", "P552.json"))))["sets"]
    done = set()
    best = None
    stat = {}
    if os.path.exists(RES):
        for line in open(RES):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add(tuple(r["P"]))
            stat[r["status"][:6]] = stat.get(r["status"][:6], 0) + 1
            if r.get("kappa") and (best is None or r["kappa"] > best["kappa"]):
                best = r
    todo = [P for P in sets if tuple(P) not in done]
    log("start: %d sets, %d done, %d to do, workers %d" % (len(sets), len(done), len(todo), workers))
    t0, n = time.time(), 0
    with Pool(workers, initializer=low_priority) as pool, open(RES, "a") as out:
        for r in pool.imap_unordered(work, todo, chunksize=4):
            out.write(json.dumps(r) + "\n"); out.flush()
            n += 1
            stat[r["status"][:6]] = stat.get(r["status"][:6], 0) + 1
            if r.get("kappa") and (best is None or r["kappa"] > best["kappa"]):
                best = r
                log("new best kappa %.12f R %d P %s profile %s" % (r["kappa"], r["R"], r["P"], r["profile"]))
            if n % 100 == 0 or n == len(todo):
                el = time.time() - t0
                eta = el / n * (len(todo) - n)
                log("%d/%d (total %d/%d) status %s | best %.12f R %s | %.0f min elapsed, ETA %.0f min" % (
                    n, len(todo), n + len(done), len(sets), stat, best["kappa"] if best else 0,
                    best["R"] if best else "-", el / 60, eta / 60))
    log("finished")


if __name__ == "__main__":
    main()
