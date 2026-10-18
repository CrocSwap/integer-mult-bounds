"""portability: run the code paths that the toolkit takes on Windows on any OS, then selftest.py in this process.

Before the toolkit is imported, the resource module is hidden and SIGALRM/alarm/setitimer are removed from signal, as on
Windows; multiprocessing offers only spawn. Checks:
  1. compat.deadline uses its watchdog: a busy block past its deadline raises Timeout; 300 blocks that end around their
     deadline never leak an interrupt afterwards (and the SIGINT handler is restored); a SIGINT raised inside a block is still KeyboardInterrupt.
  2. peak_rss_gib() is None and pool_context() is spawn.
  3. a harness pricing interrupted by a 0.05 s deadline returns status 'timeout', and the same pricing completes after.
  4. selftest.py (with --quick: steps 1-4) passes in this process.
On Windows the hiding changes nothing. usage: python -B portability.py [--quick]"""
import multiprocessing as mp, runpy, signal, sys, time
from pathlib import Path
sys.modules["resource"] = None                     # import resource -> ImportError
for name in ("SIGALRM", "alarm", "setitimer", "ITIMER_REAL"):
    if hasattr(signal, name): delattr(signal, name)
mp.get_all_start_methods = lambda: ["spawn"]
import compat
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""), flush=True)
    if not ok: failures.append(name)
def busy(seconds):
    t = time.monotonic()
    while time.monotonic() - t < seconds: sum(range(1000))
t0 = time.monotonic()
try:
    with compat.deadline(0.2): busy(5); hit = False
except compat.Timeout: hit = True
check("watchdog deadline: busy block raises Timeout", hit and time.monotonic() - t0 < 2, f"after {time.monotonic() - t0:.2f}s")
leaks = timeouts = 0; handler = signal.getsignal(signal.SIGINT)
for i in range(300):                               # deadline 20 ms, blocks of 10..60 ms: the watchdog (a few ms late) fires around the block end
    try:
        with compat.deadline(0.02): busy(0.01 + 0.05 * i / 299)
    except compat.Timeout: timeouts += 1
    try: busy(0.003)
    except BaseException: leaks += 1
check("watchdog deadline: no interrupt leaks after the block", leaks == 0 and 0 < timeouts < 300 and signal.getsignal(signal.SIGINT) is handler,
      f"{timeouts}/300 blocks timed out, {leaks} leaks, SIGINT handler restored")
try:
    with compat.deadline(30): signal.raise_signal(signal.SIGINT); busy(1); real = "none"
except KeyboardInterrupt: real = "KeyboardInterrupt"
except compat.Timeout: real = "Timeout"
check("watchdog deadline: a real SIGINT stays KeyboardInterrupt", real == "KeyboardInterrupt", real)
check("no resource module: peak_rss_gib() is None", compat.peak_rss_gib() is None)
check("no fork: pool_context() is spawn", compat.pool_context().get_start_method() == "spawn")
if __name__ == "__main__":
    import harness as C, selftest as ST
    import tempfile
    pre = ST.extract(ST.PRE, tempfile.mkdtemp(prefix="eft-portability-"))
    P = C.Pricer(pre); ed = dict(delete=[], insert=[], tail=[], prepend=[])
    slow = P.price(ed, timeout=0.05); full = P.price(ed, timeout=90)
    check("harness: a pricing over its deadline returns 'timeout'; the same pricing completes after", slow.get("status") == "timeout" and full.get("status") == "ok" and full.get("delta") == 0,
          f"{slow.get('status')} then {full.get('status')} delta {full.get('delta')}")
    if failures:
        print("PORTABILITY FAIL", failures); sys.exit(1)
    sys.argv = [str(Path(__file__).with_name("selftest.py"))] + sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
