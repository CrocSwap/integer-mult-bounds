import{mkdirSync,readFileSync,writeFileSync,copyFileSync,readdirSync,statSync}from'node:fs';
import{resolve,join}from'node:path';import{createHash}from'node:crypto';import{spawn}from'node:child_process';
const root=process.cwd(),pkg=resolve(import.meta.dir),work=process.argv[2];if(!work||!work.startsWith('/tmp/'))throw Error('fresh absolute /tmp work required');
const local=process.argv[3];if(!local)throw Error('source-bound native local directory required');
const source=join(root,'research/complex-k492-owner-repair/vendor/multicold'),vendor=join(source,'vendor/pr558/vendor/pr552/complex-global/vendor531'),old=join(root,'research/complex-t16-rare-pattern-exchanges');
const read=(p:string)=>JSON.parse(readFileSync(p,'utf8'));const sha=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
const write=(p:string,v:any)=>writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const cutoff=process.env.RESEARCH_DEADLINE_UTC?Date.parse(process.env.RESEARCH_DEADLINE_UTC):Date.now()+600000;mkdirSync(work);const src=join(work,'source');mkdirSync(src);
async function external(cmd:string,args:string[],log:string,env:any={}){if(Date.now()>cutoff)throw Error('search/replay deadline');const started=Date.now();const child=spawn(cmd,args,{cwd:root,env:{...process.env,...env},stdio:['ignore','pipe','pipe']});let output='';child.stdout.on('data',x=>output+=x);child.stderr.on('data',x=>output+=x);const timer=setTimeout(()=>child.kill('SIGTERM'),Math.min(240000,cutoff-Date.now()));const rc=await new Promise<number|null>(r=>child.on('exit',r));clearTimeout(timer);writeFileSync(log,output);if(rc!==0)throw Error(`${cmd} exit ${rc}: ${output.slice(-5000)}`);return{seconds:(Date.now()-started)/1000,log_sha256:sha(log)}}
await external('tar',['-xzf',join(old,'upstream1087.tar.gz'),'-C',src],join(work,'extract.log'));
const pins=read(join(src,'MANIFEST.json'));if(sha(join(src,'MANIFEST.json'))!==read(join(old,'SOURCE.json')).manifest_sha256)throw Error('archive manifest pin');for(const[p,h]of Object.entries(pins))if(sha(join(src,p))!==h)throw Error('archive pin '+p);
for(const[p,h]of Object.entries(read(join(src,'data/UPSTREAM-PINS.json'))))if(sha(join(root,p))!==h)throw Error('dependency pin '+p);
copyFileSync(join(pkg,'data/OWNERS.json.gz'),join(src,'data/OWNERS.json.gz'));
copyFileSync(join(old,'data/SPEC.json'),join(src,'data/SPEC.json'));
const spec=join(src,'data/SPEC.json'),spec8=join(src,'data/SPEC-T8.json');
const stages:any[]=[];const baseEnv={PYTHONDONTWRITEBYTECODE:'1',PYTHONUTF8:'1',PYTHONINTMAXSTRDIGITS:'0',MULTICOLD_SOURCE:source,GAIN_PR564_SOURCE:source};
async function run(name:string,script:string,args:string[],which=spec,extra:any={}){const info=await external('python3',['-B',join(source,'code/run_portable.py'),script,...args],join(work,name+'.log'),{...baseEnv,WITNESS_SPEC:which,WITNESS_DISCOVER:'0',...extra});stages.push({name,...info});write(join(work,'STAGES.json'),stages);console.log('PASS',name,info.seconds)}
const code=join(src,'code'),t16=join(src,'t16');
await run('restore-parent',join(code,'restore_parent.py'),['--source',source,'--baseline',join(root,'research/community-k492-audit/pr622/replay/baseline558'),'--out',join(work,'parent558')],spec8);
await run('bind8',join(code,'bind_providers_portable.py'),['--baseline',join(work,'parent558'),'--provider','gauge44='+local,'--plan',join(src,'data/T8/PLAN.json'),'--out',join(work,'global8')],spec8);
await run('lift16',join(t16,'lift16.py'),[join(work,'global8/base'),join(src,'data/T8/PLAN.json'),join(src,'data/T8/OWNERS.json.gz'),join(src,'data/OWNERS.json.gz'),join(work,'lift')],spec8);
copyFileSync(join(work,'lift/PLAN.json'),join(src,'data/PLAN.json'));copyFileSync(join(src,'data/PLAN.json'),join(pkg,'data/PLAN.json'));
{const s=read(spec);s.data.owners_sha256=sha(join(src,'data/OWNERS.json.gz'));s.data.plan_sha256=sha(join(src,'data/PLAN.json'));write(spec,s);}
await external('cp',['-a',join(work,'parent558'),join(work,'parent16')],join(work,'copy-parent.log'));
copyFileSync(join(work,'lift/GLOBAL-TEMPLATE.json.gz'),join(work,'parent16/complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz'));
for(const mode of['discovery','strict']){
 const g=join(work,mode),extra=mode==='discovery'?{WITNESS_DISCOVER:'1',WITNESS_RECORD:join(work,'WITNESS-RECORD.jsonl')}:{};
 await run(mode+'-bind',join(code,'bind_providers_portable.py'),['--baseline',join(work,'parent16'),'--provider','gauge44='+local,'--plan',join(src,'data/PLAN.json'),'--out',g],spec,extra);
 await run(mode+'-emit',join(code,'emit_allcold.py'),['--base',join(g,'base'),'--owners',join(src,'data/OWNERS.json.gz'),'--plan',join(g,'PLAN.json'),'--out',join(g,'hosted')],spec,extra);
 await run(mode+'-audit',join(code,'audit_allcold.py'),[join(g,'base'),join(g,'hosted'),join(g,'audit/ASYNC-AUDIT.json'),'--mutation-controls'],spec,extra);
 await run(mode+'-invoice',join(code,'invoice_allcold.py'),['--base',join(g,'base'),'--hosted',join(g,'hosted'),'--audit',join(g,'audit'),'--out',join(g,'audit'),'--retained-invoice',join(vendor,'evidence/audit/PREFIX-AND-INVOICE.json')],spec,extra);
 await run(mode+'-assembly',join(code,'assemble.py'),[source,g,join(g,'ASSEMBLY.json')],spec,extra);
 if(mode==='discovery'){
  const s=read(spec),records=readFileSync(join(work,'WITNESS-RECORD.jsonl'),'utf8').trim().split('\n').map(JSON.parse);for(const[k,v]of records){let parts=k.split('.');if(parts.length>3&&parts[0]==='providers'&&parts[2]==='artifacts')parts=[...parts.slice(0,3),parts.slice(3).join('.')];let o=s;for(const p of parts.slice(0,-1))o=o[p]??=( {});o[parts.at(-1)!]=v;}
  const a=read(join(g,'ASSEMBLY.json'));for(const k of['complex_lower','conservative_complex_lower','kappa','kappa_decimal','conservative_kappa_decimal'])s.expected[k]=a[k];write(spec,s);copyFileSync(spec,join(pkg,'data/SPEC.json'));
 }else{
  await run('admission-controls',join(code,'assembly_controls.py'),['--source-package',source,'--owner',join(g,'audit/OWNERS-AND-PROFILE.json'),'--invoice',join(g,'audit/PREFIX-AND-INVOICE.json'),'--out',join(g,'ADMISSION-CONTROLS.json')]);
  await run('bit-controls',join(code,'bit_supplier_controls.py'),['--source-package',source,'--owner',join(g,'audit/OWNERS-AND-PROFILE.json'),'--invoice',join(g,'audit/PREFIX-AND-INVOICE.json'),'--out',join(g,'BIT-SUPPLIER-CONTROLS.json')]);
  const s=read(spec);await run('independent-t16',join(t16,'indep16.py'),['--baseline-parent',join(work,'global8/base/split-centres/GLOBAL-TEMPLATE.json.gz'),'--owners',join(src,'data/OWNERS.json.gz'),'--word',join(local,'CANONICAL-WORD.json.gz'),'--out',join(g,'INDEPENDENT-T16.json')],spec,{T16_EXPECTED_IDLE:JSON.stringify(s.expected.idle_remainder_profile),T16_EXPECTED_WIDTHS:JSON.stringify(s.providers.gauge44.inventory)});
 }
}
console.log('PASS_CHANGED_HOSTING_REPLAY',read(join(work,'strict/ASSEMBLY.json')).kappa_decimal);
