// FIVEROW propagation enumerator (own code). For every closure (F subset B, dim F=f, dim B=b) of F2^9:
// Dbar = ports with label in B, Sbar = ports with label perp F. Cells of Dbar x Sbar are REMOVED (row 5 may live there);
// rows 1-4 must equal T on every other Q-cell. Rigidity propagation (FATROWS) from a rank-4 all-Q biclique avoiding the
// removed cells: W[t] forced if its allowed forced partners have Y-rank 4 (not inside one Y hyperplane flat); same for U.
// Output: histogram of outcomes (KW,KU) with counts and one example closure. Purely combinatorial => exact given the
// exactly computed flats/bicliques (prep.py).
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <map>
#include <string>
#include <cstring>
#include <functional>
typedef unsigned __int128 M;
int n; int lab[128]; M Q[128]; std::vector<M> HX,HY; std::vector<std::pair<M,M>> BIC;
M ALL;
M rd(FILE*f){ char buf[64]; if(fscanf(f,"%63s",buf)!=1) exit(2); M x=0; for(char*p=buf;*p;p++){int d=(*p<='9')?*p-'0':*p-'a'+10; x=(x<<4)|d;} return x; }
static inline bool rank4(M part,const std::vector<M>&H){ if(!part) return false; for(const M&h:H) if((part&~h)==0) return false; return true; }
static inline int pc(M x){ return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64)); }
static void propagate(M D,M S,M I,M J,M&KW,M&KU){
  KW=I; KU=J; bool ch=true;
  while(ch){ ch=false;
    for(int t=0;t<n;t++){ M bt=((M)1)<<t;
      if(!(KW&bt)){ M part=Q[t]&KU; if(D&bt) part&=~S; if(pc(part)>=4 && rank4(part,HY)){ KW|=bt; ch=true; } }
      if(!(KU&bt)){ M part=Q[t]&KW; if(S&bt) part&=~D; if(pc(part)>=4 && rank4(part,HX)){ KU|=bt; ch=true; } }
    } }
}
static void best(M D,M S,M&KW,M&KU,int&nst){
  // start blocks: maximal rank-4 bicliques I x J (I = 4-port coset). Admissible sub-blocks with all cells allowed:
  //  (a) I x J if I avoids Dbar; (b) I x (J\Sbar) if Y[J\Sbar] has rank 4 (then T[I,J\Sbar] = X[I] Y[J\Sbar]^T has rank 4);
  //  (c) transposed: (J\Dbar) x I if I avoids Sbar and X[J\Dbar], Y[I] have rank 4.
  KW=0;KU=0; nst=0; int bestv=-1; int tries=0;
  for(int pass=0;pass<3;pass++) for(auto&ij:BIC){ M I=ij.first,J=ij.second, sI,sJ;
    if(pass==0){ if(I&D) continue; sI=I; sJ=J; }
    else if(pass==1){ if(!(I&D)) continue; sJ=J&~S; if(!rank4(sJ,HY)) continue; sI=I; }
    else { if(I&S) continue; sI=J&~D; if(!rank4(sI,HX) || !rank4(I,HY)) continue; sJ=I; }
    nst++;
    if((sI&~KW)==0 && (sJ&~KU)==0) continue;
    M a,b; propagate(D,S,sI,sJ,a,b); int v=pc(a)+pc(b); if(v>bestv){bestv=v;KW=a;KU=b;}
    if(bestv==2*n || ++tries>=6) return; }
}
// E8 bound: rows 1-4 are (X a)(Y b)^T on KW x KU, so row support contains KW\hx and KU\hy for hyperplane flats hx,hy.
// beta = min over (hx,hy) of rank_F2 of the label pairing on span(KW\hx) x span(KU\hy) = dim A - dim(A cap C^perp).
struct S512{ unsigned long long w[8]; };
static S512 spanset(M ports){ int bs[9]; int nb=0; for(int t=0;t<n;t++) if((ports>>t)&1){ int v=lab[t]; for(int j=0;j<nb;j++) if((v^bs[j])<v) v^=bs[j]; if(v){ bs[nb++]=v; for(int j=nb-1;j>0 && bs[j]>bs[j-1];j--) std::swap(bs[j],bs[j-1]);} }
  S512 r; memset(&r,0,sizeof r); for(int x=0;x<(1<<nb);x++){ int v=0; for(int j=0;j<nb;j++) if(x>>j&1) v^=bs[j]; r.w[v>>6]|=1ULL<<(v&63);} return r; }
