// SERVE2: independent exhaustive max served(E). served by DEFINITION (no leftover tables): target t (120 roots, 1080 norm-4) counted if t in E (roots)
// or Off(t)\E splits into two parts of label F2-rank<=7. Own E8/labels/reflections from setup2.py.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef unsigned long long u64;
int lab[120],perm[8][120]; u128 OFF[1200];
static inline int pc(u128 x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static inline int red(int*b,int n,int x){for(int i=0;i<n;i++){int y=x^b[i]; if(y<x)x=y;} return x;}
static int lbl[128],nl;
static int rec(int i,int*bx,int nx,int*by,int ny){
  for(;i<nl;i++){int x=lbl[i]; int rx=red(bx,nx,x); if(!rx)continue; int ry=red(by,ny,x); if(!ry)continue;
    if(nx<7){int nb[8];memcpy(nb,bx,nx*4);nb[nx]=rx; if(rec(i+1,nb,nx+1,by,ny))return 1;}
    if(ny<7 && (ny>0||nx>0)){int nb[8];memcpy(nb,by,ny*4);nb[ny]=ry; if(rec(i+1,bx,nx,nb,ny+1))return 1;}
    return 0;}
  return 1;}
static int covered(u128 R){nl=0; while(R){int t; u64 lo=(u64)R; if(lo)t=__builtin_ctzll(lo); else t=64+__builtin_ctzll((u64)(R>>64)); lbl[nl++]=lab[t]; R&=R-1;}
  int bx[8],by[8]; return rec(0,bx,0,by,0);}
static int served(u128 E,u128*outS){int n=0; for(int t=0;t<1200;t++){int hit=0; if(t<120&&((E>>t)&1))hit=1; else hit=covered(OFF[t]&~E); if(hit){n++; if(outS)*outS=0;}} return n;}
static void servedlist(u128 E){printf("S"); for(int t=0;t<1200;t++){int hit=(t<120&&((E>>t)&1))||covered(OFF[t]&~E); if(hit){ if(t<120)printf(" r%d",t); else printf(" d%d",t-120);}} printf("\n");}
static int cmp(const void*a,const void*b){u128 x=*(u128*)a,y=*(u128*)b;return x<y?-1:x>y;}
static int rk(int*v,int n){int b[9],m=0; for(int i=0;i<n;i++){int x=red(b,m,v[i]); if(x){b[m++]=x; /* keep min-reduced property loosely */ for(int j=0;j<m-1;j++){} }} return m;}
static int rank2(int*v,int n){int b[9]; int m=0; for(int i=0;i<n;i++){int x=v[i]; for(int j=0;j<m;j++){int y=x^b[j]; if(y<x)x=y;} if(x){b[m++]=x; /*sort desc*/ for(int j=m-1;j>0&&b[j]>b[j-1];j--){int t=b[j];b[j]=b[j-1];b[j-1]=t;}}} return m;}
u128* flats(int s,long*cnt){long cap=1<<20,n=0; u128*A=malloc(cap*16);
  // enumerate all s-dim subspaces by RREF
  for(int P=0;P<512;P++){ if(__builtin_popcount(P)!=s)continue; int piv[9],k=0; for(int b=8;b>=0;b--) if((P>>b)&1)piv[k++]=b;
    int fb[24][2],nf=0; for(int i=0;i<s;i++) for(int c=0;c<piv[i];c++) if(!((P>>c)&1)){fb[nf][0]=i;fb[nf][1]=c;nf++;}
    for(long a=0;a<(1L<<nf);a++){int row[9]; for(int i=0;i<s;i++)row[i]=1<<piv[i]; for(int j=0;j<nf;j++) if((a>>j)&1) row[fb[j][0]]|=1<<fb[j][1];
      u128 N=0; int ls[120],m=0; for(int t=0;t<120;t++){int x=lab[t]; for(int i=0;i<s;i++) if((x>>piv[i])&1)x^=row[i]; if(!x){N|=(u128)1<<t; ls[m++]=lab[t];}}
      
      if(rank2(ls,m)<s){ // dominated by a strictly larger flat? (exists x with N(span+x)!=N)
        int dom=0; for(int x=1;x<512&&!dom;x++){ // x not in span
          u128 N2=0; for(int t=0;t<120;t++){ int l=lab[t]; int in=0; // l in span(ls)+<x> : l in W or l^x in W
            int a=l,b=l^x; // membership in W via rank test
            int w1[130],w2[130]; memcpy(w1,ls,m*4); w1[m]=a; memcpy(w2,ls,m*4); w2[m]=b;
            if(rank2(w1,m+1)==rank2(ls,m)||rank2(w2,m+1)==rank2(ls,m)) N2|=(u128)1<<t; }
          if(N2!=N) dom=1; }
        if(dom)continue; }
      if(n==cap){cap*=2;A=realloc(A,cap*16);} A[n++]=N;}}
  qsort(A,n,16,cmp); long k=0; for(long i=0;i<n;i++) if(i==0||A[i]!=A[i-1])A[k++]=A[i]; *cnt=k; return A;}
static u128 img(int g,u128 m){u128 o=0; for(int t=0;t<120;t++) if((m>>t)&1) o|=(u128)1<<perm[g][t]; return o;}
static long find(u128*A,long n,u128 x){long lo=0,hi=n-1;while(lo<=hi){long m=(lo+hi)/2;if(A[m]==x)return m;if(A[m]<x)lo=m+1;else hi=m-1;}return -1;}
long*uf; static long fnd(long x){while(uf[x]!=x){uf[x]=uf[uf[x]];x=uf[x];}return x;}

// ---- SERVE3: served by mask containment, tables from tabs.bin (impl B leftovers transported into SERVE2 labelling) ----
#define NRL 9387
#define NDL 6021
static u128 *TB; // 120*NRL then 1080*NDL
typedef struct{int t; u128 R;} Ent;
static Ent*LST; static long nl3; static long bstart[121]; static int baseServed[1200]; static int baseCount;
static int stamp[1200]; static int stampid=0; static u128 Fcur;
static inline int low(u128 R){return (u64)R?__builtin_ctzll((u64)R):64+__builtin_ctzll((u64)(R>>64));}
// prepare for fixed F: residual R=L&~F; resmax bounds |E\F|.
static int cmpEnt(const void*a,const void*b){return low(((const Ent*)a)->R)-low(((const Ent*)b)->R);}
static void prep(u128 F,int resmax){ Fcur=F; memset(baseServed,0,sizeof baseServed); baseCount=0;
  long cap=0; for(int t=0;t<1200;t++){ int nn=t<120?NRL:NDL; u128*m=TB+(t<120? (long)t*NRL : 120L*NRL+(long)(t-120)*NDL);
    if(t<120 && ((F>>t)&1)){baseServed[t]=1;continue;}
    for(int i=0;i<nn;i++) if((m[i]&~F)==0){baseServed[t]=1;baseCount++;break;} }
  free(LST); LST=malloc(sizeof(Ent)*(120L*NRL+1080L*NDL)); nl3=0;
  for(int t=0;t<1200;t++){ if(baseServed[t])continue; int nn=t<120?NRL:NDL; u128*m=TB+(t<120? (long)t*NRL : 120L*NRL+(long)(t-120)*NDL);
    for(int i=0;i<nn;i++){u128 R=m[i]&~F; if(pc(R)<=resmax){LST[nl3].t=t;LST[nl3].R=R;nl3++;}}}
  qsort(LST,nl3,sizeof(Ent),cmpEnt);
  // bucket by lowest residual bit; bstart[b]..bstart[b+1]
  long j=0; for(int b=0;b<=120;b++){ bstart[b]=j; while(j<nl3 && (b<120?low(LST[j].R)==b:0)) j++; }
  bstart[120]=nl3; }
// served(E), E=F u X, X given as mask (X disjoint from F)
static int served3(u128 X){ u128 E=Fcur|X; int n=pc(E)+baseCount; stampid++;
  // roots in X that are base-served were counted twice (E and base): baseServed only set for roots not in F, so subtract
  for(u128 Y=X;Y;Y&=Y-1){int b=low(Y); if(baseServed[b]) n--; stamp[b]=stampid;}
  for(u128 Y=X;Y;Y&=Y-1){int b=low(Y); for(long i=bstart[b];i<bstart[b+1];i++){ int t=LST[i].t; if(stamp[t]==stampid)continue; if((LST[i].R&~X)==0){stamp[t]=stampid;n++;}}}
  // entries with empty residual are base-served (excluded from LST)
  return n; }
// full-table served (no prep): used for spot checks
static int servedfull(u128 E){ int n=0; for(int t=0;t<1200;t++){ if(t<120&&((E>>t)&1)){n++;continue;} int nn=t<120?NRL:NDL; u128*m=TB+(t<120? (long)t*NRL : 120L*NRL+(long)(t-120)*NDL); for(int i=0;i<nn;i++) if((m[i]&~E)==0){n++;break;} } return n;}
static void loadtabs(){ FILE*f=fopen("tabs.bin","rb"); long N=120L*NRL+1080L*NDL; unsigned char*b=malloc(N*16); if(fread(b,16,N,f)!=N){fprintf(stderr,"short tabs\n");exit(1);} fclose(f); TB=malloc(N*16); for(long i=0;i<N;i++){u64 lo,hi; memcpy(&lo,b+16*i,8); memcpy(&hi,b+16*i+8,8); TB[i]=((u128)hi<<64)|lo;} free(b);}
static void servedlist3(u128 E){printf("S"); for(int t=0;t<1200;t++){ int hit=0; if(t<120&&((E>>t)&1))hit=1; else {int nn=t<120?NRL:NDL; u128*m=TB+(t<120? (long)t*NRL : 120L*NRL+(long)(t-120)*NDL); for(int i=0;i<nn;i++) if((m[i]&~E)==0){hit=1;break;}} if(hit){ if(t<120)printf(" r%d",t); else printf(" d%d",t-120);}} printf("\n");}
int main(int argc,char**argv){
  FILE*f=fopen("data.txt","r"); for(int t=0;t<120;t++)fscanf(f,"%d",&lab[t]); for(int g=0;g<8;g++)for(int t=0;t<120;t++)fscanf(f,"%d",&perm[g][t]);
  for(int t=0;t<1200;t++){u64 a,b; fscanf(f,"%llu %llu",&a,&b); OFF[t]=((u128)b<<64)|a;} fclose(f);
  // modes: pair s1 s2 | lines s k | one <mask-line-list from stdin>(served of E) 
  if(!strcmp(argv[1],"one")){ int t; u128 E=0; while(scanf("%d",&t)==1)E|=(u128)1<<t; printf("%d\n",served(E,0)); return 0;}

  if(!strcmp(argv[1],"tone")){ loadtabs(); int t; u128 E=0; while(scanf("%d",&t)==1)E|=(u128)1<<t; printf("%d\n",servedfull(E)); return 0;}
  if(!strcmp(argv[1],"tlist")){ loadtabs(); int t; u128 E=0; while(scanf("%d",&t)==1)E|=(u128)1<<t; servedlist3(E); return 0;}
  if(!strcmp(argv[1],"tcheck")){ loadtabs(); /* compare served3 with servedfull on random E=F u X */ srand(1); int s=atoi(argv[2]); long n; u128*A=flats(s,&n); int bad=0;
    for(int it=0;it<atoi(argv[3]);it++){ u128 F=A[rand()%n]; u128 G=A[rand()%n]; prep(F,pc(G&~F)); u128 X=G&~F; int a=served3(X),b=servedfull(F|X); if(a!=b){bad++;printf("MISMATCH %d %d\n",a,b);} } printf("tcheck bad=%d\n",bad); return 0;}
  int s=atoi(argv[2]); long n; u128*A=flats(s,&n); fprintf(stderr,"flats s=%d: %ld\n",s,n);
  uf=malloc(n*sizeof(long)); for(long i=0;i<n;i++)uf[i]=i;
  for(long i=0;i<n;i++)for(int g=0;g<8;g++){long j=find(A,n,img(g,A[i])); if(j<0){fprintf(stderr,"not closed\n");return 1;} long a=fnd(i),b=fnd(j); if(a!=b)uf[a]=b;}
  long reps[200],osz[200],nr=0; for(long i=0;i<n;i++)if(fnd(i)==i){reps[nr]=i;osz[nr]=0;nr++;} for(long i=0;i<n;i++){long r=fnd(i);for(long j=0;j<nr;j++)if(reps[j]==r){osz[j]++;break;}}
  fprintf(stderr,"orbits: %ld\n",nr); for(long j=0;j<nr;j++)fprintf(stderr," rep %ld size %ld lines %d\n",j,osz[j],pc(A[reps[j]]));
  int lo=0,hi=nr; if(argc>5){lo=atoi(argv[5]);hi=atoi(argv[6]);}
  int thr=argc>4?atoi(argv[4]):1000;


  if(!strcmp(argv[1],"t3")){ // t3 s3dim pairfile : for each pair E0 (list of line ids per row in file) and every F3 flat, distinct served sets
    loadtabs(); int s3=atoi(argv[2]); long n3; u128*H=flats(s3,&n3); FILE*pf=fopen(argv[3],"r"); char buf[4096]; 
    unsigned long long *seen=malloc(8*20000000L); long ns=0; long total=0; int minv=1000,maxv=0;
    while(fgets(buf,sizeof buf,pf)){ if(buf[0]!='E')continue; u128 E0=0; char*p=buf+1; int v,nc; while(sscanf(p," %d%n",&v,&nc)==1){E0|=(u128)1<<v;p+=nc;} // stops at 'S'
      prep(E0,pc(H[0])); int mx=0; for(long i=0;i<n3;i++)if(pc(H[i])>mx)mx=pc(H[i]); prep(E0,mx);
      for(long i=0;i<n3;i++){ u128 X=H[i]&~E0; int vv=served3(X); total++; if(vv<minv)minv=vv; if(vv>maxv)maxv=vv;
        unsigned long long h=1469598103934665603ULL; u128 EE=E0|X; for(int t=0;t<1200;t++){ int hit=baseServed[t]||stamp[t]==stampid||(t<120&&((EE>>t)&1)); if(hit){h^=t+1;h*=1099511628211ULL;} }
        int f=0; for(long q=0;q<ns;q++) if(seen[q]==h){f=1;break;} if(!f){ if(ns<20000000L)seen[ns++]=h; printf("E"); for(int t=0;t<120;t++)if((EE>>t)&1)printf(" %d",t); printf(" "); servedlist3(EE); fflush(stdout);} } }
    fprintf(stderr,"t3: evaluated %ld, served range [%d,%d], distinct served sets %ld\n",total,minv,maxv,ns); return 0;}
  if(!strcmp(argv[1],"tpair")||!strcmp(argv[1],"tlines")){ loadtabs(); int pair=!strcmp(argv[1],"tpair");
    int s2=pair?atoi(argv[3]):0; long n2=0; u128*B=0; int mx2=0; if(pair){B=(s2==s)?A:flats(s2,&n2); if(s2==s)n2=n; for(long i=0;i<n2;i++) if(pc(B[i])>mx2)mx2=pc(B[i]);}
    int k=pair?0:atoi(argv[3]);
    for(int j=lo;j<hi;j++){u128 F=A[reps[j]]; int best=0; u128 bE=0; long cnt=0; long hist[260]={0};
      if(pair){ prep(F,mx2); for(long i=0;i<n2;i++){u128 X=B[i]&~F; if(!X)continue; int v=served3(X); hist[v]++; if(v>best){best=v;bE=F|X;} if(v>=thr){cnt++; if(argc>7){printf("E"); for(int t=0;t<120;t++)if(((F|X)>>t)&1)printf(" %d",t); printf(" "); servedlist3(F|X);}}} }
      else { prep(F,k); int out[120],no=0; for(int t=0;t<120;t++)if(!((F>>t)&1))out[no++]=t;
        if(k==2){for(int a=0;a<no;a++)for(int b=a+1;b<no;b++){u128 X=((u128)1<<out[a])|((u128)1<<out[b]); int v=served3(X); if(v>best){best=v;bE=F|X;} if(v>=thr){cnt++; if(argc>7){printf("E"); for(int t=0;t<120;t++)if(((F|X)>>t)&1)printf(" %d",t); printf(" "); servedlist3(F|X);}}}}
        else for(int a=0;a<no;a++)for(int b=a+1;b<no;b++)for(int c=b+1;c<no;c++){u128 X=((u128)1<<out[a])|((u128)1<<out[b])|((u128)1<<out[c]); int v=served3(X); if(v>best){best=v;bE=F|X;} if(v>=thr)cnt++;} }
      int vf=servedfull(bE);
      printf("rep %d (orbit %ld, lines %d): max %d (full-table recheck %d) n>=thr:%ld E=",j,osz[j],pc(F),best,vf,cnt); for(int t=0;t<120;t++)if((bE>>t)&1)printf(" %d",t); printf("\n"); fflush(stdout);} return 0; }
  if(!strcmp(argv[1],"pair")){ int s2=atoi(argv[3]); long n2; u128*B=(s2==s)?A:flats(s2,&n2); if(s2==s)n2=n; fprintf(stderr,"second flats %ld\n",n2);
    for(int j=lo;j<hi;j++){u128 F=A[reps[j]]; int best=0; u128 bE=0; int cnt=0; for(long i=0;i<n2;i++){u128 E=F|B[i]; if(E==F)continue; int v=served(E,0); if(v>best){best=v;bE=E;} if(v>=thr){cnt++;}}
      printf("rep %d (size %ld, lines %d): max %d  E=",j,osz[j],pc(F),best); for(int t=0;t<120;t++)if((bE>>t)&1)printf(" %d",t); printf("  n>=thr:%d\n",cnt); fflush(stdout);} }
  else if(!strcmp(argv[1],"lines")){ int k=atoi(argv[3]);
    for(int j=lo;j<hi;j++){u128 F=A[reps[j]]; int out[120],no=0; for(int t=0;t<120;t++)if(!((F>>t)&1))out[no++]=t; int best=0; u128 bE=0; int cnt=0;
      int idx[4]; // k up to 3
      if(k==2){for(int a=0;a<no;a++)for(int b=a+1;b<no;b++){u128 E=F|((u128)1<<out[a])|((u128)1<<out[b]); int v=served(E,0); if(v>best){best=v;bE=E;} if(v>=thr){cnt++; if(argc>7){printf("E"); for(int t=0;t<120;t++)if((E>>t)&1)printf(" %d",t); printf(" ");servedlist(E);}}}}
      else {for(int a=0;a<no;a++)for(int b=a+1;b<no;b++)for(int c=b+1;c<no;c++){u128 E=F|((u128)1<<out[a])|((u128)1<<out[b])|((u128)1<<out[c]); int v=served(E,0); if(v>best){best=v;bE=E;} if(v>=thr)cnt++;}}
      printf("rep %d (size %ld, lines %d): max %d  E=",j,osz[j],pc(F),best); for(int t=0;t<120;t++)if((bE>>t)&1)printf(" %d",t); printf("  n>=thr:%d\n",cnt); fflush(stdout);} }
  return 0;}
