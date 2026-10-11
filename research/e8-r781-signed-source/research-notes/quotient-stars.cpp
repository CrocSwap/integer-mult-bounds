#include <bits/stdc++.h>
#include <json.hpp>
using namespace std;using J=nlohmann::json;
struct Q{long long a,b;Q(long long n=0,long long d=1){if(d<0)n=-n,d=-d;long long g=gcd(abs(n),d);a=n/g;b=d/g;}friend Q operator+(Q x,Q y){long long g=gcd(x.b,y.b);__int128 a=(__int128)x.a*(y.b/g)+(__int128)y.a*(x.b/g),b=(__int128)x.b*(y.b/g);if(a>LLONG_MAX||a<LLONG_MIN||b>LLONG_MAX)throw runtime_error("rational overflow");return Q((long long)a,(long long)b);}friend Q operator*(Q x,Q y){long long g=gcd(abs(x.a),y.b),h=gcd(abs(y.a),x.b);__int128 a=(__int128)(x.a/g)*(y.a/h),b=(__int128)(x.b/h)*(y.b/g);if(a>LLONG_MAX||a<LLONG_MIN||b>LLONG_MAX)throw runtime_error("rational overflow");return Q((long long)a,(long long)b);}Q&operator+=(Q y){return *this=*this+y;}friend bool operator!=(Q x,int n){return x.a!=n*x.b;}};


