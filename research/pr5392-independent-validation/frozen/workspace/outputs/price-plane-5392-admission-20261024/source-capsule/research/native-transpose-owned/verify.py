"""Check the owned transpose, physical phases and complete conditional bound.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse,gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from support import authenticate,read,need,packed

def run():
    source=authenticate()
    import word,interface,phases,price
    from check_certificate import check
    native,emitted,problem=word.run(source)
    check(problem,native['native'])
    print('PASS_TRANSPOSE_ALL_INPUTS_AND_NATIVE_CHECKER',flush=True)
    boundary=interface.run()
    physical=phases.run(source)
    print('PASS_TRANSPOSE_ALL_PHYSICAL_CLASSES',flush=True)
    b=native['source_replay']
    f=dict(b,real_scalar_allowance=native['real_scalar_allowance'],
           max_formal_prefix_l1=native['transpose']['max_formal_prefix_l1'],
           max_denominator=native['transpose']['max_denominator'])
    arithmetic=price.run({'forward':f,'backward':b})
    result={'status':'PASS_CONDITIONAL_KAPPA_00302725_OWNED_TRANSPOSE',
            'native':native,'interface':boundary,'physical':physical,'arithmetic':arithmetic}
    return result,emitted,problem

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Write this package after every check passes')
    args=parser.parse_args()
    result,emitted,problem=run()
    artifacts={'RESULT.json':result,'WORD.json.gz':emitted,'NATIVE-PROBLEM.json.gz':problem,
               'NATIVE-CERTIFICATE.json':result['native']['native']}
    for name,value in artifacts.items():
        path=HERE/name
        if args.write:
            data=packed(value)
            path.write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
        else:need(read(path)==json.loads(packed(value)),'Exact committed artifact: '+name)
    print(result['status'],flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
