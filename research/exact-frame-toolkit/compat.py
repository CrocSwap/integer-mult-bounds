"""compat: the toolkit's platform-dependent pieces, for POSIX (Linux, macOS) and Windows.

deadline(seconds)   context manager raising Timeout in the main thread after `seconds` of wall time. POSIX: SIGALRM, as
                    before. Windows has no SIGALRM: a watchdog thread interrupts the main thread (_thread.interrupt_main)
                    and a temporary SIGINT handler turns that interrupt into Timeout; a real Ctrl+C still raises
                    KeyboardInterrupt. Both act between Python bytecodes, so one long C call (e.g. numpy) finishes first.
peak_rss_gib()      peak resident memory of this process in GiB (ru_maxrss counts bytes on macOS, KiB on Linux), or None
                    where the resource module is missing (Windows).
pool_context()      multiprocessing context for the sweeps: fork where the platform has it, else spawn
                    (EFT_START_METHOD overrides, e.g. to test spawn on POSIX).
child_env()         environment for the Python subprocesses (audit_local, compose): UTF-8 mode, no PYTHONOPTIMIZE.
Importing this module refuses python -O: the toolkit's assert statements (kappa outer constraints, recount monotonicity,
archive pins) are checks."""
import contextlib, multiprocessing as mp, os, signal, sys, threading, time, _thread

if not __debug__:
    raise RuntimeError("exact-frame-toolkit: run without -O / PYTHONOPTIMIZE; its assert statements are checks")


class Timeout(Exception):
    pass


@contextlib.contextmanager
def deadline(seconds):
    if not seconds or threading.current_thread() is not threading.main_thread():
        yield
        return
    if hasattr(signal, "SIGALRM"):
        def on_alarm(sig, frame): raise Timeout()
        old = signal.signal(signal.SIGALRM, on_alarm); signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0); signal.signal(signal.SIGALRM, old)
        return
    state = dict(fired=False, delivered=False); lock = threading.Lock(); done = threading.Event()
    def watch():
        if done.wait(seconds): return
        with lock:                          # fire only while the block is still running
            if done.is_set(): return
            state["fired"] = True; _thread.interrupt_main()
    def on_sigint(sig, frame):
        if state["fired"] and not state["delivered"]:
            state["delivered"] = True; raise Timeout()
        if prev == signal.SIG_IGN: return
        if callable(prev): return prev(sig, frame)
        raise KeyboardInterrupt
    prev = signal.signal(signal.SIGINT, on_sigint)
    t = threading.Thread(target=watch, daemon=True); t.start()
    try:
        yield
    finally:
        try:
            with lock: done.set()           # after this the watchdog cannot fire
            t.join()
            for _ in range(1000):           # an interrupt that fired as the block ended is still pending: take it here
                if not state["fired"] or state["delivered"]: break
                time.sleep(0.001)
        except Timeout:
            pass
        finally:
            signal.signal(signal.SIGINT, prev if prev is not None else signal.default_int_handler)


def peak_rss_gib():
    try:
        import resource
    except ImportError:
        return None
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1024 ** 3 if sys.platform == "darwin" else r / 1024 ** 2


def pool_context():
    m = os.environ.get("EFT_START_METHOD") or ("fork" if "fork" in mp.get_all_start_methods() else "spawn")
    return mp.get_context(m)


def child_env():
    env = dict(os.environ, PYTHONUTF8="1"); env.pop("PYTHONOPTIMIZE", None)
    return env
