#include <array>
#include <vector>
#include <map>
#include <set>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <algorithm>
using namespace std;
struct M {array<unsigned char,6> a;array<unsigned char,64> x;};
M make(array<unsigned char,6>a){M m;m.a=a;m.x[0]=0;for(int i=1;i<64;i++){int b=__builtin_ctz(i);m.x[i]=m.x[i^(1<<b)]^a[b];}return m;}
M eye(){return make({1,2,4,8,16,32});}
bool commute(const M&a,const M&b){for(int i=0;i<6;i++)if(b.x[a.a[i]]!=a.x[b.a[i]])return false;return true;}
M mul(const M&a,const M&b){array<unsigned char,6>z;for(int i=0;i<6;i++)z[i]=b.x[a.a[i]];return make(z);}
M complement(M a){for(int i=0;i<6;i++)a.a[i]^=1<<i;return make(a.a);}
int rankm(M a){int r=0;for(int j=5;j>=0;j--){int p=r;while(p<6&&!(a.a[p]>>j&1))p++;if(p==6)continue;swap(a.a[p],a.a[r]);for(int i=r+1;i<6;i++)if(a.a[i]>>j&1)a.a[i]^=a.a[r];r++;}return r;}
uint64_t profile(const array<M,4>&p){uint64_t k=0;int total=0;for(int m=0;m<16;m++){M q=eye();for(int i=0;i<4;i++)q=mul(q,(m>>i&1)?p[i]:complement(p[i]));int r=rankm(q);total+=r;k|=uint64_t(r)<<(3*m);}if(total!=6)throw runtime_error("bad profile");return k;}
struct Witness{array<int,4> sites,ids;array<M,4> p;};
int main(int argc,char**argv){
 if(argc!=3)return 2;ifstream in(argv[1]);int ng;in>>ng;vector<int> sites(ng);vector<vector<M>>g(ng);
 for(int j=0;j<ng;j++){int n;in>>sites[j]>>n;g[j].resize(n);for(auto&m:g[j]){array<unsigned char,6>a;for(int k=0;k<6;k++){int z;in>>z;a[k]=z;}m=make(a);}}
 if(sites!=vector<int>({0,1,3,5,6}))throw runtime_error("unexpected active sites");
 // Cached compatibility lists from the three interior sites to each end.
 array<array<vector<vector<int>>,3>,2> compatible;
 for(int e=0;e<2;e++)for(int j=0;j<3;j++){
  int end=e?4:0,mid=j+1;compatible[e][j].resize(g[mid].size());
  for(int i=0;i<(int)g[mid].size();i++)for(int v=0;v<(int)g[end].size();v++)if(commute(g[mid][i],g[end][v]))compatible[e][j][i].push_back(v);
 }
 map<uint64_t,Witness>patterns;uint64_t cliques=0,tests=0;map<string,uint64_t>byset;
 auto intersection=[](const vector<int>&a,const vector<int>&b){vector<int>z;set_intersection(a.begin(),a.end(),b.begin(),b.end(),back_inserter(z));return z;};
 auto save=[&](array<int,4> gg,array<int,4> ids){array<M,4>p;array<int,4> ss;string name;for(int k=0;k<4;k++){p[k]=g[gg[k]][ids[k]];ss[k]=sites[gg[k]];name+=to_string(ss[k]);}uint64_t key=profile(p);cliques++;byset[name]++;if(!patterns.count(key))patterns[key]={ss,ids,p};};
 // Both ends plus two of the three interior sites.
 for(int u=1;u<=3;u++)for(int v=u+1;v<=3;v++){
  for(int a=0;a<(int)g[u].size();a++)for(int b=0;b<(int)g[v].size();b++){
   if(!commute(g[u][a],g[v][b]))continue;
   auto left=intersection(compatible[0][u-1][a],compatible[0][v-1][b]);
   auto right=intersection(compatible[1][u-1][a],compatible[1][v-1][b]);
   for(int l:left)for(int r:right){tests++;if(commute(g[0][l],g[4][r]))save({0,u,v,4},{l,a,b,r});}
  }
  cerr<<"PAIR "<<sites[u]<<","<<sites[v]<<" cliques "<<cliques<<" patterns "<<patterns.size()<<" comparisons "<<tests<<"\n";
 }
 // One end plus all three interior sites.
 for(int a=0;a<(int)g[1].size();a++)for(int b=0;b<(int)g[2].size();b++){
  if(!commute(g[1][a],g[2][b]))continue;
  for(int c=0;c<(int)g[3].size();c++){
   if(!commute(g[1][a],g[3][c])||!commute(g[2][b],g[3][c]))continue;
   for(int e=0;e<2;e++){
    auto ends=intersection(intersection(compatible[e][0][a],compatible[e][1][b]),compatible[e][2][c]);
    for(int d:ends){if(e)save({1,2,3,4},{a,b,c,d});else save({0,1,2,3},{d,a,b,c});}
   }
  }
 }
 ofstream out(argv[2]);out<<"{\"status\":\"EXACT_ALL_35_FOUR_FULL_SITE_RANK23_PATTERNS\",\"commuting_cliques\":"<<cliques<<",\"endpoint_pair_tests\":"<<tests<<",\"pattern_count\":"<<patterns.size()<<",\"site_sets\":{";bool first=true;for(auto&kv:byset){if(!first)out<<",";first=false;out<<"\""<<kv.first<<"\":"<<kv.second;}out<<"},\"patterns\":[";first=true;
 for(auto&kv:patterns){if(!first)out<<",";first=false;auto&w=kv.second;out<<"{\"masks\":[";for(int i=0;i<16;i++){if(i)out<<",";out<<((kv.first>>(3*i))&7);}out<<"],\"sites\":[";for(int i=0;i<4;i++){if(i)out<<",";out<<w.sites[i];}out<<"],\"projectors\":[";for(int j=0;j<4;j++){if(j)out<<",";out<<"[";for(int i=0;i<6;i++){if(i)out<<",";out<<int(w.p[j].a[i]);}out<<"]";}out<<"]}";}
 out<<"]}\n";cout<<"cliques "<<cliques<<" patterns "<<patterns.size()<<" comparisons "<<tests<<"\n";
}
