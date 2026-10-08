// Independent global assembly: one local producer per common pair C, exact
// support identification across contexts, pruning, four-point star
// resynthesis by greedy disjoint CSE, and (small h) a full coefficient check.
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <cstdint>
#include <vector>
#include <array>
#include <map>
#include <set>
#include <unordered_map>
#include <algorithm>
#include <tuple>
using namespace std;
typedef uint32_t U; typedef uint64_t V;

struct K7 { array<V,7> x{}; bool operator==(const K7&o)const{return x==o.x;} };
struct HK { size_t operator()(const K7&k)const{ V h=1469598103934665603ULL; for(V y:k.x){ y*=0x9E3779B97F4A7C15ULL; y^=y>>29; h=(h^y)*1099511628211ULL; } return h; } };

int h, n, ni;
vector<array<int,3>> trip; // local triples
int main(int argc,char**argv){
  h=atoi(argv[1]); const char* lf=argv[2]; int absorb = argc>3 ? atoi(argv[3]) : 1;
  FILE* f=fopen(lf,"r"); int na; fscanf(f,"%d %d %d",&n,&ni,&na); assert(n==h-2);
  trip.resize(ni); for(auto&t:trip) fscanf(f,"%d %d %d",&t[0],&t[1],&t[2]);
  vector<array<int,3>> ladd(na); int maxid=ni;
  for(auto&r:ladd){ fscanf(f,"%d %d %d",&r[0],&r[1],&r[2]); maxid=max(maxid,r[0]); }
  vector<pair<array<int,3>,int>> lout(ni); for(auto&o:lout) fscanf(f,"%d %d %d %d",&o.first[0],&o.first[1],&o.first[2],&o.second);
  int ltotal; fscanf(f,"%d",&ltotal); fclose(f);
  // local supports (as bitsets over ni) and local cores
  int W=(ni+63)/64; unordered_map<int,int> pos; vector<vector<V>> sup; vector<U> lcore;
  auto getpos=[&](int id)->int{ auto it=pos.find(id); assert(it!=pos.end()); return it->second; };
  for(int i=0;i<ni;i++){ pos[i+1]=sup.size(); vector<V> s(W,0); s[i/64]|=1ULL<<(i%64); sup.push_back(s);
    lcore.push_back((1U<<trip[i][0])|(1U<<trip[i][1])|(1U<<trip[i][2])); }
  for(auto&r:ladd){ int a=getpos(r[1]), b=getpos(r[2]); vector<V> s(W);
    for(int w=0;w<W;w++){ assert(!(sup[a][w]&sup[b][w])); s[w]=sup[a][w]|sup[b][w]; }
    pos[r[0]]=sup.size(); sup.push_back(s); lcore.push_back(lcore[a]&lcore[b]); }
  // sanity: local output supports exact
  for(auto&o:lout){ int p=getpos(o.second); U E=(1U<<o.first[0])|(1U<<o.first[1])|(1U<<o.first[2]);
    for(int i=0;i<ni;i++){ U t=(1U<<trip[i][0])|(1U<<trip[i][1])|(1U<<trip[i][2]); bool in=(sup[p][i/64]>>(i%64))&1; assert(in==((t&E)==0)); } }
  // residual lists per local node with nonempty local core
  int L=sup.size(); vector<vector<U>> resid(L); // for core1: pairs of local points (a*32+b); core2: single point
  for(int p=ni;p<L;p++){ int c=__builtin_popcount(lcore[p]); if(c==0) continue;
    for(int i=0;i<ni;i++) if((sup[p][i/64]>>(i%64))&1){ U t=((1U<<trip[i][0])|(1U<<trip[i][1])|(1U<<trip[i][2]))&~lcore[p];
      int a=__builtin_ctz(t); t&=t-1; if(c==1){ int b=__builtin_ctz(t); resid[p].push_back(a*32+b);} else resid[p].push_back(a); } }
  // global 5-sets
  unordered_map<U,U> fid; vector<U> fmask; fmask.push_back(0);
  for(U m=0;m<(1U<<h);m++) if(__builtin_popcount(m)==5){ fid[m]=fmask.size(); fmask.push_back(m);}
  int v=fmask.size()-1; int pidx[32][32]; int q=0; for(int a=0;a<h;a++)for(int b=a+1;b<h;b++){pidx[a][b]=pidx[b][a]=q++;}
  vector<array<U,2>> args(v+1,{0,0}); vector<U> core(v+1); for(int i=1;i<=v;i++) core[i]=fmask[i];
  vector<U> starm(v+1,0); // for core-4 nodes, residual point mask
  unordered_map<K7,U,HK> m3; unordered_map<V,U> m4; if(h==28){ m3.reserve(7000000); m4.reserve(4000000);}
  vector<U> roots; vector<array<U,4>> rootinfo; // (C mask, E mask or 0 for total, id)
  long long instances=0;
  for(int ca=0;ca<h;ca++)for(int cb=ca+1;cb<h;cb++){
    U C=(1U<<ca)|(1U<<cb); vector<int> ord;
    for(int x=0;x<h;x+=2) if(!(C>>x&1) && !(C>>(x+1)&1)){ ord.push_back(x); ord.push_back(x+1);}
    for(int x=0;x<h;x++) if(!(C>>x&1) && (C>>(x^1)&1)) ord.push_back(x);
    assert((int)ord.size()==n);
    auto mapm=[&](U lm){ U g=0; while(lm){int i=__builtin_ctz(lm); lm&=lm-1; g|=1U<<ord[i];} return g; };
    vector<U> gid(L);
    for(int i=0;i<ni;i++) gid[i]=fid.at(C|mapm(lcore[i]));
    for(int p=ni;p<L;p++){ instances++;
      U gc=C|mapm(lcore[p]); int nc=__builtin_popcount(gc); int a=gid[getpos(ladd[p-ni][1])], b=gid[getpos(ladd[p-ni][2])];
      U id;
      if(nc==2){ id=args.size(); args.push_back({(U)a,(U)b}); core.push_back(gc); starm.push_back(0);}
      else if(nc==3){ K7 k; k.x[6]=gc; for(U r:resid[p]){ int i=pidx[ord[r/32]][ord[r%32]]; k.x[i/64]|=1ULL<<(i%64);}
        auto it=m3.find(k); if(it!=m3.end()) id=it->second; else { id=args.size(); m3.emplace(k,id); args.push_back({(U)a,(U)b}); core.push_back(gc); starm.push_back(0);} }
      else { assert(nc==4); U rm=0; for(U r:resid[p]) rm|=1U<<ord[r]; V k=((V)gc<<32)|rm;
        auto it=m4.find(k); if(it!=m4.end()) id=it->second; else { id=args.size(); m4.emplace(k,id); args.push_back({(U)a,(U)b}); core.push_back(gc); starm.push_back(rm);} }
      gid[p]=id; }
    for(auto&o:lout){ U E=mapm((1U<<o.first[0])|(1U<<o.first[1])|(1U<<o.first[2])); int p=getpos(o.second); roots.push_back(gid[p]); rootinfo.push_back({C,E,0,0}); }
    roots.push_back(gid[getpos(ltotal)]); rootinfo.push_back({C,0,1,0});
  }
  m3.clear(); m3.rehash(0); m4.clear(); m4.rehash(0);
  size_t N=args.size(); long long unique_adds=N-v-1;
  vector<char> act(N,0); vector<U> st(roots.begin(),roots.end()); long long actadds=0, actin=0;
  while(!st.empty()){U x=st.back(); st.pop_back(); if(act[x])continue; act[x]=1; if(args[x][0]){actadds++; assert(args[x][0]<x&&args[x][1]<x); st.push_back(args[x][0]); st.push_back(args[x][1]);} else actin++;}
  printf("{\"h\":%d,\"local_instances\":%lld,\"unique_additions\":%lld,\"active_additions\":%lld,\"active_inputs\":%lld,\"roots\":%zu}\n",h,instances,unique_adds,actadds,actin,roots.size());
  // stars
  map<U,long long> starsize; map<U,vector<U>> demand; vector<char> isdem(N,0);
  for(size_t x=v+1;x<N;x++) if(act[x]){ if(__builtin_popcount(core[x])==4) starsize[core[x]]++;
    for(int j=0;j<2;j++){ U c=args[x][j]; if(args[c][0] && __builtin_popcount(core[c])==4 && core[c]!=core[x]) isdem[c]=1; } }
  for(U r:roots) if(args[r][0] && __builtin_popcount(core[r])==4) isdem[r]=1;
  for(size_t x=v+1;x<N;x++) if(isdem[x]) demand[core[x]].push_back(starm[x]);
  // every star node lies under a demanded node? (star sizes counted for all active core-4 nodes)
  map<vector<U>,vector<pair<U,U>>> cache; long long oldst=0,newst=0;
  map<U,vector<pair<U,U>>> starGates; map<U,vector<U>> starOrd; // gates in canonical coords
  for(auto& [B,ms]:starsize){ (void)ms; }
  for(auto& kv:demand){ U B=kv.first; vector<int> ord;
    for(int x=0;x<h;x++) if(!(B>>x&1)&&!(B>>(x^1)&1)) ord.push_back(x);
    for(int x=0;x<h;x++) if(!(B>>x&1)&&(B>>(x^1)&1)) ord.push_back(x);
    assert((int)ord.size()==h-4);
    vector<U> tg; for(U m:kv.second){ U z=0; for(int j=0;j<(int)ord.size();j++) if(m>>ord[j]&1) z|=1U<<j; tg.push_back(z);}
    sort(tg.begin(),tg.end()); tg.erase(unique(tg.begin(),tg.end()),tg.end());
    auto it=cache.find(tg);
    if(it==cache.end()){
      // greedy disjoint CSE
      vector<set<U>> terms; set<U> nodes; for(U m:tg){ set<U> s; for(int j=0;j<h-4;j++) if(m>>j&1){ s.insert(1U<<j); nodes.insert(1U<<j);} terms.push_back(s);}
      vector<pair<U,U>> gates;
      while(true){ bool any=false; for(auto&t:terms) if(t.size()>1) any=true; if(!any) break;
        map<pair<U,U>,int> fr; for(auto&t:terms){ vector<U> e(t.begin(),t.end()); for(size_t i=0;i<e.size();i++)for(size_t j=i+1;j<e.size();j++) fr[{e[i],e[j]}]++; }
        pair<U,U> best; bool have=false; int bf=0;
        for(auto& [p,c]:fr){ U u=p.first|p.second; if(!have){best=p;bf=c;have=true;continue;}
          U bu=best.first|best.second;
          auto key=make_tuple(-c,__builtin_popcount(u),u,p.first,p.second); auto bk=make_tuple(-bf,__builtin_popcount(bu),bu,best.first,best.second);
          if(key<bk){best=p;bf=c;} }
        U a=best.first,b=best.second; assert(!(a&b)); U nd=a|b;
        if(!nodes.count(nd)){ nodes.insert(nd); gates.push_back({a,b}); }
        for(auto&t:terms) if(t.count(a)&&t.count(b)){ t.erase(a); t.erase(b); t.insert(nd);}
        if(absorb) for(auto&t:terms){ vector<U> c; U s=0; for(U x:t) if((x&~nd)==0){c.push_back(x); s|=x;} if(c.size()>1 && s==nd){ for(U x:c) t.erase(x); t.insert(nd);} }
      }
      // independent validity check of the template
      set<U> have; for(int j=0;j<h-4;j++) have.insert(1U<<j);
      for(auto&g:gates){ assert(!(g.first&g.second)); assert(have.count(g.first)&&have.count(g.second)); assert(have.insert(g.first|g.second).second); }
      for(U m:tg) assert(have.count(m));
      it=cache.emplace(tg,gates).first; }
    oldst+=starsize[B]; newst+=it->second.size();
    starGates[B]=it->second; starOrd[B]=vector<U>(ord.begin(),ord.end()); }
  // stars that are active but have no demanded node would be fully removable
  long long undemanded=0; for(auto&[B,c]:starsize) if(!demand.count(B)) undemanded+=c;
  long long opt=actadds-oldst-undemanded+newst;
  printf("{\"stars_with_demand\":%zu,\"stars_total\":%zu,\"templates\":%zu,\"old_star_additions\":%lld,\"undemanded_star_additions\":%lld,\"new_star_additions\":%lld,\"optimized_additions\":%lld,\"output_uses\":%zu,\"roles\":%lld}\n",
    demand.size(),starsize.size(),cache.size(),oldst,undemanded,newst,opt,roots.size(),opt+(long long)roots.size());
  bool full=h<=16;
  // Rebuild the final DAG and check every coefficient exactly (small h).
  int FW=full?(v+63)/64:0; vector<vector<V>> fs; fs.push_back(vector<V>(FW,0));
  for(int i=1;i<=v;i++){ vector<V> s(FW,0); if(full) s[(i-1)/64]|=1ULL<<((i-1)%64); fs.push_back(s);}
  long long finaladds=0; vector<U> remap(N,0); for(int i=1;i<=v;i++) remap[i]=i;
  auto addnode=[&](U a,U b){ vector<V> s(FW); for(int w=0;w<FW;w++){ assert(!(fs[a][w]&fs[b][w])); s[w]=fs[a][w]|fs[b][w]; } fs.push_back(s); finaladds++; return (U)(fs.size()-1); };
  map<pair<U,U>,U> starnode; // (B, global residual mask) -> final id
  for(auto&[B,gates]:starGates){ auto&ord=starOrd[B]; map<U,U> loc; for(int j=0;j<h-4;j++) loc[1U<<j]=fid.at(B|(1U<<ord[j]));
    for(auto&g:gates){ U id=addnode(loc[g.first],loc[g.second]); loc[g.first|g.second]=id; }
    for(auto&[m,id]:loc){ U gm=0; for(int j=0;j<h-4;j++) if(m>>j&1) gm|=1U<<ord[j]; starnode[{B,gm}]=id; } }
  for(size_t x=v+1;x<N;x++) if(act[x]){
    if(__builtin_popcount(core[x])==4){ if(isdem[x]) remap[x]=starnode.at({core[x],starm[x]}); continue; }
    U a=args[x][0],b=args[x][1]; assert(remap[a]&&remap[b]); remap[x]=addnode(remap[a],remap[b]); }
  assert(finaladds==opt); if(!full){ for(U r:roots) assert(remap[r]); printf("{\"h28_rebuild_wiring_ok\":true,\"final_additions\":%lld}\n",finaladds); return 0; }
  // check roots and the combined identity mod 3
  vector<vector<int>> coef(v+1, vector<int>(v+1,0));
  for(size_t r=0;r<roots.size();r++){ U id=remap[roots[r]]; assert(id); U C=rootinfo[r][0],E=rootinfo[r][1]; bool tot=rootinfo[r][2];
    for(int i=1;i<=v;i++){ U T=fmask[i]; bool in=(fs[id][(i-1)/64]>>((i-1)%64))&1; bool exp= tot ? ((T&C)==C) : ((T&C)==C && (T&E)==0); assert(in==exp); }
    if(tot){ for(int s=1;s<=v;s++) if((fmask[s]&C)==C) for(int i=1;i<=v;i++) if((fs[id][(i-1)/64]>>((i-1)%64))&1) coef[s][i]+=1; }
    else { int s=fid.at(C|E); for(int i=1;i<=v;i++) if((fs[id][(i-1)/64]>>((i-1)%64))&1) coef[s][i]-=1; } }
  for(int s=1;s<=v;s++) for(int i=1;i<=v;i++){ int c=((coef[s][i]%3)+3)%3; assert(c==(s==i)); }
  printf("{\"h\":%d,\"final_dag_rebuilt\":true,\"every_root_support_exact\":true,\"combined_map_identity_mod3\":true,\"final_additions\":%lld}\n",h,finaladds);
}
