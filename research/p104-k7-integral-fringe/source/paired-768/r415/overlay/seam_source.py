"""Adapt the authenticated #8094 seam checker to the fixed-height tariff edit."""

from hashlib import sha256
from pathlib import Path


SOURCE_SHA256 = "b790eb6855afa255a609eaaf88a46ed9e8b04232671cca4d0f8bd0bad27f11ac"


def patch_stage_checks(peer: Path) -> None:
    path = peer / "check_stage_seam.py"
    original = path.read_bytes()
    if sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("The exact #8094 check_stage_seam.py is required")
    source = original.decode("utf-8")
    replacements = (
        (
            "    ORDINARY=Q(1420718,2**20)       # floor retune + child tariff + no 256/255 (unchanged by the Gaussian word)",
            """    OLD_ORDINARY=Q(1420718,2**20)
    ORDINARY=Q(1414404,2**20)  # tariff 2391/1024, same floor and fringe
    OLD_KAPPA=Q(".003900857267786")
    GRID=Q(1,10**15)""",
        ),
        (
            '    assert TERMINAL.kappa==Q(".003900857267786")',
            '    assert TERMINAL.kappa==Q(".003900857269150")',
        ),
        (
            """    assert ordinary_upper(ranks)>paid and gaussian_upper(TERMINAL.complex_log)>paid
    # The ordinary side binds: the install is the 15-digit floor of its rate.
    assert TERMINAL.kappa<=ordinary_upper(ranks)-5*STOP<TERMINAL.kappa+Q(1,10**15)""",
            """    assert ordinary_upper(ranks)>gaussian_upper(TERMINAL.complex_log)>paid
    old_crossing=ordinary_upper(ranks,OLD_ORDINARY)-5*STOP
    assert OLD_KAPPA<=old_crossing<OLD_KAPPA+GRID
    assert TERMINAL.kappa>old_crossing
    assert TERMINAL.kappa+GRID>=gaussian_upper(TERMINAL.complex_log)-5*STOP""",
        ),
        (
            """    def require_funding(proposed,gaussian):
        if ordinary_upper(proposed)<=paid or gaussian_upper(gaussian)<=paid:""",
            """    def require_funding(proposed,gaussian,*,debit=ORDINARY,kappa=TERMINAL.kappa):
        threshold=kappa+5*STOP
        if ordinary_upper(proposed,debit)<=threshold or gaussian_upper(gaussian)<=threshold:""",
        ),
        (
            """    # The install is the 15-digit floor of the rate, so the lower heights carry
    # slack: DROPS[i] is the first drop of height i that falls below the booking.
    DROPS=[917, 943, 944, 944, 5]
    for i,d in enumerate(DROPS):
        require_funding(at(i,-(d-1)),TERMINAL.complex_log)
    assert ordinary_upper(previous_record[0])<ordinary_upper(ranks)
    controls=[rejected(lambda i=i,d=d:require_funding(at(i,-d),TERMINAL.complex_log),f"ordinary-height-{i}-minus-{d}")
              for i,d in enumerate(DROPS)]""",
            """    # These height drops describe the old ordinary-limited booking.
    def require_old_funding(proposed,gaussian):
        require_funding(proposed,gaussian,debit=OLD_ORDINARY,kappa=OLD_KAPPA)

    DROPS=[917, 943, 944, 944, 5]
    for i,d in enumerate(DROPS):
        require_old_funding(at(i,-(d-1)),TERMINAL.complex_log)
    assert ordinary_upper(previous_record[0],OLD_ORDINARY)<ordinary_upper(ranks,OLD_ORDINARY)
    controls=[rejected(lambda i=i,d=d:require_old_funding(at(i,-d),TERMINAL.complex_log),f"old-ordinary-height-{i}-minus-{d}")
              for i,d in enumerate(DROPS)]""",
        ),
        (
            """        rejected(lambda:require_funding(*previous_record),"pr8090-profile-at-new-rate"),
        rejected(lambda:require_funding(*capped),"capped-combined-profile-at-new-rate"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log-1),"gaussian-height-minus-one"),""",
            """        rejected(lambda:require_old_funding(*previous_record),"pr8090-profile-at-old-booking"),
        rejected(lambda:require_old_funding(*capped),"capped-combined-profile-at-old-booking"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log-1),"gaussian-height-minus-one"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),
                 "next-displayed-kappa-at-fixed-gaussian-height"),""",
        ),
        (
            "                neighbours.append(ordinary_upper((*t,max_penultimate(t),TOP)))",
            "                neighbours.append(ordinary_upper((*t,max_penultimate(t),TOP),OLD_ORDINARY))",
        ),
        (
            "    assert all(n<=ordinary_upper(ranks) for n in neighbours)",
            "    assert all(n<=ordinary_upper(ranks,OLD_ORDINARY) for n in neighbours)",
        ),
    )
    for old, new in replacements:
        if source.count(old) != 1:
            raise ValueError("A stage-check source anchor was missing or repeated")
        source = source.replace(old, new, 1)
    compile(source, str(path), "exec")
    path.write_text(source, encoding="utf-8")
