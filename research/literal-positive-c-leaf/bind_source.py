"""Replay the exact current selected source/rank/positive-C normalization gate."""
from pathlib import Path
import copy
import gzip
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from check import authenticate, require


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result
    spec.loader.exec_module(result)
    return result


def main():
    source_count=authenticate()
    C=module('literal_c_compiler',HERE/'reference/clifford_exact.py')
    V=module('literal_c_independent',HERE/'reference/native_verify.py')
    raw=(HERE/'reference/selected-native.json.gz').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883',
            'selected source compressed pin')
    word=json.loads(gzip.decompress(raw))
    canonical=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(canonical=='91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097',
            'selected source semantic pin')
    event=word['program'][24472]
    require(event==['MOVE',415,3,99,False], 'actual selected occurrence')
    a=C.canonical_frame(9,tuple(word['frames'][3]))
    b=C.canonical_frame(9,tuple(word['frames'][99]))
    recipe,_=C.lower_child(a.adjoint().then(b))
    require(recipe['rank']==1, 'rank-one child')
    target=V.adjoint(V.frame(word['frames'][3],9))+V.frame(word['frames'][99],9)
    V.equal(V.recipe(recipe),target,'actual selected complete recipe')
    columns=[V.state(V.fourier(1),basis) for basis in (0,1)]
    require(columns==[({0:(1,1),1:(1,-1)},1),({0:(1,-1),1:(1,1)},1)],
            'positive C absolute normalization')
    wrong=copy.deepcopy(recipe);wrong['rank']=2
    try:
        V.equal(V.recipe(wrong),target,'wrong central rank')
    except ValueError:
        pass
    else:
        raise ValueError('rank mutant survived')
    require([V.state(V.adjoint(V.fourier(1)),b) for b in (0,1)]!=columns,
            'inverse C mistaken for positive C')
    print(json.dumps({'status':'PASS_LITERAL_C_CURRENT_SOURCE','event_index':24472,
          'event':event,'rank':1,'factor':'C tensor f, not f=1','source_files':source_count,
          'positive_C_columns':columns,'canonical_native_sha256':canonical,
          'recipe':recipe,'negative_controls':['wrong central rank','conjugate/inverse C'],
          'scope':'Source operator binding only; full MOVE and old-format/packing bridges remain supplied.'},
          indent=2,sort_keys=True))


if __name__=='__main__':
    main()
