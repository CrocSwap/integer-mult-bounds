"""Construct the single paid-quarter and compact tier edit over exact #8055."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
from shutil import copytree
import subprocess
import sys
import tempfile

HEAD = "7b48187d99525ad59f560de3921ec7e48382484c"
SOURCES_SHA = "7a10012734132909e99b0c6160d68d0b8647e1607d25679efb1f5315cf8e23de"
PROTOTYPE_SHA = "f86a898583ffec816871cd94f8580daa3201d0892185cc0484a1cb77211eceb8"
PRICE_SHA = "426d4b919668e504b5017f589fdc100154e2f60509c93546f5fb7eb0cd12f927"
PINS = {
    "bootstrap.py": "74ac8f1d3af21f86cda48a3d50084d6fa5faf84b44ec2e5929b587f40f5bcfd1",
    "installations.py": "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df",
    "grades.py": "340684fdd5ca0e611836b0e7301f1c339282ba532bf9e3ec8055944d8981f3c8",
    "receipt.py": "3d0219eb2262ea64ccf2dc8da4d2877e32c519c4670d99577703f8bfc236ba61",
    "independent_price.py": "0b2ecc4a1845a2807782644b6b2675e2fcb194fcbb3ae80b50af9a775363e952",
    "check_gaussian.py": "383a3385bc9763d6eb557163ee62aa9ab999b0d98c719a004db87abfee063d24",
    "RESULT.json": "661e16fcb533b69b97ad2dc91ab81bed79c44e7fdce01306ce573cb6f0ed7fa7",
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def replace(path, script):
    text = path.read_text()
    for old, new in script:
        if text.count(old) != 1:
            raise ValueError(f"No unique edit for {old!r} in {path.name}")
        text = text.replace(old, new)
    path.write_text(text)


PROGRAM = {
    "transport.py": (
        ("class Plan:", """def paid_axis_count(rank, columns):
    if rank in (F(1, 4), F(3, 4)):
        if columns < 4 or columns % 2:
            raise ValueError("Expected at least four even columns")
        first = columns // 4
        return first if rank == F(1, 4) else columns - first
    return rank * columns


