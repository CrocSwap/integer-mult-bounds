// Independent finite distance-certificate checker. Apache-2.0.
// Does not perform BFS or import any construction code.
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static void require(bool ok, const char *why) {
  if (!ok) throw std::runtime_error(why);
}
static std::vector<unsigned char> read(const std::string &name, size_t size) {
  std::ifstream in(name,std::ios::binary);
  require(bool(in),"missing table");
  std::vector<unsigned char> result(size);
  in.read(reinterpret_cast<char*>(result.data()),size);
  require(size_t(in.gcount())==size && in.peek()==EOF,"table size");
  return result;
}
int main(int argc, char **argv) {
  try {
    require(argc==3,"usage: metric_check n table-prefix");
    int n=std::stoi(argv[1]); require(n>=2 && n<=5,"dimension");
    size_t size=size_t(1)<<(n*n);
    auto dist=read(std::string(argv[2])+".dist",size);
    auto last=read(std::string(argv[2])+".last",size);
    uint64_t expected=1, vertices=0, edges=0;
    uint32_t unit=0;
    for (int i=0;i<n;++i) {unit+=uint32_t(1)<<(i*n+i); expected*= (1u<<n)-(1u<<i);}
    require(dist[unit]==0 && last[unit]==255,"root");
    std::array<uint64_t,32> hist{};
    for (uint32_t x=0; x<size; ++x) {
      if (dist[x]==255) {require(last[x]==255,"unreachable predecessor"); continue;}
      require(dist[x]<hist.size(),"distance range");
      ++vertices; ++hist[dist[x]];
      // Decode once. Row addition below rebuilds the changed field rather
      // than reusing the search program's shift/XOR update expression.
      std::array<uint32_t,5> row{}, place{};
      uint32_t rest=x;
      for (int i=0;i<n;++i) {row[i]=rest % (1u<<n); rest/=1u<<n; place[i]=1u<<(n*i);}
      if (x != unit) {
        require(dist[x]>0,"extra root");
        unsigned g=last[x];
        require(g<unsigned(n*n) && g/n!=g%n,"predecessor generator");
        uint32_t pred=x-row[g/n]*place[g/n]+(row[g/n]^row[g%n])*place[g/n];
        require(unsigned(dist[pred])+1==unsigned(dist[x]),"predecessor descent");
      }
      for (int a=0;a<n;++a) for (int b=0;b<n;++b) if (a!=b) {
        uint32_t y=x-row[a]*place[a]+(row[a]^row[b])*place[a];
        require(dist[y]!=255,"edge closure");
        int delta=int(dist[y])-int(dist[x]);
        require(delta>=-1 && delta<=1,"edge Lipschitz"); ++edges;
      }
    }
    require(vertices==expected,"GL cardinality");
    std::cout<<"{\"n\":"<<n<<",\"vertices\":"<<vertices<<",\"directed_edges\":"<<edges<<",\"histogram\":[";
    size_t end=hist.size(); while (end && hist[end-1]==0) --end;
    for(size_t i=0;i<end;++i) std::cout<<(i?",":"")<<hist[i];
    std::cout<<"]}\n";
  } catch (const std::exception &e) {std::cerr<<e.what()<<'\n'; return 1;}
}