static S512 perp(const S512&C){ int bs[9]; int nb=0; for(int c=1;c<512;c++) if((C.w[c>>6]>>(c&63))&1){ int v=c; for(int j=0;j<nb;j++) if((v^bs[j])<v) v^=bs[j]; if(v){ bs[nb++]=v; for(int j=nb-1;j>0 && bs[j]>bs[j-1];j--) std::swap(bs[j],bs[j-1]);} if(nb==9) break; }
  S512 r; memset(&r,0,sizeof r); for(int v=0;v<512;v++){ bool ok=true; for(int j=0;j<nb&&ok;j++) if(__builtin_parity(v&bs[j])) ok=false; if(ok) r.w[v>>6]|=1ULL<<(v&63);} return r; }
static int lg(const S512&a){ int c=0; for(int i=0;i<8;i++) c+=__builtin_popcountll(a.w[i]); int d=0; while((1<<d)<c) d++; return d; }
static int dimspan(M ports){ int bs[9]; int nb=0; for(int t=0;t<n && nb<9;t++) if((ports>>t)&1){ int v=lab[t]; for(int j=0;j<nb;j++) if((v^bs[j])<v) v^=bs[j]; if(v){ bs[nb++]=v; for(int j=nb-1;j>0 && bs[j]>bs[j-1];j--) std::swap(bs[j],bs[j-1]);} } return nb; }
static int beta(M KW,M KU){ // exact min; fast path via dim A + dim C - 9 lower bound
  int ma=9,mc=9; for(const M&h:HX){ int d=dimspan(KW&~h); if(d<ma) ma=d; } for(const M&h:HY){ int d=dimspan(KU&~h); if(d<mc) mc=d; }
  if(ma+mc-9>=7) return 100+ (ma+mc-9); // >=7 certified by the dimension bound (100+ flags 'via dims')
  std::vector<S512> A,Cp; std::vector<int> dA;
  for(const M&h:HX){ S512 a=spanset(KW&~h); A.push_back(a); dA.push_back(lg(a)); }
  for(const M&h:HY){ Cp.push_back(perp(spanset(KU&~h))); }
  int best=99; for(size_t i=0;i<A.size();i++) for(size_t j=0;j<Cp.size();j++){ int c=0; for(int k=0;k<8;k++) c+=__builtin_popcountll(A[i].w[k]&Cp[j].w[k]); int d=0; while((1<<d)<c) d++; int r=dA[i]-d; if(r<best) best=r; }
  return best; }
