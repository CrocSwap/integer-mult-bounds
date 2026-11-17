"""Fail-closed supervisor receipt binding; no service or science at import."""
import gzip,hashlib,json

def digest(raw):return hashlib.sha256(raw).hexdigest()
def physical_custody(result_raw,read_file,words=None):
    result=json.loads(result_raw)
    if words is None:words={'source':'b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238',
           'candidate':'1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'}
    logs={'verify_host3_odd','physical','physical_wrong_alpha2','rank9_physical_child'}
    for label,canonical in words.items():
        item=result['physical'][label];prefix='PHYSICAL-'+label.upper()+'/'
        if item['status']!='PASS_FINITE_PHYSICAL_ONLY' or item['word_canonical_sha256']!=canonical:raise ValueError('physical word identity')
        if read_file(prefix+'STARTED').decode().strip()!=canonical:raise ValueError('physical marker')
        gz=read_file(prefix+'word.json.gz')
        if digest(gz)!=item['word_gzip_sha256'] or digest(gzip.decompress(gz))!=canonical:raise ValueError('physical word bytes')
        if set(item['logs'])!=logs:raise ValueError('physical log inventory')
        for name,row in item['logs'].items():
            data=read_file(prefix+name+'.log')
            if row['returncode']!=0 or row['sha256']!=digest(data) or row['bytes']!=len(data):raise ValueError('physical log custody')
    return True
def finalize(record,started_raw,terminal_raw,result_raw,freeze_sha,post_auth_ok,group_empty,limits_ok,final_cpu_usec,final_memory_peak):
    """Preserve primary failures and append custody problems as secondary."""
    r=dict(record);errors=list(r.get('secondary_errors',[]))
    def check(ok,message):
        if not ok:errors.append(message)
    started=terminal=result=None
    try:
        started=json.loads(started_raw);terminal=json.loads(terminal_raw);result=json.loads(result_raw)
    except (ValueError,TypeError,UnicodeDecodeError):errors.append('missing or invalid driver artifacts')
    check(all(isinstance(x,dict) for x in (started,terminal,result)),'driver artifact shape')
    if all(isinstance(x,dict) for x in (started,terminal,result)):
        run_id=started.get('run_id');rh=digest(result_raw)
        check(isinstance(run_id,str) and len(run_id)==64,'invalid run ID')
        check(run_id==terminal.get('run_id')==result.get('run_id'),'run ID mismatch')
        check(started.get('freeze_sha256')==terminal.get('freeze_sha256')==result.get('freeze_sha256')==freeze_sha,'freeze mismatch')
        check(terminal.get('result_sha256')==rh,'result hash mismatch')
        check(terminal.get('status')=='SCOPED_GATE_RETURNED' and terminal.get('result_status')=='PASS_E4_INGREDIENT_NATIVE_ONLY' and result.get('status')=='PASS_E4_INGREDIENT_NATIVE_ONLY' and result.get('schema')=='e4-native-paired/v1','driver status mismatch')
        r.update(run_id=run_id,result_sha256=rh,started_sha256=digest(started_raw),driver_terminal_sha256=digest(terminal_raw),freeze_sha256=freeze_sha,result_status=result.get('status'))
    check(r.get('exit_code')==0,'driver exit failed')
    check(r.get('wall_killed') is False and r.get('cpu_killed') is False,'supervisor limit stop')
    check(type(r.get('execution_wall_seconds')) in (int,float) and 0<=r['execution_wall_seconds']<=4200,'execution wall missing or exceeded')
    check(post_auth_ok is True,'post authentication failed')
    check(group_empty is True,'cgroup not verified empty')
    check(limits_ok is True,'live limit readback failed')
    check(type(final_cpu_usec) is int and 0<final_cpu_usec<=3600*1000000,'final aggregate CPU missing or exceeded')
    check(type(final_memory_peak) is int and 0<final_memory_peak<=2*1024**3,'final peak memory missing or exceeded')
    r.update(post_authentication_pass=post_auth_ok is True,process_group_empty=group_empty is True,readback_limits_pass=limits_ok is True,
             aggregate_cpu_usec=final_cpu_usec,peak_memory_bytes=final_memory_peak,secondary_errors=errors)
    r['status']='PASS_SUPERVISED_INGREDIENT_NATIVE' if not r.get('error') and not errors else 'INCOMPLETE_OR_FAILED'
    return r