class Plan:"""),
        ("size = self.paid[j] * (e - 8)", "size = paid_axis_count(self.paid[j], e - 8)"),
        ("self.ticks * self.count[e] * self.paid[j] * (e - 8)",
         "self.ticks * self.count[e] * paid_axis_count(self.paid[j], e - 8)"),
    ),
    "retimed_supplier.py": (
        ("from grades import SCALES, SPLITS, numerical_source, numerical_recipe",
         "from grades import QUARTER, SCALES, SPLITS, numerical_source, numerical_recipe\nfrom transport import paid_axis_count"),
        ('raise ValueError("Each split needs a positive even column count")',
         'raise ValueError("Each split needs a positive even column count")\n        if columns < 4:\n            raise ValueError("Each quarter split needs at least four columns")'),
        ("yield job.select(range(width // 2))\n                    yield job.select(range(width // 2, width))",
         "first = paid_axis_count(QUARTER, width)\n                    yield job.select(range(first))\n                    yield job.select(range(first, width))"),
    ),
    "unpowered_price.py": (
        ("    if r == F(1, 2):\n        low, high = power_interval(2, t)\n        return (UNIT * UNIT // high, -(-UNIT * UNIT // low))\n    return power_interval(int(r), t)",
         "    rank = F(r)\n    low, high = power_interval(rank.numerator, t)\n    if rank.denominator == 1:\n        return low, high\n    a, b = power_interval(rank.denominator, t)\n    return UNIT * low // b, -(-UNIT * high // a)"),
    ),
}


EDIT = {
    "bootstrap.py": (
        ('    copyfile(HERE / "grades.py", dest / "grades.py")',
         '    copyfile(HERE / "grades.py", dest / "grades.py")\n    from runpy import run_path\n    run_path(str(HERE / "quarter_overlay.py"))["apply"](dest)'),
    ),
    "installations.py": (
        ("Q(2143194013, 2**39)", "Q(1097317122991, 2**48)"),
        ('TERMINAL = Profile((35327, 559005), 680000, Q(".0038982"))',
         'TERMINAL = Profile((35327, 561325), 680000, Q(".00389821005"))'),
    ),
    "grades.py": (
        ("HALF = Fraction(1, 2)", "QUARTER = Fraction(1, 4)\nCOMPLEMENT = Fraction(3, 4)"),
        ("self.histogram[HALF] += 2 * splits",
         "self.histogram[QUARTER] += splits\n            self.histogram[COMPLEMENT] += splits"),
        ("yield HALF\n                    yield HALF", "yield QUARTER\n                    yield COMPLEMENT"),
    ),
    "receipt.py": (
        ("len(cells) == 62","len(cells) == 63"),
        ("assert max(Q(k)/r for r, k in cells) == 9",
         "assert max(Q(k)/r for r, k in cells) == 9 and min(paid) == Q(1, 4)\n"
         "        assert c.denominator <= 2**48 and Q(100,99)**250 > 4\n"
         "        assert Q(99,100)*Q(2,9)>Q(19,100) and t > Q(996,1000)\n"
         "        assert Q(10)*Q(106,100)/(Q(996,1000)*Q(99,100)*Q(19,100)) < 64\n"
         "        assert max(target)*4 < 32*2066\n"
         "        for r,k in cells:\n"
         "            z=Q(-1,2) if r==Q(1,4) else Q(1,2) if r==Q(3,4) else Q(0)\n"
         "            assert 8*k-10*r+min(0,z)>=0\n"
         "            assert 10*k-8*r+max(0,z)<10*k and z<=8*r"),
        ("assert factor < Q(power_interval(2,Q(43,256))[0],UNIT)",
         "assert factor**2048 < 2**339"),
        ("positive = GAUSSIAN_C-Q(43,256*num)", "positive = GAUSSIAN_C-Q(339,2048*num)"),
        ("(572,339787971)", "(573,340530371)"),
        ('delta = TERMINAL.kappa-Q(".0038981730255")\n    assert delta == Q(53949,2*10**12)',
         'delta = TERMINAL.kappa-Q(".00389821")\n    assert delta == Q(1,20_000_000_000)'),
        ('old_rate=".0038981730255"','old_rate=".00389821"'),
    ),
    "independent_price.py": (
        ("assert margin(histogram(79),GAUSSIAN_C)[0] > 0",
         """fixed_79 = histogram(79)
assert margin(fixed_79, GAUSSIAN_C)[1] < 0
quarter_79 = fixed_79.copy()
quarter_79[Q(1,2)] += 2016
quarter_79[Q(1,4)] -= 1008
quarter_79[Q(3,4)] -= 1008
new_lo, new_hi = Q(2194634319317, 2**49), Q(4389268638635, 2**50)
assert margin(quarter_79, new_lo)[0] > 0
assert margin(quarter_79, new_hi)[1] < 0
assert margin(quarter_79, GAUSSIAN_C)[0] > 0
assert Q(2143194013,2**39)-Q(43,256*TERMINAL.complex_log)<TERMINAL.ordinary
# The scaled quarter inventory only needs uniqueness in the admitted
# t > .996 tariff range to compare it with the exact installed price.
derivative = 0
for r, n in quarter_79.items():
    a, b = log_rank(Q(r).numerator)
    d, e = log_rank(Q(r).denominator)
    ends = (*power(r, Q(249,250)), *power(r,1-Q(2143194013,2**39)))
    derivative += min(n*x*y for x in (a-e,b-d) for y in (min(ends),max(ends)))
assert derivative > 10**7
print("PASS_INDEPENDENT_QUARTER_BRACKET", new_lo, new_hi)"""),
    ),
    "verify.py": (
        ('print(worker("check_gaussian.py",dst),end="")',
         'run([sys.executable,"-IB",str(PACKAGE/"check_gaussian.py"),str(dst)],check=True)'),
    ),
    "check_gaussian.py": (
        ("from grades import SCALES, SPLITS","from grades import SCALES, SPLITS\nfrom transport import paid_axis_count"),
        ("jobs=[Job(i,range(2*k))", "columns = 6\n    jobs=[Job(i,range(columns*k))"),
        ("widths=tuple(2*s for s in SCALES)", "widths=tuple(columns*s for s in SCALES)"),
        ("slots=2*producer.recipe.ambient", "slots=columns*producer.recipe.ambient"),
        ("Raw(w,raw).native(jobs,2)", "Raw(w,raw).native(jobs,columns)"),
        ("len(job.axes)==2*grade","len(job.axes)==paid_axis_count(grade, columns)"),
        ('assert len(job.axes)==paid_axis_count(grade, columns)',
         'assert len(job.axes)==paid_axis_count(grade, columns)\n'
         '        if completed % 100_000 == 0:\n'
         '            print("CHECK_COMPACT_NUMERICAL_PAID_CUTS", completed, flush=True)'),
        ('"sum output axes",2*sum(sizes)', '"sum output axes",columns*sum(sizes)'),
    ),
}


def make_overlay(work, source_record):
    installed_pins={key:source_record["runtime"][key]["after"] for key in PROGRAM}
    code = f"""# Apply the charged paid quarter/complement rule to exact #8055 runtime files.