// enumerate k-dim subspaces of F2^m in RREF; callback gets basis (k vectors, m bits)
template<class Fn> void subspaces(int m,int k,Fn fn){
  std::vector<int> piv(k);
  std::function<void(int,int)> choose;
  std::vector<int> bas(k);
  std::function<void(int)> fill;
  // free positions for row i: columns > piv[i] that are not pivots
  fill=[&](int i){ if(i==k){ fn(bas); return; }
    std::vector<int> fr; for(int c=piv[i]+1;c<m;c++){ bool isp=false; for(int j=0;j<k;j++) if(piv[j]==c) isp=true; if(!isp) fr.push_back(c);}
    int nf=fr.size(); for(long x=0;x<(1L<<nf);x++){ int v=1<<piv[i]; for(int j=0;j<nf;j++) if(x>>j&1) v|=1<<fr[j]; bas[i]=v; fill(i+1);} };
  choose=[&](int i,int start){ if(i==k){ fill(0); return; } for(int c=start;c<m;c++){ piv[i]=c; choose(i+1,c+1);} };
  choose(0,0);
}
#include <functional>
static inline int dot(int a,int b){ return __builtin_parity(a&b); }
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); int f_=atoi(argv[2]), b_=atoi(argv[3]); const char*out=argv[4]; int bref=(argc>5)?atoi(argv[5]):-1; long nref=0, nrefail=0;
  if(fscanf(f,"%d",&n)!=1) return 2; for(int i=0;i<n;i++) if(fscanf(f,"%d",&lab[i])!=1) return 2;
  for(int i=0;i<n;i++) Q[i]=rd(f); int k; if(fscanf(f,"%d",&k)!=1) return 2; for(int i=0;i<k;i++) HX.push_back(rd(f));
  if(fscanf(f,"%d",&k)!=1) return 2; for(int i=0;i<k;i++) HY.push_back(rd(f));
  if(fscanf(f,"%d",&k)!=1) return 2; for(int i=0;i<k;i++){ M I=rd(f),J=rd(f); BIC.push_back({I,J}); }
  ALL=(n==128)?~(M)0:((((M)1)<<n)-1);
  long tot=0,nostart=0,be1[100]={0},be2[100]={0}; int nfail=0; FILE*fo=fopen(out,"w");
  subspaces(9,f_,[&](const std::vector<int>&Fb){
    // complement basis
    std::vector<int> full(Fb); std::vector<int> comp; 
    auto inspan=[&](const std::vector<int>&bs,int v){ int r=v; std::vector<int> e; // gaussian
      std::vector<int> bb; for(int x:bs){ int y=x; for(int z:bb) if((y^z)<y) y^=z; if(y) bb.push_back(y);} 
      for(int z:bb) if((r^z)<r) r^=z; return r==0; };
    for(int e=0;e<9 && (int)full.size()<9;e++){ int v=1<<e; if(!inspan(full,v)){ full.push_back(v); comp.push_back(v);} }
    M S=0; for(int t=0;t<n;t++){ bool ok=true; for(int x:Fb) if(dot(lab[t],x)) ok=false; if(ok) S|=((M)1)<<t; }
    subspaces(9-f_,b_-f_,[&](const std::vector<int>&Cb){
      std::vector<int> Bb(Fb); for(int c:Cb){ int v=0; for(int j=0;j<9-f_;j++) if(c>>j&1) v^=comp[j]; Bb.push_back(v);} 
      static unsigned char inB[512]; memset(inB,0,512); int nb=Bb.size();
      for(int x=0;x<(1<<nb);x++){ int v=0; for(int j=0;j<nb;j++) if(x>>j&1) v^=Bb[j]; inB[v]=1; }
      M D=0; for(int t=0;t<n;t++) if(inB[lab[t]]) D|=((M)1)<<t;
      M KW,KU; int nst; best(D,S,KW,KU,nst); tot++; if(nst==0) nostart++;
      int be=beta(KW,KU); bool fail=(be<7)||(be>=100 && be<107);
      if(be>=100) be2[be-100]++; else be1[be]++;
      if(fail && bref>=0){ // refine: all B' with F <= B' <= B, dim B' = bref
        std::vector<int> Bc(Bb.begin()+f_,Bb.end());
        subspaces(b_-f_,bref-f_,[&](const std::vector<int>&Cs){
          std::vector<int> B2(Fb); for(int c:Cs){ int v=0; for(int j=0;j<b_-f_;j++) if(c>>j&1) v^=Bc[j]; B2.push_back(v);} 
          static unsigned char in2[512]; memset(in2,0,512); int nb2=B2.size();
          for(int x=0;x<(1<<nb2);x++){ int v=0; for(int j=0;j<nb2;j++) if(x>>j&1) v^=B2[j]; in2[v]=1; }
          M D2=0; for(int t=0;t<n;t++) if(in2[lab[t]]) D2|=((M)1)<<t;
          M K2,U2; int ns2; best(D2,S,K2,U2,ns2); int b2=beta(K2,U2); nref++;
          bool f2=(b2<7)||(b2>=100&&b2<107);
          if(f2){ nrefail++; if(nfail<2000){ nfail++; fprintf(fo,"REFINED-FAIL beta %d KW %d KU %d nst %d | F",b2,pc(K2),pc(U2),ns2); for(int x:Fb) fprintf(fo," %d",x); fprintf(fo," B"); for(int x:B2) fprintf(fo," %d",x); fprintf(fo,"\n"); } }
        });
      } else if(fail && nfail<2000){ nfail++; fprintf(fo,"beta %d KW %d KU %d nst %d | F",be,pc(KW),pc(KU),nst); for(int x:Fb) fprintf(fo," %d",x); fprintf(fo," B"); for(int x:Bb) fprintf(fo," %d",x); fprintf(fo,"\n"); }
    });
  });
  fprintf(fo,"# f=%d b=%d closures %ld nostart %ld refine-to %d: refined %ld refined-fail %ld\n",f_,b_,tot,nostart,bref,nref,nrefail); printf("refine-to %d: refined %ld refined-fail %ld | ",bref,nref,nrefail); printf("f=%d b=%d closures %ld nostart %ld | beta exact:",f_,b_,tot,nostart);
  for(int i=0;i<100;i++) if(be1[i]) printf(" %d:%ld",i,be1[i]); printf(" | beta>=dims bound:"); for(int i=0;i<100;i++) if(be2[i]) printf(" %d:%ld",i,be2[i]); printf("\n");
  fprintf(fo,"# beta exact:"); for(int i=0;i<100;i++) if(be1[i]) fprintf(fo," %d:%ld",i,be1[i]); fprintf(fo," | via dims:"); for(int i=0;i<100;i++) if(be2[i]) fprintf(fo," %d:%ld",i,be2[i]); fprintf(fo,"\n"); fclose(fo); return 0;
}
