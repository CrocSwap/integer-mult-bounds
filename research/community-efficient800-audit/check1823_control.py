"""Check actual sign reversal separately from submitted omitted-unload control."""
import importlib.util, pathlib, hashlib, json
p=pathlib.Path('/tmp/pr-efficient800/sources/1823/research/compact-agreement-set-seed29/verify.py')
s=importlib.util.spec_from_file_location('reviewed1823',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
n,K,G,rho=2,5,1,4
y,t,c=4240,0,0
assert m.guard_temp_target(y,t,n,K,G,rho)
y1,t1=m.step_E(c,y,t,n,K,G,rho)
assert (y1,t1)==(m.ideal_y(y,c,n,K,rho),t)
off=sum((((y1>>(rho+i*K))&1)^((c>>i)&1))<<(i*G) for i in range(n))
mask=(1<<(n*G))-1
omitted=(t1+off)&mask
reversed_sign=(t1+2*off)&mask
assert omitted != t and reversed_sign != t
print(json.dumps(dict(status='PASS_ACTUAL_SIGN_REVERSED_UNLOAD_REJECTED',input=[y,t,c],unload=off,correct_t=t1,omitted_t=omitted,sign_reversed_t=reversed_sign,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Submitted t1+off control omits the unloading rather than reversing it. The actual sign reversal is t1+2*off and also violates restoration in the same guarded fixture. Main census unchanged.')))
