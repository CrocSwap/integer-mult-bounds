// Exact finite negative-basis exceptional NE ranks, with no assumed profile.
// CRT/Hadamard proves zeros; modular nonzero minors prove nonzeros.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
using Triple=std::array<uint8_t,3>;
constexpr int a=23,b=25,d=47;
int64_t mul(int64_t x,int64_t y,int64_t p){return x*y%p;}
int64_t power(int64_t x,int64_t n,int64_t p){int64_t out=1;for(;n;n>>=1,x=mul(x,x,p))if(n&1)out=mul(out,x,p);return out;}
bool prime(int64_t p){if(p<2)return false;if(!(p&1))return p==2;for(int64_t i=3;i*i<=p;i+=2)if(p%i==0)return false;return true;}
std::array<int,d> rows,cols;
std::vector<std::pair<int,int>> pivots(const Triple&T,const Triple&S,int64_t p){
 int64_t x[a],y[b],M[d][d];
 for(int i=0;i<a;i++)x[i]=(i==T[0]||i==T[1]||i==T[2])?78:-858;
 for(int i=0;i<b;i++)y[i]=(i==S[0]||i==S[1]||i==S[2])?77:-924;
 for(int i=0;i<d;i++)for(int j=0;j<d;j++){
  int64_t z=-66;if(rows[i]==cols[j])z+=x[rows[i]];if(i%b==(528+j)%b)z+=y[i%b];assert(std::abs(z)<=1848);M[i][j]=(z%p+p)%p;
 }
 std::vector<std::pair<int,int>> result;
 for(int i=0;i<d;i++){
  int c=d-1;while(c>=0&&!M[i][c])c--;if(c<0)continue;
  result.push_back({i,c});int64_t inverse=power(M[i][c],p-2,p);
  for(int r=i+1;r<d;r++)if(M[r][c]){
   int64_t ratio=mul(M[r][c],inverse,p);
   for(int j=0;j<c;j++)if(M[i][j]){int64_t z=M[r][j]-mul(ratio,M[i][j],p);M[r][j]=z<0?z+p:z;}
   M[r][c]=0;
  }
 }
 return result;
}
int main(int argc,char**argv){
 assert(argc==4);int part=std::stoi(argv[2]),parts=std::stoi(argv[3]);assert(parts>0&&part>=0&&part<parts);
 std::ifstream input(argv[1],std::ios::binary);uint32_t count;input.read(reinterpret_cast<char*>(&count),4);assert(count==192596);
 for(int i=0;i<a;i++)rows[i]=cols[i]=i;rows[a]=a-1;cols[a]=0;for(int i=0;i<a;i++)rows[a+1+i]=cols[a+1+i]=i;
 std::vector<int64_t> primes;for(int64_t p=2147483647;primes.size()<21;p-=2)if(prime(p))primes.push_back(p);
 cpp_int bound=1,product=1;for(int i=0;i<24;i++)bound*=47;for(int i=0;i<47;i++)bound*=1848;for(auto p:primes)product*=p;assert(product>bound);
 uint32_t checked=0;int64_t deficient_field_ranks=0;std::map<std::vector<int>,uint32_t> profiles;std::map<std::vector<int>,uint32_t> representatives;
 for(uint32_t k=0;k<count;k++){
  uint32_t index;Triple T,S;input.read(reinterpret_cast<char*>(&index),4);input.read(reinterpret_cast<char*>(T.data()),3);input.read(reinterpret_cast<char*>(S.data()),3);assert(input);
  if(k%parts!=uint32_t(part))continue;
  std::array<std::array<int,d+1>,d+1> best{};
  for(auto p:primes){
   auto pv=pivots(T,S,p);if(pv.size()!=d)deficient_field_ranks++;
   std::array<std::array<int,d+1>,d+1> ranks{};for(auto [r,c]:pv)ranks[r+1][c]=1;
   for(int r=1;r<=d;r++)for(int c=d-1;c>=0;c--){ranks[r][c]+=ranks[r-1][c]+ranks[r][c+1]-ranks[r-1][c+1];best[r][c]=std::max(best[r][c],ranks[r][c]);}
  }
  std::vector<std::pair<int,int>> exact;
  for(int r=1;r<=d;r++)for(int c=0;c<d;c++){int z=best[r][c]-best[r-1][c]-best[r][c+1]+best[r-1][c+1];assert(z==0||z==1);if(z)exact.push_back({r-1,c});}
  assert(exact.size()==d);std::vector<int> runs;int length=0;
  for(size_t i=0;i<exact.size();i++){if(i&&exact[i].first==exact[i-1].first+1&&exact[i].second==exact[i-1].second+1)length++;else{if(length)runs.push_back(length);length=1;}}
  if(length)runs.push_back(length);profiles[runs]++;if(!representatives.count(runs))representatives[runs]=index;checked++;
  if(checked%10000==0)std::cerr<<"Exact exceptional NE ranks "<<checked<<" part "<<part<<"\n";
 }
 char extra;assert(!input.read(&extra,1));assert(checked==(count+parts-1-part)/parts);
 std::cout<<"{\"status\":\"EXACT COMPLETE EXCEPTION PART NE RANKS\",\"part\":"<<part<<",\"parts\":"<<parts<<",\"input_pairs\":"<<count<<",\"checked_pairs\":"<<checked<<",\"integer_matrix_scale\":66,\"entry_absolute_bound\":1848,\"minor_absolute_bound\":\""<<bound<<"\",\"prime_product\":\""<<product<<"\",\"field_replays\":"<<int64_t(checked)*primes.size()<<",\"deficient_field_ranks\":"<<deficient_field_ranks<<",\"primality_trial_division\":true,\"primes\":[";
 for(size_t i=0;i<primes.size();i++){if(i)std::cout<<",";std::cout<<primes[i];}std::cout<<"],\"profiles\":[";size_t written=0;
 for(auto&[runs,n]:profiles){if(written++)std::cout<<",";std::cout<<"{\"count\":"<<n<<",\"representative_pair_index\":"<<representatives[runs]<<",\"null_corner_runs\":[";for(size_t i=0;i<runs.size();i++){if(i)std::cout<<",";std::cout<<runs[i];}std::cout<<"]}";}std::cout<<"]}\n";
}
