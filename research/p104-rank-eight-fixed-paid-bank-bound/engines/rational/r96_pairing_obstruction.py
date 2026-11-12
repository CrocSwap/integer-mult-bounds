"""Record the exact two scalar pairings on each of four independently traced lines."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
SOURCE_SHA = "0bbf9d1ea0957de30dbe9f7afa4a6fb86236b2910127f1af2722cab6b597ab26"


def main():
    assert __debug__
    source = ROOT / "exact_four.py"
    assert sha256(source.read_bytes()).hexdigest() == SOURCE_SHA
    adapter = run_path(str(source))
    for rel in ("reused/exact_six.py", "reused/rolling_exterior.py"):
        adapter["pinned"](ROOT / rel, rel)
    exact = run_path(str(ROOT / "reused/exact_six.py"))

    def read(name):
        rel = f"inputs/{name}.json"
        return loads(adapter["pinned"](ROOT / rel, rel), object_pairs_hook=exact["unique"])

    def stop(*_):
        raise TimeoutError("Hard 35-second verification cap")

    signal(SIGALRM, stop)
    alarm(35)
    deadline = monotonic() + 33
    try:
        rows, _ = adapter["selected_banks"](*(read(x) for x in ("SELECTION", "GEOMETRY", "SUFFIX", "PRICE")))
        word = exact["checked"](ROOT / "inputs/7334-WORD.json.gz", "word")
        cohort = set(read("PRICE")["cohort"])
        result = []
        for row, (p, s) in zip(rows, exact["trace"](word, rows, deadline), strict=True):
            _, pre = exact["pure"](p, cohort)
            _, suf = exact["pure"](s, cohort)
            assert len(pre) == len(suf) == 1
            (a, c), (b, d) = pre[0], suf[0]
            cut, endpoint = exact["dot"](a, b), exact["dot"](c, d)
            assert c and d and (cut == 0 or cut != endpoint)
            a = {row["public"][i]: v for i, v in a.items()}
            b = {row["public"][i]: v for i, v in b.items()}
            result.append(dict(key=row["key"], cut_pairing=str(cut), endpoint_pairing=str(endpoint),
                generators={name: {i: str(v) for i, v in values.items()}
                            for name, values in zip("abcd", (a,b,c,d), strict=True)}))
    finally:
        alarm(0)
    print(dumps(dict(adapter_sha256=SOURCE_SHA, results=result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
