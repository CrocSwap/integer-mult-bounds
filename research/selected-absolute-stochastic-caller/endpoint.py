"""Decode the numerical endpoint with the independent source coordinate code."""

import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,label):
    if not ok:
        raise ValueError(label)


def main():
    need(__debug__, 'source assertions enabled')
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'], 'source bytes')
    sys.path.insert(0,str(ROOT/'research/staged544-mixed-fourth-entry/native/vendor/native/new/code/borrow'))
    import bw_gauss
    folder=Path(sys.argv[1]);data=json.loads((folder/'fixture.json').read_text())
    word=json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    def decode(values,frame):
        need(len(values)==512 and max(abs(v) for z in values for v in z) < 1 << 30, 'oracle integer input bound')
        x=np.array(values,dtype=np.int64)
        a,b,d=bw_gauss.frame((x[:,0,None],x[:,1,None],0),word['frames'][frame],9,-1)
        need(d<=9, 'source frame denominator')
        return [(Q(int(r),1 << d),Q(int(i),1 << d)) for r,i in zip(a[:,0],b[:,0])]
    initial=[decode(data['initial'][str(r)],frame) for r,frame in enumerate(word['initial'])]
    errors=[]
    for r,frame in enumerate(word['final']):
        actual=decode(data['output'][str(r)],frame)
        other=initial[r-112] if r-112 in word['live'] else [(Q(0),Q(0))]*512
        err=sum((x-a-c)**2+(y-b-d)**2 for (x,y),(a,b),(c,d) in zip(actual,initial[r],other))
        errors.append(err)
    tensor=json.loads((folder/'tensor-fixture.json').read_text())
    values=np.array(tensor['initial'],dtype=np.int64)
    re,im=values[:,0].reshape(512,512),values[:,1].reshape(512,512)
    old,new=tensor['edge']
    for axis in range(2):
        if axis==0:
            re,im=re.T,im.T
        need(np.max(np.abs(re)) < 1 << 25 and np.max(np.abs(im)) < 1 << 25,
             'tensor oracle integer input bound')
        re,im,exponent=bw_gauss.frame(bw_gauss.frame((re,im,0),word['frames'][old],9,-1),
                                    word['frames'][new],9)
        need(exponent<=18 and np.all(re % (1 << exponent)==0) and
             np.all(im % (1 << exponent)==0), 'exact tensor grid')
        re,im=re//(1 << exponent),im//(1 << exponent)
        if axis==0:
            re,im=re.T,im.T
    actual=np.array(tensor['output'],dtype=np.int64)
    need(np.array_equal(re.reshape(-1),actual[:,0]) and np.array_equal(im.reshape(-1),actual[:,1]),
         'independent full tensor operator')
    (folder/'endpoint.json').write_text(json.dumps({'decoded_public_fields':len(errors),
        'max_squared_error':[str(max(errors)),errors.index(max(errors))],
        'squared_errors':[str(v) for v in errors],
        'independent_tensor_coordinates':len(actual),
        'source_assertions_enabled':__debug__},indent=2)+'\n')


if __name__=='__main__':
    main()
