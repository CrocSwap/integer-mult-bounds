"""Price #1005's global profile plus (local delta x calls), with saved rank mass as rank-48 idle (ideal packing)."""
import json,sys,subprocess,os
base={1:174763,2:30105,3:30275,4:12240,5:4896,7:54,8:576,16:23,48:2419}
def price(dH,calls=72,tag='x'):
    H=dict(base)
    for r,x in dH.items():H[int(r)]=H.get(int(r),0)+calls*x
    mass=sum(r*x for r,x in H.items());dm=520704-mass
    H[48]+=dm//48
    if dm%48:H[dm%48]=H.get(dm%48,0)+1
    p=__import__('os').environ.get('PC_OUT','.')+'/price-%s.json'%tag;json.dump({'profile':{str(k):v for k,v in sorted(H.items()) if v}},open(p,'w'))
    o=__import__('os').environ.get('PC_OUT','.')+'/price-%s.out.json'%tag
    subprocess.run([__import__('sys').executable,'-B',__import__('os').environ['PC_MAIN']+'/research/gauge44-leaver8/independent/price_profile.py','--main',__import__('os').environ['PC_MAIN'],'--profile',p,'--output',o],check=True,capture_output=True)
    return json.load(open(o))['prices']['native']['outer_with_bit']['kappa_decimal']
if __name__=='__main__':
    print('base',price({},tag='base'))
    print('one key x1',price({1:8,2:-4,3:-2,6:-2},tag='k1'))
