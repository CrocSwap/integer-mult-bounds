// DEG2 impl A: triple (a,b,c): h_ab=A, h_ac=C non-root types; third pair relaxed to Off(h_bc) >= A^C (alpha,beta!=0), or A if collinear (nongeneric A==C).
// union U = A\(La|Lb) | C\(La|Lc) | (A^C)\(Lb|Lc) ; count/min |U| <= cap. usage: triA cap repLo repHi [mode]  (mode 1: drop X_bc = control "pairs only")
#include "e8.h"
typedef struct{u X;int b;}ent;typedef struct{ent*e;int n,cap;}lst;

static int sl_[64],ns_;
static int cmpu64(const void*a,const void*b){unsigned long long x=*(unsigned long long*)a,y=*(unsigned long long*)b;return x<y?-1:x>y;}
// all distinct non-dominated masks (over S) of affine flats of affine dim k (2^k pts) through point p
static int flatsk(int p,int k,unsigned long long*out){int idx[64],m=0;for(int i=0;i<ns_;i++)if(i!=p)idx[m++]=i;int nr=0;unsigned long long*tmp=out;
 int kk=k<m?k:m;int c[4];for(int i=0;i<kk;i++)c[i]=i;
 while(1){int bs[8]={0};for(int i=0;i<kk;i++){int x=sl_[idx[c[i]]]^sl_[p];for(int t=7;t>=0&&x;t--)if(x>>t&1){if(bs[t])x^=bs[t];else{bs[t]=x;x=0;}}}
  unsigned long long mm=0;for(int j=0;j<ns_;j++){int x=sl_[j]^sl_[p];for(int t=7;t>=0&&x;t--)if((x>>t&1)&&bs[t])x^=bs[t];if(!x)mm|=1ULL<<j;}
  tmp[nr++]=mm;if(kk==0)break;int i=kk-1;while(i>=0&&c[i]==m-kk+i)i--;if(i<0)break;c[i]++;for(int j=i+1;j<kk;j++)c[j]=c[j-1]+1;}
 qsort(tmp,nr,8,cmpu64);int no=0;for(int q=0;q<nr;q++)if(q==0||tmp[q]!=tmp[q-1])tmp[no++]=tmp[q];
 {int w=0;for(int q=0;q<no;q++){int dom=0;for(int z=0;z<no&&!dom;z++)if(z!=q&&(tmp[q]&~tmp[z])==0)dom=1;if(!dom)tmp[w++]=tmp[q];}no=w;}
 return no;}
static unsigned long long *Mk[2][64];static int Mn[2][64];
static unsigned long long spanmask(int*pts,int np){ // affine span of pts (np points) intersected with S
 int bs[8]={0};for(int i=1;i<np;i++){int x=sl_[pts[i]]^sl_[pts[0]];for(int t=7;t>=0&&x;t--)if(x>>t&1){if(bs[t])x^=bs[t];else{bs[t]=x;x=0;}}}
 unsigned long long mm=0;for(int j=0;j<ns_;j++){int x=sl_[j]^sl_[pts[0]];for(int t=7;t>=0&&x;t--)if((x>>t&1)&&bs[t])x^=bs[t];if(!x)mm|=1ULL<<j;}return mm;}
static unsigned long long*tmpb;
static void buildmasks(){ // per point p and flat dim kind (0: 8-pt via 3 gens; 1: 4-pt via 2 gens): distinct non-dominated masks containing p
 if(!tmpb)tmpb=malloc(8*30000);
 for(int kd=0;kd<2;kd++)for(int p=0;p<ns_;p++){int g=kd==0?3:2;int m=0,idx[64];for(int i=0;i<ns_;i++)if(i!=p)idx[m++]=i;int nr=0;
  int c[3];int kk=g<m?g:m;for(int i=0;i<kk;i++)c[i]=i;
  while(1){int pts[4];pts[0]=p;for(int i=0;i<kk;i++)pts[i+1]=idx[c[i]];tmpb[nr++]=spanmask(pts,kk+1);if(kk==0)break;int i=kk-1;while(i>=0&&c[i]==m-kk+i)i--;if(i<0)break;c[i]++;for(int j=i+1;j<kk;j++)c[j]=c[j-1]+1;}
  qsort(tmpb,nr,8,cmpu64);int no=0;for(int q=0;q<nr;q++)if(q==0||tmpb[q]!=tmpb[q-1])tmpb[no++]=tmpb[q];
  int w=0;for(int q=0;q<no;q++){int dom=0;for(int z=0;z<no&&!dom;z++)if(z!=q&&(tmpb[q]&~tmpb[z])==0)dom=1;if(!dom)tmpb[w++]=tmpb[q];}
  free(Mk[kd][p]);Mk[kd][p]=malloc(8*(w+1));memcpy(Mk[kd][p],tmpb,8*w);Mn[kd][p]=w;}}
