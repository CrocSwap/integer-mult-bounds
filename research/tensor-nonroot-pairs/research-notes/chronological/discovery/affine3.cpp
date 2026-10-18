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

 map<int,vector<pair<int,int>>> shortest;shortest[273]={};queue<int>qq;qq.push(273);while(!qq.empty()){int x=qq.front();qq.pop();for(int i=0;i<3;i++)for(int j=0;j<3;j++)if(i!=j){int y=x^(((x>>(3*j))&7)<<(3*i));if(!shortest.count(y)){shortest[y]=shortest[x];shortest[y].push_back({i,j});qq.push(y);}}}
 set<array<int,3>>trip;vector<pair<int,int>>edges;for(auto g:B)for(int x:g.s)if(v<=x&&x<2*v)edges.push_back({g.d-v,x-v});for(auto[a,b]:edges)for(auto[c,d]:edges){set<int>t{a,b,c,d};if(t.size()==3){auto it=t.begin();int x=*it++,y=*it++,z=*it;trip.insert({x,y,z});}}
 long long neutral=0;int bestsave=0;
 for(auto t:trip){int limit=nb;for(int i=0;i<nb;i++){bool yy=false,touch=false,out=false;for(int x:B[i].s)if(v<=x&&x<2*v)yy=true;auto rs=B[i].s;rs.push_back(B[i].d);for(int x:rs)if(v<=x&&x<2*v){if(find(t.begin(),t.end(),x-v)!=t.end())touch=true;else out=true;}if(yy&&touch&&out){limit=i;break;}}
  array<int,3>M{1,2,4};map<int,int>N,first,last;int oldcount=0,targetcount=0;
  for(int e=0;e<limit;e++){auto g=B[e];auto it=find(t.begin(),t.end(),g.d-v);if(it==t.end())continue;int j=it-t.begin();for(int x:g.s){oldcount++;if(x>=2*v){N[x]^=1<<j;if(!first.count(x))first[x]=e;last[x]=e;}else if(v<=x&&x<2*v){int q=find(t.begin(),t.end(),x-v)-t.begin();if(q>=3)throw runtime_error("outside");M[j]^=M[q];for(auto&[h,mask]:N)if((mask>>q)&1)mask^=1<<j;targetcount++;}else throw runtime_error("source direct");}
   if(targetcount<2)continue;int key=M[0]|(M[1]<<3)|(M[2]<<6);int newcount=shortest[key].size();for(auto[x,mask]:N)newcount+=__builtin_popcount((unsigned)mask);
   for(int late=0;late<2;late++){trials++;array<array<int,9>,3>H{};array<int,3>curs{start[v+t[0]],start[v+t[1]],start[v+t[2]]};bool ok=true;map<int,array<vector<int>,3>>writes;
    for(auto[x,mask]:N)for(int j=0;j<3;j++)if((mask>>j)&1)writes[late?last[x]:first[x]][j].push_back(x);
    auto visit=[&](int j,int f){int&cl=curs[j];if(!sub[cl][f]){ok=false;return;}if(cl!=f)H[j][dim[f]-dim[cl]]++;cl=f;};
    for(auto[k,rs]:writes){for(int j=0;j<3;j++)if(!rs[j].empty())visit(j,B[k].f);if(!ok)break;}if(!ok)continue;
    for(int j=0;j<3;j++){for(int k:path[t[j]])if(k>e)visit(j,B[k].f);visit(j,fin[v+t[j]]);}if(!ok)continue;valid++;
    array<int,9>delta{};for(int r=0;r<=8;r++)for(int j=0;j<3;j++)delta[r]+=H[j][r]-old[t[j]][r];long double cost=price(delta);
    if(cost<-1e-14L||(cost<=1e-14L&&newcount<oldcount)){J ds=J::object(),w=J::array();for(int r=1;r<=8;r++)if(delta[r])ds[to_string(r)]=delta[r];for(auto[k,rs]:writes)for(int j=0;j<3;j++)if(!rs[j].empty())w.push_back({k,v+t[j],rs[j]});J nom={{"targets",J::array({t[0]+v,t[1]+v,t[2]+v})},{"matrix_rows",M},{"cnot_word",shortest[key]},{"end",e},{"writes",w},{"target_delta",ds},{"moment_delta",double(cost)},{"old_scalar_count",oldcount},{"new_scalar_count",newcount}};noms.push_back(nom);if(cost<best-1e-14L||newcount<oldcount&&oldcount-newcount>bestsave){best=min(best,cost);bestsave=max(bestsave,oldcount-newcount);bestj=nom;cout<<"BEST "<<nom.dump()<<endl;}}
   }
  }
  if(chrono::duration<double>(chrono::steady_clock::now()-clock).count()>stod(av[3]))goto done;
 }
 done:ofstream(av[2])<<J({{"triples",trip.size()},{"trials",trials},{"valid",valid},{"best",bestj},{"nominees",noms},{"dim",dim},{"seconds",chrono::duration<double>(chrono::steady_clock::now()-clock).count()}}).dump(2);cout<<"DONE "<<trip.size()<<" "<<trials<<" "<<valid<<" "<<noms.size()<<endl;
 }catch(exception&e){cerr<<e.what()<<endl;return 1;}}
