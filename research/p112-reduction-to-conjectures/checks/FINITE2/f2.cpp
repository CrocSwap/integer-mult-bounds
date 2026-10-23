// FINITE2: independent re-impl. usage: ./f2 d1 d2 p R [repfrom repto]
// For each orbit rep V1 (d1-dim label subspace, orbits of distinct Lambda-sets under SIX/gens.txt line perms), for each
// distinct Lambda(V2) (V2 d2-dim, ALL), qualifying dirs h: exists <=p lines whose removal from Off(h)\(L1 u L2) leaves F2-rank<=R.
// Method: per (V1,h) DFS finds minimal witness sets Lambda(S); then scan all V2 by mask containment.
#include <set>
#include <map>
#include <array>
#include <tuple>
#include <vector>
#include <string>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cmath>
using namespace std; typedef unsigned long long u64; typedef long long ll;
struct M{u64 a,b; bool operator==(const M&o)const{return a==o.a&&b==o.b;} bool operator<(const M&o)const{return a<o.a||(a==o.a&&b<o.b);}};
static inline void setb(M&m,int i){ if(i<64)m.a|=1ULL<<i; else m.b|=1ULL<<(i-64);}
static inline bool getb(const M&m,int i){ return i<64?(m.a>>i)&1:(m.b>>(i-64))&1;}
static inline bool sub(const M&x,const M&y){return !(x.a&~y.a)&&!(x.b&~y.b);} // x subset y
int LAB[112],lineOf[512]; int Pc[112][8]; int G[12][112];
vector<M> enumL(int d){ // distinct Lambda masks of all d-dim subspaces of F2^9 via RREF
  set<M> out; 
  for(int pm=0;pm<512;pm++){ if(__builtin_popcount(pm)!=d)continue;
    vector<int> piv; for(int c=8;c>=0;c--) if(pm>>c&1) piv.push_back(c);
    vector<vector<int>> fr(d); int tot=0;
    for(int i=0;i<d;i++){ for(int c=piv[i]-1;c>=0;c--) if(!(pm>>c&1)) fr[i].push_back(c); tot+=fr[i].size(); }
    for(ll code=0;code<(1LL<<tot);code++){ int rows[9]; ll cc=code;
      for(int i=0;i<d;i++){ int r=1<<piv[i]; for(int c:fr[i]){ if(cc&1) r|=1<<c; cc>>=1;} rows[i]=r; }
      M m={0,0}; for(int s=0;s<(1<<d);s++){ int v=0; for(int i=0;i<d;i++) if(s>>i&1) v^=rows[i]; if(lineOf[v]>=0) setb(m,lineOf[v]); }
      out.insert(m); } }
  return vector<M>(out.begin(),out.end()); }
M permM(const M&m,const int*g){ M r={0,0}; for(int i=0;i<112;i++) if(getb(m,i)) setb(r,g[i]); return r; }
struct Dir{ int nv; ll v[2][8]; vector<int> off; };
vector<Dir> dirs;
int d1,d2,p,R; int gcap[10]={0,1,2,4,8,12,20,36,56,112};
// DFS
vector<int> restL; set<tuple<u64,u64,u64,u64>> memo; vector<M> wit;
M lamOf(const vector<int>&basis){ M m={0,0}; int n=basis.size(); for(int s=0;s<(1<<n);s++){int v=0; for(int i=0;i<n;i++) if(s>>i&1) v^=basis[i]; if(lineOf[v]>=0) setb(m,lineOf[v]);} return m;}
void dfs(vector<int>&basis,M rem,int budget){
  M lam=lamOf(basis); auto key=make_tuple(lam.a,lam.b,rem.a,rem.b); if(!memo.insert(key).second) return;
  int bs[10],nb=0; vector<int> ind; // greedy indep among rest lines
  for(int t:restL){ if(getb(lam,t)||getb(rem,t))continue; int x=LAB[t]; for(int i=0;i<nb;i++) x=min(x,x^bs[i]); if(x){bs[nb++]=x; ind.push_back(t); if(nb==R+1)break;} }
  if(nb<=R){ wit.push_back(lam); return; }
  for(int t:ind){
    if((int)basis.size()<d2){ vector<int> b2=basis; b2.push_back(LAB[t]); dfs(b2,rem,budget);} 
    if(budget>0){ M r2=rem; setb(r2,t); dfs(basis,r2,budget-1);} }
}
int realrank(vector<array<ll,8>>&rows){ vector<array<double,8>> a; for(auto&r:rows){array<double,8> x; for(int i=0;i<8;i++)x[i]=r[i]; a.push_back(x);} int rk=0;
  for(int c=0;c<8&&rk<(int)a.size();c++){ int pv=-1;double best=1e-9; for(int i=rk;i<(int)a.size();i++) if(fabs(a[i][c])>best){best=fabs(a[i][c]);pv=i;} if(pv<0)continue; swap(a[rk],a[pv]);
    for(int i=0;i<(int)a.size();i++) if(i!=rk){double f=a[i][c]/a[rk][c]; for(int k=0;k<8;k++)a[i][k]-=f*a[rk][k];} rk++;} return rk;}