struct Gate{int source,frame,time,version;long double coef;};
bool sub(const vector<int>&a,const vector<int>&b){int p[9]={};for(int x:b)while(x){int k=31-__builtin_clz(x);if(p[k])x^=p[k];else{p[k]=x;break;}}for(int x:a)while(x){int k=31-__builtin_clz(x);if(!p[k])return false;x^=p[k];}return true;}
int main(int argc,char**argv){try{
 if(argc!=3)throw runtime_error("source.json output.json");J c;ifstream(argv[1])>>c;int v=c["v"],n=2*v+c["R"].get<int>();vector<vector<int>>F=c["frames"];vector<int>start=c["start"],finish=c["final"],version(n);vector<vector<Gate>>feeds(v);vector<vector<Q>>clean(n,vector<Q>(v));for(int i=0;i<v;i++)clean[i][i]=Q(1);map<string,int>classes;int time=0,nA=c["A"].size();
 for(string phase:{"A","B"})for(auto&g:c[phase]){for(auto&a:g[3]){int t=g[0]=="in"?g[2].get<int>():a[0].get<int>(),s=g[0]=="in"?a[0].get<int>():g[2].get<int>();if(v<=s&&s<2*v)throw runtime_error("base target read");Q coeff(a[1].get<long long>(),a[2].get<long long>());if(phase=="B"&&v<=t&&t<2*v){Q scale;for(auto z:clean[s])if(z.a){scale=z;break;}string key;if(scale.a)for(auto z:clean[s]){Q u=z*Q(scale.b,scale.a);key+=to_string(u.a)+"/"+to_string(u.b)+",";}else key="zero";if(!classes.count(key))classes[key]=classes.size();feeds[t-v].push_back({s,g[1],time,classes[key],(long double)coeff.a/coeff.b*scale.a/scale.b});}for(int k=0;k<v;k++)clean[t][k]+=coeff*clean[s][k];version[t]++;}time++;}
 vector<map<int,int>>old(v);for(int i=0;i<v;i++){int f=start[v+i];for(auto g:feeds[i])if(g.frame!=f){old[i][F[g.frame].size()-F[f].size()]++;f=g.frame;}if(f!=finish[v+i])old[i][F[finish[v+i]].size()-F[f].size()]++;}
 long double w[10]={};for(int r=1;r<=9;r++)w[r]=powl((long double)r/73,1-.0010013L)+1e-16L*32*73*73*powl(1.L/73,1-.0010013L);
 vector<pair<int,int>>scales={{1,1},{-1,1},{2,1},{-2,1},{1,2},{-1,2}};using Key=tuple<int,int,int>;vector<vector<long double>>gain(v,vector<long double>(v));vector<vector<J>>best(v,vector<J>(v));long long trials=0,legal=0;J candidates=J::array();
 for(int i=0;i<v;i++)for(int j=0;j<v;j++)if(i!=j)for(int len=1;len<=(int)feeds[j].size();len++){
  auto last=feeds[j][len-1];int cut=last.time,E=last.frame;if(F[E].empty()||F[E].size()>=8)continue;
  for(auto [qn,qd]:scales){trials++;long double q=(long double)qn/qd;map<Key,pair<long double,Gate>>row;
   for(auto g:feeds[i])if(g.time<=cut){Key k={g.version,0,g.frame};if(!row.count(k))row[k]={0,g};row[k].first+=g.coef;}
   for(auto g:feeds[j])if(g.time<=cut){Key k={g.version,0,g.frame};if(!row.count(k))row[k]={0,g};row[k].first-=q*g.coef;}
   vector<Gate>seq;int zeros=0;for(auto[k,p]:row){if(fabsl(p.first)<1e-15L){zeros++;continue;}auto g=p.second;g.coef=p.first;seq.push_back(g);}for(auto g:feeds[i])if(g.time>cut)seq.push_back(g);
   seq.push_back({v+j,E,cut,-1,q});stable_sort(seq.begin(),seq.end(),[&](Gate a,Gate b){if(a.time!=b.time)return a.time<b.time;if(a.source==v+j)return false;if(b.source==v+j)return true;return a.source<b.source;});
   int f=start[v+i];bool ok=true;map<int,int>dh=old[i];for(auto&[r,z]:dh)z=-z;
   for(auto g:seq){if(!sub(F[f],F[g.frame])){ok=false;break;}int d=F[g.frame].size()-F[f].size();if(d)dh[d]++;f=g.frame;}
   if(!ok||!sub(F[f],F[finish[v+i]]))continue;int d=F[finish[v+i]].size()-F[f].size();if(d)dh[d]++;legal++;long double delta=0;int mass=0;J hist=J::object();for(auto[r,z]:dh)if(r&&z){mass+=r*z;delta+=w[r]*z;hist[to_string(r)]=z;}if(mass)throw runtime_error("mass");
   if(delta<-1e-14L){J e={{"destination",v+i},{"donor_target",v+j},{"prefix_target_deliveries",len},{"cut_group",cut},{"recovery_frame",E},{"scale_numerator",qn},{"scale_denominator",qd},{"histogram_delta",hist},{"gain",double(-delta)},{"cancelled_tokens",zeros}};if(-delta>gain[i][j]){gain[i][j]=-delta;best[i][j]=e;}}
  }
 }
 for(int i=0;i<v;i++)for(int j=0;j<v;j++)if(gain[i][j]>0)candidates.push_back(best[i][j]);
 auto score=[&](const vector<int>&donors){long double sum=0;for(int i=0;i<v;i++)if(!donors[i]){long double a=0;for(int j=0;j<v;j++)if(donors[j])a=max(a,gain[i][j]);sum+=a;}return sum;};
 mt19937 rng(17011);vector<int>solution(v);long double optimum=0;
 for(int restart=0;restart<80;restart++){vector<int>d(v);for(int i=0;i<v;i++)d[i]=rng()%100<(10+restart%6*10);long double val=score(d);for(int iter=0;iter<80;iter++){int win=-1;long double top=val;for(int i=0;i<v;i++){d[i]^=1;long double z=score(d);d[i]^=1;if(z>top+1e-14L){top=z;win=i;}}if(win<0)break;d[win]^=1;val=top;}if(val>optimum){optimum=val;solution=d;}}
 J stars=J::array(),delta=J::object();map<int,int>hist;map<int,int>usage;for(int i=0;i<v;i++)if(!solution[i]){int jwin=-1;long double z=0;for(int j=0;j<v;j++)if(solution[j]&&gain[i][j]>z){z=gain[i][j];jwin=j;}if(jwin>=0){auto e=best[i][jwin];stars.push_back(e);usage[v+jwin]++;for(auto it=e["histogram_delta"].begin();it!=e["histogram_delta"].end();it++)hist[stoi(it.key())]+=it.value().get<int>();}}
 for(auto[r,z]:hist)if(z)delta[to_string(r)]=z;J use=J::object();for(auto[k,z]:usage)use[to_string(k)]=z;
 J result={{"status","NOMINATION_ONLY"},{"source_R",c["R"]},{"tested",trials},{"legal",legal},{"positive_pairs",candidates.size()},{"selections",stars},{"donor_fanouts",use},{"histogram_delta",delta},{"moment_gain",double(optimum)},{"candidates",candidates},{"scope","Normalized exact CLEAN row plus frame token quotient; raw dirty response changes and explicit fresh decoder is mandatory. Native price nomination only."}};
 ofstream(argv[2])<<result.dump(2)<<"\n";cout<<"R "<<c["R"]<<" tested "<<trials<<" legal "<<legal<<" positive "<<candidates.size()<<" stars "<<stars.size()<<" donors "<<usage.size()<<" gain "<<(double)optimum<<" delta "<<delta.dump()<<"\n";
}catch(exception&e){cerr<<e.what()<<"\n";return 1;}}
