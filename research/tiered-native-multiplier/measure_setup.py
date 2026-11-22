"""Measure complete fixed preparation in one fresh process per observation."""

from argparse import ArgumentParser
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import platform
import resource
from subprocess import run
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

HERE = Path(__file__).resolve().parent


def load_file(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cpu():
    rows = [resource.getrusage(who) for who in (resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN)]
    return sum(x.ru_utime+x.ru_stime for x in rows)


def measure(peer):
    start, used = perf_counter(), cpu()
    with TemporaryDirectory(prefix="tier-timing-") as tmp:
        work = Path(tmp)
        machine = work / "machine"
        if peer is None:
            load_file("candidate_setup",HERE/"bootstrap.py").install(machine)
        else:
            wrapper = load_file("fixed_carrier_source",peer/"verify.py")
            src = work / "peer"
            src.mkdir()
            wrapper.restore(src)
            wrapper.edit_installation(src)
            run([sys.executable,"-IB",str(src/"bootstrap.py"),str(machine)],check=True)
        sys.path.insert(0,str(machine))
        from band_product import prepare_native
        from installations import PROFILES
        if peer is None:
            rows = prepare_native()
        else:
            rows = (prepare_native(PROFILES["extended"]),)
        contracts = [[(r.rank_log,len(r.targets),len(r.paid),len(r.cells)) for r in tier] for tier in rows]
        assert all(len(tier)==3 and tier[-1][1:3]==(105216,564144) for tier in contracts)
        digest = sha256((machine/"strong-bit.json.gz").read_bytes()).hexdigest()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(dict(revision="candidate" if peer is None else "8053",wall=perf_counter()-start,
                          cpu=cpu()-used,rss_bytes=rss if sys.platform=="darwin" else rss*1024,
                          python=sys.version.split()[0],system=platform.platform(),machine=platform.machine(),
                          installed=contracts,binary_sha256=digest)))


if __name__ == "__main__":
    args = ArgumentParser(description=__doc__)
    args.add_argument("--peer-8053",type=Path)
    measure(args.parse_args().peer_8053)