int main(int argc,char**argv){ d1=atoi(argv[1]);d2=atoi(argv[2]);p=atoi(argv[3]);R=atoi(argv[4]); int rf=argc>5?atoi(argv[5]):0, rt=argc>6?atoi(argv[6]):1<<30;
  string W="../"; ifstream f(W+"FINITE/data80.txt"); for(int i=0;i<112;i++)f>>LAB[i]; int z; for(int i=0;i<8;i++)f>>z;
  for(int i=0;i<112;i++)for(int k=0;k<8;k++)f>>Pc[i][k]; ifstream g(W+"SIX/gens.txt"); for(int i=0;i<12;i++)for(int j=0;j<112;j++)g>>G[i][j];
  memset(lineOf,-1,sizeof lineOf); for(int i=0;i<112;i++) lineOf[LAB[i]]=i;
  // label linearity of generators
  for(int gi=0;gi<12;gi++){ // check: label sets map; linear map on span: sum relations preserved
    map<int,int> mp; vector<int> bs,im; bool ok=true; for(int t=0;t<112;t++){ int x=LAB[t],y=LAB[G[gi][t]]; int xx=x,yy=y; for(size_t i=0;i<bs.size();i++){ if((xx^bs[i])<xx){xx^=bs[i];yy^=im[i];} } if(xx){bs.push_back(xx);im.push_back(yy); // keep reduced order: re-sort not needed since test uses min
        } else if(yy) ok=false; }
    if(!ok){fprintf(stderr,"gen %d NONLINEAR?\n",gi);} }
  // all 120 root lines (doubled coords), via E8 vectors norm 2
  vector<array<int,8>> V; // E8 vectors by norm<=6, doubled coords
  { int ev[5]={-4,-2,0,2,4}, od[4]={-3,-1,1,3}; array<int,8> v;
    for(int par=0;par<2;par++){ int n=par?4:5; ll tot=1; for(int i=0;i<8;i++)tot*=n;
      for(ll c=0;c<tot;c++){ ll cc=c; int s=0,sq=0; for(int i=0;i<8;i++){ int x=par?od[cc%n]:ev[cc%n]; cc/=n; v[i]=x; s+=x; sq+=x*x; }
        if(sq==0||sq>24||((s/2)%2!=0&&(s%4!=0)))continue; if(s%4!=0)continue; V.push_back(v);} } }
  auto dotd=[&](const int*a,const int*b){int s=0;for(int i=0;i<8;i++)s+=a[i]*b[i];return s;};
  map<array<int,8>,int> seen; 
  for(auto&v:V){ int gg=0; for(int x:v)gg=std::gcd(gg,abs(x)); array<int,8> w; for(int i=0;i<8;i++)w[i]=v[i]/gg; array<int,8> n; for(int i=0;i<8;i++)n[i]=-w[i]; if(n>w)w=n; if(seen.count(w))continue; seen[w]=1;
    Dir D; D.nv=1; for(int i=0;i<8;i++)D.v[0][i]=w[i]; for(int t=0;t<112;t++) if(dotd(w.data(),Pc[t])!=0) D.off.push_back(t); if(D.off.size()<=80) dirs.push_back(D); }
  int nfin=dirs.size();
  // 120 lines
  vector<array<int,8>> L; for(auto&v:V){ int sq=0;for(int x:v)sq+=x*x; if(sq!=8)continue; array<int,8> n; for(int i=0;i<8;i++)n[i]=-v[i]; if(n>v) continue; L.push_back(v);} 
  set<vector<int>> pk; 
  for(size_t i=0;i<L.size();i++)for(size_t j=i+1;j<L.size();j++){ int ip=dotd(L[i].data(),L[j].data()); if(abs(ip)!=4)continue; vector<int> key; for(size_t k=0;k<L.size();k++) if(dotd(L[k].data(),L[i].data())==0&&dotd(L[k].data(),L[j].data())==0) key.push_back(k);
    if(!pk.insert(key).second)continue; Dir D; D.nv=2; for(int k=0;k<8;k++){D.v[0][k]=L[i][k];D.v[1][k]=L[j][k];} for(int t=0;t<112;t++) if(dotd(L[i].data(),Pc[t])!=0||dotd(L[j].data(),Pc[t])!=0) D.off.push_back(t); if(D.off.size()<=80)dirs.push_back(D);} 
  fprintf(stderr,"lines %zu finite dirs %d total incl pencils %zu (expect 120 lines, 4560, 5680)\n",L.size(),nfin,dirs.size());
  // orbits of V1
  vector<M> A=enumL(d1); set<M> Aset(A.begin(),A.end()); set<M> seenO; vector<M> reps;
  for(auto&m:A){ if(seenO.count(m))continue; reps.push_back(m); vector<M> st={m}; seenO.insert(m); while(!st.empty()){M x=st.back();st.pop_back(); for(int gi=0;gi<12;gi++){M y=permM(x,G[gi]); if(!Aset.count(y)){fprintf(stderr,"orbit leaves set\n");} if(seenO.insert(y).second)st.push_back(y);} } }
  fprintf(stderr,"d1=%d distinct Lambda %zu orbit reps %zu\n",d1,A.size(),reps.size());
  vector<M> B=enumL(d2); fprintf(stderr,"d2=%d distinct Lambda %zu\n",d2,B.size());
  int gmaxrank=0,gmaxd=0; vector<int> mark(dirs.size(),-1); int stamp=0;
  for(size_t ri=rf;ri<reps.size()&&(int)ri<rt;ri++){ M L1=reps[ri]; vector<pair<M,int>> W; // witness (mask,h)
    int cap=gcap[R]+gcap[d2]+p;
    for(size_t h=0;h<dirs.size();h++){ restL.clear(); for(int t:dirs[h].off) if(!getb(L1,t)) restL.push_back(t); if((int)restL.size()>cap)continue;
      memo.clear(); wit.clear(); vector<int> basis; dfs(basis,M{0,0},p); sort(wit.begin(),wit.end()); wit.erase(unique(wit.begin(),wit.end()),wit.end());
      for(size_t i=0;i<wit.size();i++){ bool minimal=true; for(size_t j=0;j<wit.size();j++) if(j!=i&&sub(wit[j],wit[i])&&!(wit[j]==wit[i])){minimal=false;break;} if(minimal)W.push_back({wit[i],(int)h}); } }
    int mr=0,md=0;
    for(auto&V2:B){ stamp++; vector<int> q; for(auto&w:W){ if(mark[w.second]==stamp)continue; if(sub(w.first,V2)){mark[w.second]=stamp;q.push_back(w.second);} }
      if(q.empty())continue; vector<array<ll,8>> rows; for(int h:q) for(int k=0;k<dirs[h].nv;k++){array<ll,8> r; for(int i=0;i<8;i++)r[i]=dirs[h].v[k][i]; rows.push_back(r);} int rk=realrank(rows); mr=max(mr,rk); md=max(md,(int)q.size()); }
    printf("rep %zu lines %d witnesses %zu maxrank %d maxdirs %d\n",ri,__builtin_popcountll(L1.a)+__builtin_popcountll(L1.b),W.size(),mr,md); fflush(stdout);
    gmaxrank=max(gmaxrank,mr); gmaxd=max(gmaxd,md); }
  printf("OVERALL d1=%d d2=%d p=%d R=%d reps %d..%d max real rank %d max #dirs %d\n",d1,d2,p,R,rf,rt,gmaxrank,gmaxd);
}
