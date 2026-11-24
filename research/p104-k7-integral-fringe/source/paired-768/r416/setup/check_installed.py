"""Measure the fixed nine-recipe native directory on an admitted exact runtime."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from shutil import disk_usage
import signal
import sys
from tempfile import TemporaryDirectory

HEIGHTS = ((3000, 3080, 1024), (31808, 502922, 7951907, 125730703, 134217727, 208653))
SELECTORS = {
    "peer": ("5b31cca69a8f10c78152ae030ae7c7ab156d22feec83347b887aa3fe78098ee7", Q(".003900857267786")),
    "candidate": ("37460b2be0a93ecfe110be25de5a4ea787c2d09973f926f680ea148453dc89e2", Q(".003900857269150")),
}
RUNTIME = {
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "retimed_supplier.py": "2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c",
    "raw_binary_stage.py": "8020d33828233e7016700849a507a8cee78db8a17a33b6063b737313ea05b07f",
    "strong_complex.py": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
}
PORTABLE = {
    "compiler_state.py": "11f371903410a53aa138bb9b9c49e9441393a34092fff922716a78b5521e1870",
    "record_census.py": "8132c345cfcc5e7d89494fa437685673273f878f2dc40e0187bf2b84eee17e08",
    "tape_directory.py": "70bf289334f724cabf1cfa9e074199e6be93ef0aeba8193f279e5ef1336de97b",
}
RESERVE = 8 * 1024**3
EXTRA_ACTIONS = 2**40


def verify_hashes(root, pins):
    for name, expected in pins.items():
        if sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unexpected installed source at {name}")


def check_profile(profiles, kappa):
    entry, terminal = profiles
    actual = tuple((*profile.rank_logs, profile.complex_log) for profile in profiles)
    assert actual == HEIGHTS and terminal.kappa == kappa
    assert (entry.eta, terminal.eta) == (Q(39, 10000), Q(1, 256))
    for profile in profiles:
        for q in (profile.eta, profile.kappa):
            assert max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 128
        assert 0 < profile.positive_stop_denominator < 2**128


def expanded_serial_bound(extra):
    n, w = 2**68 + extra, 2**38
    h = 2*w + 2
    lookup = 8*(4*w*n)*512*128
    local = 2**16*(h+4)*(7*h+9) + 8*2**16*(h+4)**2
    return (n+1)*(lookup+local+2**120)*2**32


def census(args):
    digest, kappa = SELECTORS[args.profile]
    verify_hashes(args.runtime, {**RUNTIME, "installations.py": digest})
    verify_hashes(args.portable, PORTABLE)
    for directory in (args.runtime, args.scratch):
        if disk_usage(directory).free < RESERVE:
            raise RuntimeError("Insufficient available disk for native census")
    sys.path[:0] = [str(args.runtime), str(args.portable)]
    from upstream import install

    install()
    from band_product import production_supplier
    from compiler_state import construct
    from grades import WeightedRecipe
    from installations import PROFILES
    from record_census import inspect
    from tape_directory import dump
    from transport import Recipe

    profiles = tuple(PROFILES.values())
    check_profile(profiles, kappa)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Fixed setup tried to materialize an active native width or calendar")

    saved = Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width
    Recipe.open = WeightedRecipe.open = forbidden
    Recipe.width = WeightedRecipe.width = property(forbidden)
    try:
        state = construct()
        layers = state[0]
        assert tuple(tuple(r.rank_log for r in layer) for layer in layers) == HEIGHTS
        assert all(r.width_log == 92*r.rank_log for layer in layers for r in layer)
        assert all((r.targets is state[1].targets and r.paid is state[1].paid and r.cells is state[1].cells)
                   for layer in layers for r in layer[:-1])
        assert layers[0][-1].cells is layers[1][-1].cells
        assert layers[0][-1].targets is layers[1][-1].targets
        carriers = []
        for profile, layer in zip(profiles, layers, strict=True):
            supplier = production_supplier(profile.complex_log, profile.positive_stop_denominator)
            assert supplier.recipe is layer[-1] and supplier.carrier.bit_count() == 1
            assert supplier.carrier.bit_length() == profile.complex_log + 1
            carriers.append(supplier.carrier.bit_length())
        with TemporaryDirectory(prefix="nine-recipe-census-", dir=args.scratch) as temp:
            path = Path(temp) / "directory.dag"
            with path.open("wb") as stream:
                count = dump(stream, state)
            observed = inspect(path)
            assert count == observed["records"] > 0
            assert observed["largest_integer_bits"] < 2**38 and observed["bytes"] < 2**38
            directory_sha256 = sha256(path.read_bytes()).hexdigest()
    finally:
        Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width = saved
    overhead = 2*2048*(2**25+1) + sum(map(len, HEIGHTS))*2**24
    assert overhead == 137589952512 < EXTRA_ACTIONS
    setup = expanded_serial_bound(EXTRA_ACTIONS)
    assert expanded_serial_bound(0) < setup < 2**228
    return dict(
        scope="Observed fixed constructor and directory census; conditional all-size setup bound",
        installation_sha256=digest, profile=args.profile, heights=HEIGHTS,
        positive_carrier_bits=carriers, directory=observed, directory_sha256=directory_sha256,
        structural_added_action_ceiling=overhead, extra_indexed_action_budget=EXTRA_ACTIONS,
        serial_transition_upper=setup, serial_upper_power=228,
    )


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--profile", choices=SELECTORS, required=True)
    args = parser.parse_args()
    for path in ("runtime", "portable", "scratch"):
        setattr(args, path, getattr(args, path).resolve())
    def timeout(_signal, _frame):
        raise TimeoutError("The installed setup census reached its 150-second cap")

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(150)
    try:
        print(json.dumps(census(args), indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