from hashlib import sha256

PINS = {installed_pins!r}
EDITS = {PROGRAM!r}


def apply(root):
    for name, edits in EDITS.items():
        path = root / name
        if sha256(path.read_bytes()).hexdigest() != PINS[name]:
            raise ValueError(f"Quarter overlay source changed at {{name}}")
        text = path.read_text()
        for old, new in edits:
            if text.count(old) != 1:
                raise ValueError(f"Expected exact change point in {{name}}")
            text = text.replace(old, new)
        path.write_text(text)
"""
    (work / "quarter_overlay.py").write_text(code)


def materialize(peer, proof, prototype, work):
    assert digest(proof) == PRICE_SHA and digest(prototype)==PROTOTYPE_SHA
    expected = json.loads(proof.read_bytes())
    assert expected["peer"] == HEAD and expected["kappa"]=="1949101/500000000"
    assert digest(peer / "SOURCES.json") == SOURCES_SHA
    for name, expected_hash in PINS.items():
        assert digest(peer / name) == expected_hash, name
    for name, changes in PROGRAM.items():
        if name == "transport.py":
            source_proto=prototype.read_text()
            assert all(old in source_proto and new in source_proto
                       for old,new in changes[1:])
            assert changes[0][1].split("class Plan:")[0].strip() in source_proto
    copytree(peer,work)
    for name, changes in EDIT.items():
        replace(work / name, changes)
    manifest = json.loads((work / "SOURCES.json").read_bytes())
    for name in ("installations.py","grades.py"):
        manifest["archive_and_overlay_sha256"][name]=digest(work/name)
    manifest["runtime"]["installations.py"]["after"]=digest(work/"installations.py")
    make_overlay(work, manifest)
    (work / "SOURCES.json").write_text(json.dumps(manifest,indent=2)+"\n")


def run_worker(work, name, temporary, timeout=60):
    dst=Path(temporary)/"runtime"
    subprocess.run([sys.executable,"-IB",str(work/"bootstrap.py"),str(dst)],check=True,timeout=timeout)
    return subprocess.run([sys.executable,"-IB",str(work/name),str(dst)],
                          check=True,timeout=timeout,stdout=subprocess.PIPE,text=True).stdout


def regenerate(work):
    with tempfile.TemporaryDirectory(prefix="rounded-tier-build-") as temporary:
        output=run_worker(work,"receipt.py",temporary)
    result=json.loads(output)
    assert result["terminal"]["kappa"]=="77964201/20000000000"
    assert result["gaussian"]["transport_cells"]==63
    assert result["complete_log2_C"]==340530371
    (work/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("PASS_ROUNDED_TIERED_GAUSSIAN_PRICE",result["terminal"]["kappa"],flush=True)


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--peer",type=Path)
    parser.add_argument("--price",type=Path)
    parser.add_argument("--prototype",type=Path)
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--run",choices=("cost","interval","gaussian"))
    a=parser.parse_args()
    work=a.work.resolve()
    if a.run in ("interval","gaussian"):
        script="independent_price.py" if a.run=="interval" else "check_gaussian.py"
        with tempfile.TemporaryDirectory(prefix="rounded-tier-check-") as root:
            print(run_worker(work,script,root),end="")
    else:
        materialize(a.peer.resolve(),a.price.resolve(),a.prototype.resolve(),work)
        regenerate(work)
        if a.run=="cost":
            subprocess.run([sys.executable,"-IB",str(work/"verify.py"),"price"],check=True,timeout=60)
