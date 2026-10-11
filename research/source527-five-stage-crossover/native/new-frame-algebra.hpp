#define BOOST_MP_STANDALONE
#include <boost/multiprecision/cpp_int.hpp>
#include "json.hpp"
#include <fstream>
#include <iostream>
#include <vector>
#include <array>
#include <map>
#include <set>
#include <algorithm>
#include <cmath>
#include <chrono>
#include <stdexcept>
using nlohmann::json;using I=boost::multiprecision::cpp_int;using Row=std::array<I,24>;using Mat=std::vector<Row>;
I absI(I x){return x<0?-x:x;} I gcdI(I a,I b){a=absI(a);b=absI(b);while(b){I t=a%b;a=b;b=t;}return a;}I mul(I a,I b){return a*b;}I subI(I a,I b){return a-b;}std::string si(I x){return x.convert_to<std::string>();}
void prim(Row&r){I g=0;for(I x:r)g=gcdI(g,x);if(g>1)for(I&x:r)x/=g;for(I x:r)if(x){if(x<0)for(I&y:r)y=-y;break;}}
Mat red(Mat in,int h=24){Mat out;std::vector<int> piv;for(Row r:in){for(int k=0;k<(int)out.size();k++)if(r[piv[k]]){I a=out[k][piv[k]],b=r[piv[k]];for(int c=0;c<h;c++)r[c]=subI(mul(r[c],a),mul(out[k][c],b));prim(r);}int c=0;while(c<h&&!r[c])c++;if(c==h)continue;prim(r);for(Row&q:out)if(q[c]){I a=r[c],b=q[c];for(int j=0;j<h;j++)q[j]=subI(mul(q[j],a),mul(r[j],b));prim(q);}out.push_back(r);piv.push_back(c);}std::sort(out.begin(),out.end(),[](const Row&a,const Row&b){int x=0,y=0;while(x<24&&!a[x])x++;while(y<24&&!b[y])y++;return x<y;});return out;}
Mat ker(Mat A,int h=24){A=red(A,h);std::set<int>p;for(Row&r:A){int c=0;while(c<h&&!r[c])c++;p.insert(c);}Mat B;for(int f=0;f<h;f++)if(!p.count(f)){I d=1;for(Row&r:A){int c=0;while(c<h&&!r[c])c++;if(r[f])d=mul(d/gcdI(d,r[c]),absI(r[c]));}Row v{};v[f]=d;for(Row&r:A){int c=0;while(c<h&&!r[c])c++;if(r[f])v[c]=-mul(r[f],d/r[c]);}prim(v);B.push_back(v);}return red(B,h);}
I dot(const Row&a,const Row&b){I x=0;for(int c=0;c<24;c++){I y=mul(a[c],b[c]);x+=y;}return x;}
Mat parseMat(const json&j){Mat M;for(auto&r:j){Row a{};for(int c=0;c<24;c++)a[c]=r[c].get<long long>();M.push_back(a);}return M;}
struct Frame{Mat A,B;};std::vector<Frame> fr;std::map<std::string,int>interned;std::map<int,int>orig;std::map<std::pair<int,int>,int>cacheMeet;std::map<std::pair<int,int>,bool>cacheSub;
std::string key(const Mat&M){std::string s;for(const Row&r:M){for(I x:r){s+=si(x);s+=',';}s+=';';}return s;}
int addB(Mat B){B=red(B);std::string k=key(B);auto it=interned.find(k);if(it!=interned.end())return it->second;int id=fr.size();fr.push_back({ker(B),B});interned[k]=id;return id;}
int addA(Mat A){return addB(ker(A));}bool sub(int a,int b){if(a==b)return true;auto k=std::make_pair(a,b);if(cacheSub.count(k))return cacheSub[k];bool ok=fr[a].B.size()<=fr[b].B.size();if(ok)for(auto&u:fr[a].B)for(auto&v:fr[b].A)if(dot(u,v)){ok=false;break;}cacheSub[k]=ok;return ok;}
int meet(int a,int b){if(sub(a,b))return a;if(sub(b,a))return b;auto k=std::minmax(a,b);if(cacheMeet.count(k))return cacheMeet[k];Mat A=fr[a].A;A.insert(A.end(),fr[b].A.begin(),fr[b].A.end());return cacheMeet[k]=addA(A);}
int joinF(int a,int b){if(sub(a,b))return b;if(sub(b,a))return a;Mat B=fr[a].B;B.insert(B.end(),fr[b].B.begin(),fr[b].B.end());return addB(B);}
bool nondeg(int f){Mat B=fr[f].B,A=fr[f].A;int n=B.size();if(!n||n==24)return true;Mat U=n<=12?B:A;int d=U.size();std::vector<I>s(d);for(int i=0;i<d;i++)for(I x:U[i])s[i]+=x;Mat M;for(int i=0;i<d;i++){Row r{};for(int j=0;j<d;j++)r[j]=n<=12?subI(mul(9,dot(U[i],U[j])),mul(s[i],s[j])):mul(-15,dot(U[i],U[j]))+mul(s[i],s[j]);M.push_back(r);}return red(M,d).size()==d;}
json load(std::string p){std::ifstream f(p);json j;f>>j;return j;}
struct End{int i,f;};struct Edge{End a,b;};std::vector<Edge>edges;std::vector<std::vector<End>>outgoing,incoming;
void edge(End a,End b){edges.push_back({a,b});if(a.i>=0)outgoing[a.i].push_back(b);if(b.i>=0)incoming[b.i].push_back(a);if(a.i>=0&&b.i>=0&&a.i>=b.i)throw std::runtime_error("edge order");}
json histogram(const std::vector<int>&X){std::map<int,long long>H;long long mass=0;for(auto&e:edges){int a=e.a.i<0?e.a.f:X[e.a.i],b=e.b.i<0?e.b.f:X[e.b.i];if(!sub(a,b))throw std::runtime_error("nesting failure");int r=fr[b].B.size()-fr[a].B.size();H[r]++;mass+=r;}json z;z["mass"]=mass;for(auto[r,n]:H)z["histogram"][std::to_string(r)]=n;double E=0;for(auto[r,n]:H)if(r)E+=n*r*log(72.0/r);z["entropy"]=E;return z;}
struct Flow{struct Arc{int to,rev;double cap;};int n;std::vector<std::vector<Arc>>g;std::vector<int>lev,ptr;Flow(int n):n(n),g(n),lev(n),ptr(n){}void add(int u,int v,double c){if(c<=1e-12||u==v)return;g[u].push_back({v,(int)g[v].size(),c});g[v].push_back({u,(int)g[u].size()-1,0});}double dfs(int u,int t,double f){if(u==t)return f;for(int&i=ptr[u];i<(int)g[u].size();i++){auto&e=g[u][i];if(e.cap>1e-10&&lev[e.to]==lev[u]+1){double z=dfs(e.to,t,std::min(f,e.cap));if(z>1e-10){e.cap-=z;g[e.to][e.rev].cap+=z;return z;}}}return 0;}void run(int s,int t){while(true){std::fill(lev.begin(),lev.end(),-1);std::vector<int>q{s};lev[s]=0;for(int k=0;k<(int)q.size();k++)for(auto&e:g[q[k]])if(e.cap>1e-10&&lev[e.to]<0){lev[e.to]=lev[q[k]]+1;q.push_back(e.to);}if(lev[t]<0)break;std::fill(ptr.begin(),ptr.end(),0);while(dfs(s,t,1e12)>1e-10){}}}std::vector<bool>source(int s){std::vector<bool>seen(n,false);seen[s]=true;std::vector<int>q{s};for(int k=0;k<(int)q.size();k++)for(auto&e:g[q[k]])if(e.cap>1e-10&&!seen[e.to]){seen[e.to]=true;q.push_back(e.to);}return seen;}};
double ent(int r){return r?r*log(72.0/r):0;}
std::vector<int> majorantCut(const std::vector<int>&F,const std::vector<int>&M,json&receipt){int N=F.size();Flow flow(N+2);std::vector<double>u(N,0);int hard=0,allowed=0;double total=0;std::vector<std::pair<int,int>>arcs;for(auto&e:edges){int i=e.a.i,j=e.b.i;int a=i<0?e.a.f:F[i],b=j<0?e.b.f:F[j];bool ai=i>=0&&F[i]!=M[i],bj=j>=0&&F[j]!=M[j];int da=fr[a].B.size(),db=fr[b].B.size();double E00=ent(db-da);if(!ai&&!bj)continue;if(ai&&!bj){u[i]+=ent(db-fr[M[i]].B.size())-E00;continue;}if(!ai&&bj){u[j]+=ent(fr[M[j]].B.size()-da)-E00;continue;}int DMA=fr[M[i]].B.size(),DMB=fr[M[j]].B.size();double E01=ent(DMB-da),E11=ent(DMB-DMA);u[j]+=E01-E00;u[i]+=E11-E01;if(!sub(M[i],F[j])){arcs.push_back({i,j});hard++;}else{double E10=ent(db-DMA);double defect=E00+E11-E01-E10;if(defect<-1e-8)throw std::runtime_error("concavity defect sign");allowed++;total+=std::max(0.0,defect);}}
double cap=1;for(double z:u)cap+=fabs(z);for(auto[i,j]:arcs)flow.add(i,j,cap);for(int i=0;i<N;i++){if(u[i]>0)flow.add(i,N+1,u[i]);if(u[i]<0)flow.add(N,i,-u[i]);}flow.run(N,N+1);auto selected=flow.source(N);auto X=F;double proxy=0;int n=0;for(int i=0;i<N;i++)if(selected[i]&&F[i]!=M[i]){X[i]=M[i];n++;proxy+=u[i];}receipt={{"selected",n},{"proxy_delta",proxy},{"forbidden10_edges",hard},{"feasible10_edges",allowed},{"total_concavity_majorant",total}};return X;}
I det(std::vector<std::vector<I>>a){int n=a.size();if(!n)return 1;I prev=1;int sign=1;for(int k=0;k<n-1;k++){int p=k;while(p<n&&!a[p][k])p++;if(p==n)return 0;if(p!=k){std::swap(a[p],a[k]);sign=-sign;}I q=a[k][k];for(int i=k+1;i<n;i++)for(int j=k+1;j<n;j++){I z=subI(mul(a[i][j],q),mul(a[i][k],a[k][j]));if(z%prev)throw std::runtime_error("Bareiss division");a[i][j]=z/prev;}for(int i=k+1;i<n;i++)a[i][k]=0;prev=q;}return sign*a[n-1][n-1];}
I primeWitness(int f){int n=fr[f].B.size();Mat U=n<=12?fr[f].B:fr[f].A;int d=U.size();std::vector<I>s(d);for(int i=0;i<d;i++)for(I x:U[i])s[i]+=x;std::vector<std::vector<I>>a(d,std::vector<I>(d));for(int i=0;i<d;i++)for(int j=0;j<d;j++)a[i][j]=n<=12?subI(mul(9,dot(U[i],U[j])),mul(s[i],s[j])):subI(mul(-15,dot(U[i],U[j])),-mul(s[i],s[j]));return absI(det(a));}

