#include <bits/stdc++.h>
#include <json.hpp>
using namespace std;
#include "rational.hpp"
using namespace std;using J=nlohmann::json;using Mask=bitset<128>;
int rankq(vector<vector<int>> a){vector<vector<Q>> b;for(auto&row:a){vector<Q> r;for(int x:row)r.push_back(Q(x));for(auto&s:b){int p=0;while(!s[p].a)p++;if(r[p].a){Q t=Q(-r[p].a,r[p].b)*Q(s[p].b,s[p].a);for(int j=p;j<(int)r.size();j++)r[j]+=t*s[j];}}bool non=false;for(auto x:r)non|=bool(x.a);if(non)b.push_back(r);}return b.size();}
struct Gate{int f,d;vector<int>s;};
int main(int ac,char**av){try{
 J z;ifstream(av[1])>>z;int v=z["v"],n=2*v+z["R"].get<int>();vector<vector<int>>fs=z["frames"],lines=z["lines"];vector<Mask>m;vector<int>dim;
 for(auto&f:fs){Mask q;vector<vector<int>>a;for(int i:f){q[i]=1;a.push_back(lines[i]);}m.push_back(q);dim.push_back(rankq(a));}
 int nf=m.size();vector<vector<bool>>sub(nf,vector<bool>(nf));for(int a=0;a<nf;a++)for(int b=0;b<nf;b++)sub[a][b]=(m[a]&~m[b]).none();
 vector<int>start=z["start"],fin=z["final"];vector<Gate>B;for(auto e:z["B"])B.push_back({e[0],e[1],e[2]});int nb=B.size();
 vector<vector<int>>path(v),cur(nb+1,vector<int>(v)),bad(v,vector<int>(nb+1));cur[0]=vector<int>(start.begin()+v,start.begin()+2*v);
 for(int i=0;i<nb;i++){cur[i+1]=cur[i];for(int t=0;t<v;t++)bad[t][i+1]=bad[t][i];auto e=B[i];auto rs=e.s;rs.push_back(e.d);bool yy=false;for(int r:e.s)if(v<=r&&r<2*v)yy=true;for(int r:rs)if(v<=r&&r<2*v){cur[i+1][r-v]=e.f;path[r-v].push_back(i);if(yy)bad[r-v][i+1]++;}}
 map<pair<int,int>,int>jc;auto join=[&](int a,int b){auto k=minmax(a,b);if(jc.count(k))return jc[k];int best=-1;for(int f=0;f<nf;f++)if(sub[a][f]&&sub[b][f]&&(best<0||dim[f]<dim[best]))best=f;return jc[k]=best;};
 vector<array<int,9>>old(v);for(int t=0;t<v;t++){int last=start[t+v];for(int i:path[t]){int f=B[i].f;if(last!=f)old[t][dim[f]-dim[last]]++;last=f;}if(last!=fin[t+v])old[t][dim[fin[t+v]]-dim[last]]++;}
 long double ww[9]={};for(int r=1;r<=8;r++)ww[r]=powl((long double)r/78,1-.001286L);
 auto price=[&](array<int,9>a){long double ans=0;for(int r=1;r<=8;r++)ans+=ww[r]*a[r];return ans;};
 J noms=J::array(),bestj;long double best=0;long long trials=0,valid=0;auto clock=chrono::steady_clock::now();

 for(int orig=0;orig<nb;orig++)for(int donor:B[orig].s)if(v<=donor&&donor<2*v){int u=B[orig].d-v,d=donor-v;if(u<0||u>=v||u==d)continue;
  for(int cut=0;cut<=nb;cut++)if(cut!=orig&&cut!=orig+1){int lo=min(cut,orig),hi=max(cut,orig+1);bool barrier=false;
   set<int>dp;map<int,int>dfirst,ufirst;
   for(int k=lo;k<hi;k++){
    if(k!=orig){bool yread=false;for(int x:B[k].s)if(v<=x&&x<2*v)yread=true;
     if(yread){auto rs=B[k].s;rs.push_back(B[k].d);for(int r:rs)if(r==v+u||r==v+d)barrier=true;}}
    if(B[k].d==v+d)for(int x:B[k].s){if(x<2*v){barrier=true;continue;}if(dp.count(x))dp.erase(x);else dp.insert(x);if(!dfirst.count(x))dfirst[x]=k;}
    if(B[k].d==v+u)for(int x:B[k].s)if(x>=2*v&&!ufirst.count(x))ufirst[x]=k;
   }
   if(barrier)continue;trials++;set<pair<int,int>>drop{{orig,donor}};map<int,vector<int>>add;
   for(int x:dp)if(ufirst.count(x))drop.insert({ufirst[x],x});else add[dfirst[x]].push_back(x);
   array<int,9>hu{},hd{};int cu=start[v+u],cd=start[v+d];bool ok=true;int nf1=-1;
   auto visit=[&](int&last,int f,array<int,9>&h){if(!sub[last][f]){ok=false;return;}if(last!=f)h[dim[f]-dim[last]]++;last=f;};
   for(int k=0;k<=nb&&ok;k++){
    if(k==cut){nf1=join(cu,cd);if(nf1<0){ok=false;break;}visit(cu,nf1,hu);visit(cd,nf1,hd);}
    if(k==nb)break;auto g=B[k];bool tu=false,td=false;
    if(g.d==v+u){for(int x:g.s)if(!drop.count({k,x}))tu=true;}else for(int x:g.s)if(x==v+u)tu=true;
    if(g.d==v+d)td=true;else for(int x:g.s)if(x==v+d&&!drop.count({k,x}))td=true;
    if(tu)visit(cu,g.f,hu);if(td)visit(cd,g.f,hd);if(add.count(k))visit(cu,g.f,hu);
   }
   if(!ok)continue;visit(cu,fin[v+u],hu);visit(cd,fin[v+d],hd);if(!ok)continue;valid++;
   array<int,9>delta{};for(int r=0;r<=8;r++)delta[r]=hu[r]+hd[r]-old[u][r]-old[d][r];long double cost=price(delta);
   int extra=0;for(auto[k,xs]:add)extra+=xs.size();if(cost <= 1e-14L && (int)drop.size()-1>extra && !dp.empty()){J rm=J::array(),ad=J::array(),ds=J::object();for(auto[k,x]:drop)rm.push_back({k,x});for(auto[k,xs]:add)for(int x:xs)ad.push_back({k,x});for(int r=1;r<=8;r++)if(delta[r])ds[to_string(r)]=delta[r];J nom={{"u",u+v},{"d",d+v},{"orig",orig},{"cut",cut},{"insert_frame",nf1},{"remove",rm},{"add_after",ad},{"target_delta",ds},{"moment_delta",double(cost)}};noms.push_back(nom);if(cost<best){best=cost;bestj=nom;cout<<"BEST "<<nom.dump()<<endl;}}
  }
  if(chrono::duration<double>(chrono::steady_clock::now()-clock).count()>stod(av[3]))goto done;
 }
 done:ofstream(av[2])<<J({{"trials",trials},{"valid",valid},{"best",bestj},{"nominees",noms},{"dim",dim},{"seconds",chrono::duration<double>(chrono::steady_clock::now()-clock).count()}}).dump(2);cout<<"DONE "<<trials<<" "<<valid<<" "<<noms.size()<<endl;
 }catch(exception&e){cerr<<e.what()<<endl;return 1;}}
