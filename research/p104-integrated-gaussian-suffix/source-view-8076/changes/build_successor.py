"""Install the six-column Gaussian offset atop the authenticated #8076 runtime."""
from hashlib import sha256
from pathlib import Path
from shutil import copyfile,copytree
from fractions import Fraction as Q
import json

root=Path(__file__).resolve().parent
candidate=root/'successor'
base=root/'runtime'
dest=candidate/'runtime'
source=root/'peer/research/frequency-weighted-native-multiplier'
checks=candidate/'peer/research/frequency-weighted-native-multiplier'
changes={}


def write(path,d,old,new,count=1):
    if d.count(old)!=count:raise ValueError((str(path),old,d.count(old),count))
    return d.replace(old,new)


def adjust(path,seq):
    d=path.read_text()
    before=sha256(path.read_bytes()).hexdigest()
    for old,new,*num in seq:d=write(path,d,old,new,*num)
    path.write_text(d)
    changes[str(path.relative_to(candidate))]={"before_sha256":before,"after_sha256":sha256(path.read_bytes()).hexdigest()}


def main():
    candidate.mkdir(exist_ok=True)
    copytree(base,dest,dirs_exist_ok=True,ignore=lambda p,n: {'__pycache__'})
    copytree(root/'peer',candidate/'peer',dirs_exist_ok=True,ignore=lambda p,n: {'__pycache__'})
    typed=dest/'typed_transport.py'
    adjust(typed,[
        ('from dataclasses import dataclass','from dataclasses import dataclass\nfrom math import gcd'),
        ('    def __init__(\n        self,','    column_offset = 8\n\n    def __init__(\n        self,'),
        ('        width=None,','        width=None,\n        column_offset=8,'),
        ('        if len(types) != 2 or lower <= 8', '''        if type(column_offset) is not int or column_offset < 0 or column_offset > 8 or column_offset % 2:
            raise ValueError("Use a nonnegative even column offset of at most eight")
        self.column_offset = column_offset
        if len(types) != 2 or lower <= column_offset'''),
        ('            owners = ids[b, k]','''            if column_offset < 8:
                rr, kk = Q(2*r), Q(2*k)
                if rr.denominator != 1 or kk.denominator != 1 or column_offset*(k-r) < rr-gcd(rr.numerator,kk.numerator):
                    raise ValueError("A routed prefix can exceed its real paid field")
            owners = ids[b, k]'''),
        ('upper - 8','upper - self.column_offset'),
        ('e - 8','e - self.column_offset',4),
        ('band - 8','band - self.column_offset',3)])
    adjust(dest/'grades.py',[('LOWER = 1874','LOWER = 1054'),('            width=self.width,','            width=self.width,\n            column_offset=6,')])
    adjust(dest/'installations.py',[('Profile((8192, 111681, 524288), 509812, Q(".003898223617430"))','Profile((8192, 118919, 524288), 499284, Q(".003898226579820971"))')])
    independent=checks/'positive_debit.py'
    adjust(independent,[
      ('from fractions import Fraction as Q','from fractions import Fraction as Q\nfrom math import gcd'),
      ('BAND_LOWER = 1874','BAND_LOWER = 1054'),('Q(64939, 524288)','Q(125645,1048576)'),
      ('    fringe = 10 * target_axes / (t * psi)','''    # Nonempty interior grants are rounded down. The full proof bounds
    # the y-integral of the integer paid suffix after y=x*r/k.
    contributions = Q(0)
    needed = Q(0)
    for (r,k),share in cells.items():
        r,k=Q(r),Q(k)
        r2,k2=int(2*r),int(2*k)
        assert 2*r == r2 and 2*k == k2
        needed=max(needed,(2*r-gcd(r2,k2))/(k-r))
        ratio_upper=Q(intervals(r,t)[1],intervals(k,t)[0])
        mean=7*(k-r)+t*r*r/(2*k*lower)
        contributions += paid[r]*share*ratio_upper*mean
    assert needed==Q(94,17)<6
    fringe=contributions/(t*psi)'''),
      ('Q("7.335168")','Q("3.539446")'),('(upper - 8)','(upper - 6)')])
    adjust(checks/'receipt.py',[('Q(64939, 2**19)', 'Q(125645,1048576)'), ('LOWER == 1874', 'LOWER == 1054'), ('cost == 318291900 and premium == 518', 'cost == 318291900 and premium == 516'), ("late['log2_B'] == 206131657", "late['log2_B'] == 208447817"), ('(516124, 509812)', '(516703, 499284)'), ('older = Q(".003898219753506")', 'older = Q(".003898223617430")'), ('Q(965981, 250000000000000)', 'Q(2962390971, 1000000000000000000)'), ('Q(1361743, 100000000000000)', 'Q(16579820971, 1000000000000000000)'), ('Q(523210198560303585338978849681, 134217728000000000000000000000000)', 'Q(1667119388378402860472786027, 427661302169600000000000000000)')])
    adjust(checks/'check_placement.py',[('size = 258 * (e - 8)','size = 258 * (e - 6)')])
    adjust(checks/'check_exterior.py',[
       ('    L = 10\n    U = 12','    L = 8\n    U = 10'),
       ('    assert 4 * U < 5 * L','    assert 4 * U <= 5 * L'),
       ('        def __init__(self):\n','        column_offset = 6\n\n        def __init__(self):\n'),
       ('size = (L - 8) * k','size = (L - 6) * k'),
       ('true[owner] = (2 * k, ext.period)','true[owner] = ((L-p.column_offset) * k, ext.period)'),
       ('cols = 2 * (1 + kind)','cols = (L-p.column_offset) * (1 + kind)')])
    # One actual linked packet at e=22, d=10 retains the dense predecessor's
    # physical widths 16 and 4. Check both typed headers at the new origin.
    adjust(checks/'check_nested.py',[
       ('    grant = (','''    from typed_transport import column_header
    parent_bin, child_bin, offset = 22, 10, 6
    rr, kk = 1, 2
    grant_lo = max(parent_bin, Q(child_bin*kk,rr))
    grant_hi = min(parent_bin+2, Q((child_bin+2)*kk,rr))
    assert (grant_lo,grant_hi)==(22,24)
    grant = ('''),
       ('.mass(24, 26)[0]','.mass(grant_lo, grant_hi)[0]'),
       ('4_400_000_000 < grant.numerator // grant.denominator < 4_600_000_000','5_000_000_000 < grant.numerator // grant.denominator < 6_000_000_000'),
       ('and 24 * 1 == 12 * 2','and grant_lo < grant_hi'),
       ('    P = 16\n    S = 8','''    P = column_header(parent_bin-offset,0)
    child_header = column_header(child_bin-offset,1)
    S = 2*(child_header-1)
    assert (P,S,child_header)==(16,8,5)'''),
       ('method.native(cr, S // 2 + 1)','method.native(cr, child_header)')])
    # Exercise the new mode in generic dirty calendar and all owners too.
    adjust(checks/'check_calendar.py',[('        padding=1,','        padding=1,\n        column_offset=6,'),
       ('        192,','        196,')])
    adjust(checks/'check_ownership.py',[('        padding=1,','        padding=1,\n        column_offset=6,'),
       ('e - 8','e - 6',5)])
    (candidate/'delta-pins.json').write_text(json.dumps(changes,indent=2)+'\n')
    print('REGISTERS',len(changes))


if __name__=='__main__':main()
