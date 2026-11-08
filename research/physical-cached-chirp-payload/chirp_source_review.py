"""Independent half-angle review of the source producer's actual dyadic tables.

The supplied ``make_interval_oracle`` is used only to run the producer.  All
expected roots are enclosed by the separate integer-square-root implementation.
Prepared for @CubeJerry with separate source-aware OpenAI verification.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util


def _load_oracle():
    path=Path(__file__).with_name('dyadic_chirp_oracle.py')
    spec=importlib.util.spec_from_file_location('independent_dyadic_root_review',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(producer,make_interval_oracle):
    """Certify five finite source families, all conjugates and six bad joins.

    The factory must supply a fresh authenticated producer interval module for
    each call.  Its numerical functions never enter the expected-root oracle.
    """
    oracle=_load_oracle()
    cases=(
        ((8,4),(7,3),1,10,0),
        ((16,8,2),(-3,5,-7),3,14,27),
        ((32,4,8),(63,-15,103),2,12,0),
        ((2,),(-1,),1,0,0),
        ((256,2),(10**30+1,-3),2,11,0),
    )
    receipts=[];controls=[]
    for ordinal,(radices,slopes,radius,target,incoming) in enumerate(cases):
        bundle=producer.prepare(radices,slopes,radius,target,
            oracle=make_interval_oracle(),incoming_precision=incoming)
        check=oracle.check_tables(radices,slopes,bundle.tables,bundle.plan.f)
        receipts.append(dict(radices=radices,slopes=slopes,radius=radius,
            target=target,incoming_precision=incoming,source=bundle.receipt(),
            independent=check))
        if ordinal==0:
            t,s=radices[0],slopes[0]
            a,b=bundle.tables[0][1];p=bundle.plan.f
            wrong='proved chirp component error exceeds two ulp'
            tests=(
                ('conjugation_sign',lambda:oracle.check_row(t,s,1,a,-b,p),wrong),
                ('denominator_factor_two',lambda:oracle.check_row(t//2,s,1,a,b,p),wrong),
                ('wrong_odd_slope',lambda:oracle.check_row(t,s+2,1,a,b,p),wrong),
                ('square_coordinate',lambda:oracle.check_row(t,s,2,a,b,p),
                    'exact quarter-root encoding'),
                ('outside_unit_disk',lambda:oracle.check_row(t,s,0,(1<<p)+1,0,p),
                    'exact dyadic unit disk'),
                ('axis_slope_association',lambda:oracle.check_tables(
                    radices,(slopes[1],slopes[0]),bundle.tables,p),wrong),
            )
            for name,operation,expected in tests:
                try:operation()
                except ValueError as error:
                    oracle.need(str(error)==expected,
                        'specific decisive independent rejection: '+name)
                    controls.append(dict(name=name,rejection=str(error)))
                else:raise ValueError('negative control escaped: '+name)
            oracle.check_row(t,s+2*t,1,a,b,p)
    return dict(producer_sha256=sha256(Path(producer.__file__).read_bytes()).hexdigest(),
        oracle_sha256=sha256(Path(oracle.__file__).read_bytes()).hexdigest(),
        cases=receipts,negative_controls=controls,selfcheck=oracle.selfcheck())
