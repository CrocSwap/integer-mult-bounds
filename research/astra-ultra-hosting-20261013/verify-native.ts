/** Frozen construction replay. New orchestration only; all mathematical gates are pinned predecessor code. */
import{readFileSync,writeFileSync,mkdirSync,copyFileSync}from'node:fs';import{resolve,join}from'node:path';import{createHash}from'node:crypto';import{spawn}from'node:child_process';
const root=resolve(import.meta.dir,'../..'),pkg=import.meta.dir,[localArg,workArg]=process.argv.slice(2);if(!localArg||!workArg)throw Error('usage: bun verify-native.ts CHECKED_NATIVE_LOCAL FRESH_OUTPUT');
const local=resolve(localArg),work=resolve(workArg),src=join(work,'source'),old=join(root,'research/complex-t16-rare-pattern-exchanges');
const sha=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');const read=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
const deadline=process.env.RESEARCH_DEADLINE_UTC?Date.parse(process.env.RESEARCH_DEADLINE_UTC):Date.now()+480000;if(!Number.isFinite(deadline)||deadline<=Date.now())throw Error('expired/invalid deadline');
mkdirSync(work);mkdirSync(src);
async function run(cmd:string,args:string[],log:string){const child=spawn(cmd,args,{cwd:root,detached:true,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},stdio:['ignore','pipe','pipe']});let output='';child.stdout.on('data',x=>{output+=x;process.stdout.write(x)});child.stderr.on('data',x=>{output+=x;process.stderr.write(x)});const timer=setTimeout(()=>{try{process.kill(-child.pid!,'SIGTERM')}catch{}},deadline-Date.now());const rc=await new Promise<number|null>(r=>child.on('exit',r));clearTimeout(timer);writeFileSync(join(work,log),output);if(rc!==0)throw Error(`${cmd} exit ${rc}`)}
await run('tar',['-xzf',join(old,'upstream1087.tar.gz'),'-C',src],'extract.log');
if(sha(join(src,'MANIFEST.json'))!==read(join(old,'SOURCE.json')).manifest_sha256)throw Error('archive manifest pin');for(const[p,h]of Object.entries(read(join(src,'MANIFEST.json'))))if(sha(join(src,p))!==h)throw Error('archive source pin '+p);
const candidate=read(join(pkg,'RESULT.json'));for(const name of['OWNERS.json.gz','PLAN.json','SPEC.json']){if(sha(join(pkg,'data',name))!==candidate.candidate_data_sha256[name])throw Error('candidate pin '+name);copyFileSync(join(pkg,'data',name),join(src,'data',name))}
await run('python3',['-B',join(src,'verify_t16.py'),'--main',root,'--local',local,'--work',join(work,'strict')],'native.log');
const r=read(join(work,'strict/REPLAY.json'));if(r.status!=='PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'||r.kappa!==candidate.kappa)throw Error('final result mismatch');console.log('PASS_FROZEN_HOSTING_GAIN',r.kappa_decimal);
