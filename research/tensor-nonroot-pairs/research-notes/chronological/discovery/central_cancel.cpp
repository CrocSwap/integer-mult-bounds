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

 struct Read{int k,h;Mask response;};map<int,vector<Read>>groups;vector<Mask>response(v);for(int t=0;t<v;t++)response[t][t]=1;
 for(int k=nb-1;k>=0;k--){auto g=B[k];for(int x:g.s)if(x>=2*v)groups[x].push_back({k,x,response[g.d-v]});for(int x:g.s)if(v<=x&&x<2*v)response[x-v]^=response[g.d-v];}
 auto profile=[&](const set<pair<int,int>>&drop){array<int,9>H{};vector<int>cf=start;auto visit=[&](int r,int f){if(!sub[cf[r]][f])throw runtime_error("nonmonotone");if(cf[r]!=f)H[dim[f]-dim[cf[r]]]++;cf[r]=f;};
 for(string phase:{"D","A","B","C"}){int k=0;for(auto e:z[phase]){int f=e[0],d=e[1];vector<int>ss=e[2];if(phase=="B"){vector<int>keep;for(int x:ss)if(!drop.count({k,x}))keep.push_back(x);ss=keep;}if(!ss.empty()){visit(d,f);for(int x:ss)visit(x,f);}k++;}if(phase=="A")for(int r:z["ret"])H[dim[cf[r]]]++;}
 for(int r=0;r<n;r++)visit(r,fin[r]);return H;};
 auto oldall=profile({});long long subsets=0;int skipped=0;
 for(auto&[h,reads]:groups){int k=reads.size();if(k>22){skipped++;continue;}vector<Mask>value(1<<k);for(unsigned mask=1;mask<(1u<<k);mask++){int b=__builtin_ctz(mask);value[mask]=value[mask&(mask-1)]^reads[b].response;if(value[mask].any())continue;subsets++;set<pair<int,int>>drop;for(int j=0;j<k;j++)if((mask>>j)&1)drop.insert({reads[j].k,h});auto H=profile(drop);array<int,9>delta{};for(int r=0;r<=8;r++)delta[r]=H[r]-oldall[r];long double cost=price(delta);if(cost<-1e-14L){J ds=J::object(),rm=J::array();for(int r=1;r<=8;r++)if(delta[r])ds[to_string(r)]=delta[r];for(auto[k,x]:drop)rm.push_back({k,x});J nom={{"helper",h},{"remove",rm},{"delta",ds},{"moment_delta",double(cost)}};noms.push_back(nom);if(cost<best){best=cost;bestj=nom;cout<<"BEST "<<nom.dump()<<endl;}}}
 }
 ofstream(av[2])<<J({{"groups",groups.size()},{"large_groups_skipped",skipped},{"zero_response_subsets",subsets},{"best",bestj},{"nominees",noms},{"dim",dim}}).dump(2);cout<<"DONE "<<groups.size()<<" "<<subsets<<" "<<noms.size()<<" skipped "<<skipped<<endl;
 }catch(exception&e){cerr<<e.what()<<endl;return 1;}}
