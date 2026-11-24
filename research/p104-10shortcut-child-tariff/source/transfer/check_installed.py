"""Measure the admitted ten-recipe 28-bit native directory without opening calendars."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from shutil import disk_usage
import sys
from tempfile import TemporaryDirectory


HEIGHTS = ((3000, 3080, 1024), (8192, 63614, 1005821, 15903360, 251454111, 268435455, 52270))
SELECTORS = {
    "peer": ("cbf85060a63dc4433c706d71ec582b0ebe6a09bbe26963ff78acb4c08e5edd92", ".003900862325217"),
    "tariff": ("d34b860c4c35aeb302767216bf58dd9da627fe2b1b2b646fd70d6a544563648e", ".003900862339776"),
    "domain": ("83c9616cadecbb6da76a0c4e0d909abe62490d48f35c47c08c68d879c65e13c7", ".003900862349161"),
    "clock": ("2d55f0269164878a6507c6756f2f27ccd6b3a6d2cbd5b3232e89ebc8e1b7a422", ".003900862349168"),
}
RUNTIME = {
    "grades.py": "8f8ec926213345e38e73110c2230e0bf03a2282252e924b5710cf212ca514be7",
    "transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "retimed_supplier.py": "2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c",
    "raw_binary_stage.py": "934d2ae0b305caa364f155cc407c0e8ca479837ba70b906b8f516f67a5cc17b6",
    "strong_complex.py": "2e87911b30d2d6467ceca95c4455f71ac010d7d258af3ff167320763fbccfd84",
    "typed_raw.py": "41f7e353bbf1914ed54f2c1c087476561dbcc06d1d5d4c828e20ebdd5bd8f28d",
    "typed_transport.py": "8968c44fb4349b3e0404c7b47dafad51e373d0ad1d290323674d6ad3cfa04348",
    "w5664_shortcut10.json.gz": "ce395afbf5c32be64c4e62389acaf9ce8cf8a9aaaa2fb7a278135bcfa0e635aa",
}
PORTABLE = {
    "compiler_state.py": "11f371903410a53aa138bb9b9c49e9441393a34092fff922716a78b5521e1870",
    "record_census.py": "8132c345cfcc5e7d89494fa437685673273f878f2dc40e0187bf2b84eee17e08",
    "tape_directory.py": "70bf289334f724cabf1cfa9e074199e6be93ef0aeba8193f279e5ef1336de97b",
}


def authenticate(root, prefix, pins):
    verified = {}
    for name, expected in pins.items():
        actual = sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Unexpected installed source at {prefix}/{name}")
        verified[f"{prefix}/{name}"] = actual
    return verified


def check_profile(profiles, kappa):
    assert tuple((*p.rank_logs, p.complex_log) for p in profiles) == HEIGHTS
    assert profiles[-1].kappa == kappa
    assert tuple(p.eta for p in profiles) == (Fraction(39, 10000), Fraction(1, 256))
    for p in profiles:
        for q in (p.eta, p.kappa):
            assert max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 128
        assert 0 < p.positive_stop_denominator < 2**128


def expanded_serial_bound(actions):
    word = 2**38
    extent = 2 * word + 2
    lookup = 8 * (4 * word * actions) * 512 * 128
    local = 2**16 * (extent + 4) * (7 * extent + 9) + 8 * 2**16 * (extent + 4)**2
    return (actions + 1) * (lookup + local + 2**120) * 2**32


def census(args):
    image, rate = SELECTORS[args.profile]
    sources = authenticate(args.runtime, "runtime", {**RUNTIME, "installations.py": image})
    sources.update(authenticate(args.portable, "portable", PORTABLE))
    for path in (args.runtime, args.scratch):
        assert disk_usage(path).free >= 8 * 1024**3
    sys.path[:0] = [str(args.runtime), str(args.portable)]
    from upstream import install

    install()
    from band_product import production_supplier
    from compiler_state import construct
    from grades import WeightedRecipe, WEIGHTS
    from installations import PROFILES
    from record_census import inspect
    from tape_directory import dump
    from transport import Recipe

    profiles = tuple(PROFILES.values())
    check_profile(profiles, Fraction(rate))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Fixed setup tried to open a native calendar or materialize its width")

    saved = Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width
    Recipe.open = WeightedRecipe.open = forbidden
    Recipe.width = WeightedRecipe.width = property(forbidden)
    try:
        state = construct()
        layers, word = state[:2]
        assert tuple(tuple(r.rank_log for r in layer) for layer in layers) == HEIGHTS
        assert all(r.width_log == 92 * r.rank_log for layer in layers for r in layer)
        for layer in layers:
            for r in layer[:-1]:
                assert r.targets is word.targets and r.paid is word.paid and r.cells is word.cells
        entry, terminal = (layer[-1] for layer in layers)
        assert entry.cells is terminal.cells
        assert entry.targets is terminal.targets and entry.paid is terminal.paid
        assert WEIGHTS == (1, 45, 2025)
        assert tuple(t.scale for t in entry.targets.variants) == (1, 2, 3)
        assert tuple(p.scale for p in entry.paid.variants) == (1, 2, 3)
        assert len({*entry.targets.histogram, *entry.paid.histogram}) < 2**8
        carriers = []
        for p, layer in zip(profiles, layers, strict=True):
            supplier = production_supplier(p.complex_log, p.positive_stop_denominator)
            assert supplier.recipe is layer[-1] and supplier.carrier.bit_count() == 1
            assert supplier.carrier.bit_length() == p.complex_log + 1
            carriers.append(supplier.carrier.bit_length())
        with TemporaryDirectory(prefix="ten-recipe-directory-", dir=args.scratch) as temp:
            path = Path(temp) / "directory.dag"
            with path.open("wb") as stream:
                count = dump(stream, state)
            observed = inspect(path)
            assert count == observed["records"] > 0
            assert observed["tag_counts"][15] == 8 and observed["tag_counts"][17] == 2
            assert observed["largest_integer_bits"] < 2**38 and observed["bytes"] < 2**38
            with path.open("rb") as stream:
                from hashlib import file_digest
                directory_sha256 = file_digest(stream, "sha256").hexdigest()
    finally:
        Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width = saved
    overhead = 2 * 2048 * (2**25 + 1) + sum(map(len, HEIGHTS)) * 2**24
    assert overhead == 137606729728 < 2**40
    serial = expanded_serial_bound(2**68 + 2**40)
    assert expanded_serial_bound(2**68) < serial < 2**228
    return {
        "scope": "Observed fixed native constructor and compact directory, with conditional setup accounting.",
        "profile": args.profile,
        "source_sha256": sources,
        "heights": HEIGHTS,
        "positive_carrier_bits": carriers,
        "directory": observed,
        "directory_sha256": directory_sha256,
        "structural_added_action_ceiling": overhead,
        "serial_transition_upper": serial,
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--profile", choices=SELECTORS, required=True)
    args = parser.parse_args()
    for name in ("runtime", "portable", "scratch"):
        setattr(args, name, getattr(args, name).resolve())
    print(json.dumps(census(args), indent=2, sort_keys=True))