static int coverrec(unsigned long long rem,int used,int lvl){ if(!rem)return 1; if(lvl>=4)return 0;
 static const int dk[4]={1,1,1,0}; int capr=0;for(int L=0;L<4;L++)if(!(used>>L&1))capr+=dk[L]?8:4; if(__builtin_popcountll(rem)>capr)return 0;
 int p=__builtin_ctzll(rem);
 for(int L=0;L<4;L++){if(used>>L&1)continue;if(L>0&&L<3&&!(used>>(L-1)&1))continue;
  for(int q=0;q<Mn[dk[L]?0:1][p];q++){ if(coverrec(rem&~Mk[dk[L]?0:1][p][q],used|1<<L,lvl+1))return 1;}}
 return 0;}
int coverable(u U){ns_=0;for(int t=0;t<120;t++)if((U>>t)&1)sl_[ns_++]=lab[t]&255;buildmasks();return coverrec(ns_==64?~0ULL:((1ULL<<ns_)-1),0,0);}

int main(int argc,char**argv){build();int cap=atoi(argv[1]),rlo=atoi(argv[2]),rhi=atoi(argv[3]),mode=argc>4?atoi(argv[4]):0;
 int Ss[5]={0x01,0x02,0x40,0x81,0xc0},gen[5]={0,0,0,1,1};u*D=0;int nd=0,*dt=0;
 for(int k=0;k<5;k++){u*o;int n=orbit(offS(Ss[k]),&o);D=realloc(D,(nd+n)*sizeof(u));dt=realloc(dt,(nd+n)*sizeof(int));for(int i=0;i<n;i++){D[nd+i]=o[i];dt[nd+i]=k;}nd+=n;free(o);}
 int*seen=calloc(NM,sizeof(int)),*q=malloc(NM*sizeof(int));int nrep=0,reps[64],osz[64];
 for(int s=0;s<NM;s++)if(!seen[s]){int n=1;q[0]=s;seen[s]=1;for(int i=0;i<n;i++)for(int r=0;r<8;r++){int j=mfind(act(r,M[q[i]]));if(!seen[j]){seen[j]=1;q[n++]=j;}}reps[nrep]=s;osz[nrep++]=n;}
 long tot=0;
 for(int ri=rlo;ri<=rhi&&ri<nrep;ri++){u La=M[reps[ri]];lst*L=calloc(nd,sizeof(lst));long ne=0;
  for(int h=0;h<nd;h++){u R=D[h]&~La;if(pc(R)>cap+40)continue;
   for(int b=0;b<NM;b++){u X=R&~M[b];if(pc(X)>cap)continue;
    if(L[h].n==L[h].cap){L[h].cap=L[h].cap?2*L[h].cap:8;L[h].e=realloc(L[h].e,L[h].cap*sizeof(ent));}L[h].e[L[h].n].X=X;L[h].e[L[h].n++].b=b;ne++;}}
  int best=999;long sol=0,solc=0;long ex=0;long ncol=0,capc=1<<20;u*col=malloc(capc*sizeof(u));
  for(int h=0;h<nd;h++)if(L[h].n)for(int g=h;g<nd;g++)if(L[g].n){
   int same=(D[h]==D[g]);if(same&&!gen[dt[h]]&&0){}
   u T=D[h]^D[g];if(same&&!gen[dt[h]])T=D[h];
   for(int i=0;i<L[h].n;i++)for(int j=0;j<L[g].n;j++){u U=L[h].e[i].X|L[g].e[j].X;if(pc(U)>cap)continue;
     if(!mode)U|=T&~(M[L[h].e[i].b]|M[L[g].e[j].b]);
     int k=pc(U);if(k<best){best=k;}if(k<=cap){if(same)solc++;else sol++;if(!same||mode==9){if(ncol==capc){capc*=2;col=realloc(col,capc*sizeof(u));}col[ncol++]=U;}if(ex<3&&getenv("EX")){ex++;printf("EX rep %d h=%d g=%d b=%d c=%d U:",ri,h,g,L[h].e[i].b,L[g].e[j].b);for(int t=0;t<120;t++)if((U>>t)&1)printf(" %d",t);printf("\n");}}}}
  qsort(col,ncol,sizeof(u),cmpu);long nu=0,ncv=0,mn=999;for(long i=0;i<ncol;i++)if(i==0||col[i]!=col[i-1]){nu++;int cv=coverable(col[i]);ncv+=cv;if(cv&&pc(col[i])<mn)mn=pc(col[i]);if(cv&&getenv("EX2"))printf("COVERABLE U rep %d:",ri),({for(int t=0;t<120;t++)if((col[i]>>t)&1)printf(" %d",t);printf("\n");});}
  printf("rep %d distinctU %ld coverable(3F4+F3) %ld minsize-coverable %ld\n",ri,nu,ncv,mn);free(col);
  printf("rep %d (orbit %d): entries %ld ; min |U| %d ; configs<=%d: distinct %ld same-Off %ld\n",ri,osz[ri],ne,best,cap,sol,solc);fflush(stdout);tot+=sol+solc;
  for(int h=0;h<nd;h++)free(L[h].e);free(L);}
 printf("TOTAL %ld\n",tot);}
