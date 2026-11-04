#include <vector>
#include <array>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <limits>
using namespace std;
int main(int argc,char**argv){
 if(argc!=3)return 2;ifstream in(argv[1]);int N,np;long long grid,L;in>>N>>np>>grid>>L;
 vector<long long>head(N+1),body(N+1),C(N+1);for(int i=0;i<=N;i++)in>>head[i]>>body[i]>>C[i];
 ofstream out(argv[2]);out<<"{\"status\":\"EXACT_INTEGER_UPPER_BOUND_ALL_ROOT_PATTERNS\",\"max_total_leaves\":"<<N<<",\"grid\":"<<grid<<",\"patterns\":[";
 long long global=numeric_limits<long long>::min();array<int,4>globaln{};int globalp=-1;uint64_t total=0;
 for(int p=0;p<np;p++){
  array<int,16>m;array<int,4>r{};for(int j=0;j<16;j++){in>>m[j];for(int i=0;i<4;i++)if(j>>i&1)r[i]+=m[j];}
  vector<pair<int,int>>left,right;for(int j=0;j<16;j++)if(m[j])((j&8)?right:left).push_back({j&7,m[j]});
  long long best=numeric_limits<long long>::min();array<int,4>bn{};uint64_t count=0;
  for(int a=1;a<=N-3;a++)for(int b=1;b<=N-a-2;b++)for(int c=1;c<=N-a-b-1;c++){
   int s=a+b+c;array<int,8>x{0,a,b,a+b,c,a+c,b+c,s};
   long long base=-C[a]-C[b]-C[c]-s*L-3*grid-(r[0]-2)*body[a]-(r[1]-2)*body[b]-(r[2]-2)*body[c];
   for(auto[u,n]:left)base+=n*head[x[u]];
   for(int d=1;d<=N-s;d++){
    long long v=base-C[d]-d*L-(r[3]-2)*body[d];for(auto[u,n]:right)v+=n*head[x[u]+d];count++;
    if(v>best){best=v;bn={a,b,c,d};}
   }
  }
  if(p)out<<",";out<<"{\"pattern\":"<<p<<",\"margin_upper_integer\":"<<best<<",\"child_sizes\":["<<bn[0]<<","<<bn[1]<<","<<bn[2]<<","<<bn[3]<<"],\"tuples\":"<<count<<"}";
  total+=count;if(best>global){global=best;globaln=bn;globalp=p;}
 }
 out<<"],\"global_margin_upper_integer\":"<<global<<",\"global_pattern\":"<<globalp<<",\"global_child_sizes\":["<<globaln[0]<<","<<globaln[1]<<","<<globaln[2]<<","<<globaln[3]<<"],\"total_tuples\":"<<total<<"}\n";
 cout<<"best "<<double(global)/grid<<" pattern "<<globalp<<" children "<<globaln[0]<<","<<globaln[1]<<","<<globaln[2]<<","<<globaln[3]<<" tuples "<<total<<"\n";
}
