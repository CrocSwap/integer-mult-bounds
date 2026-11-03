"""Reproduce baseline and price the fixed measured overlay before bank generation."""
from collections import Counter
import json
import reproduce_p10 as b
import price_candidate as p

def run():
    baseline=b.run()
    (b.HERE/'baseline-receipt.json').write_text(json.dumps(b.ae.serial(baseline),indent=2)+'\n')
    witness15=b.support.HERE/'witnesses/candidate15.json'
    fallback=json.loads(witness15.read_text())
    assert fallback['source_head']==b.HEAD and len(fallback['entries'])==15
    fallback_price=p.price(fallback['local_histogram_delta'],fallback['residual_family_delta'],label='Frozen candidate15 witness; bridge/finite binding is a separate stage')
    assert fallback_price['assembly']['kappa_decimal']=='0.000769208711124428'
    (b.HERE/'candidate15-pricing.json').write_text(json.dumps(b.ae.serial(fallback_price),indent=2)+'\n')
    census=json.loads((b.support.OUTPUT/'matching/full_path_census892.json').read_text())
    candidate=json.loads((b.support.HERE/'witnesses/candidate19-residue4.json').read_text())
    hd=Counter({int(k):n for k,n in census['helper_delta'].items()})
    hd.update({int(k):n for k,n in candidate['local_histogram_delta'].items()})
    rd=Counter({int(k):n for k,n in census['residual_delta'].items()})
    rd.update({int(k):n for k,n in candidate['residual_family_delta'].items()})
    weighted=p.price(dict(hd),dict(rd),label='Measured weighted892 path census plus fixed19; bridge/finite binding is a separate stage')
    (b.HERE/'provisional892-candidate19-pricing.json').write_text(json.dumps(b.ae.serial(weighted),indent=2)+'\n')
    return weighted
if __name__=='__main__':
    result=run();print(json.dumps({'status':result['status'],'kappa':result['assembly']['kappa_decimal'],'physical_admission':False},indent=2))
