// SPDX-License-Identifier: Apache-2.0
// Exact bipartite flow. The Python checker independently validates the certificate.
#include <algorithm>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

using Count = __int128_t;

Count read_count() {
    std::string digits;
    if (!(std::cin >> digits) || digits.empty() || digits.size() > 37)
        throw std::runtime_error("Invalid positive integer mass");
    Count out = 0;
    for (const char c : digits) {
        if (c < '0' || c > '9') throw std::runtime_error("Expected decimal mass");
        out = 10 * out + c - '0';
    }
    return out;
}

void print_count(Count value) {
    std::string s;
    do {
        s.push_back('0' + static_cast<int>(value % 10));
        value /= 10;
    } while (value);
    std::reverse(s.begin(), s.end());
    std::cout << s;
}

struct Arc { Count capacity; int target, reverse; };

class Network {
    std::vector<std::vector<Arc>> arcs;
    std::vector<int> distance, current;
public:
    explicit Network(int nodes): arcs(nodes), distance(nodes), current(nodes) {}
    void add(int src, int dst, Count cap) {
        arcs[src].push_back({cap,dst,static_cast<int>(arcs[dst].size())});
        arcs[dst].push_back({0,src,static_cast<int>(arcs[src].size())-1});
    }
    bool levels(int source, int sink) {
        std::fill(distance.begin(),distance.end(),-1);
        std::queue<int> visit;
        distance[source]=0;
        visit.push(source);
        while (!visit.empty()) {
            int current_node=visit.front(); visit.pop();
            for (const auto& edge : arcs[current_node]) {
                if (edge.capacity && distance[edge.target]<0) {
                    distance[edge.target]=distance[current_node]+1;
                    visit.push(edge.target);
                }
            }
        }
        return distance[sink]>=0;
    }
    Count send(int source, int sink, Count limit) {
        if (source==sink) return limit;
        for (int& i=current[source]; i<static_cast<int>(arcs[source].size()); ++i) {
            auto& edge=arcs[source][i];
            if (edge.capacity==0 || distance[edge.target]!=distance[source]+1) continue;
            const Count flow=send(edge.target,sink,std::min(edge.capacity,limit));
            if (!flow) continue;
            edge.capacity-=flow;
            arcs[edge.target][edge.reverse].capacity+=flow;
            return flow;
        }
        return 0;
    }
    Count solve(int source, int sink, Count bound) {
        Count total=0;
        while (levels(source,sink)) {
            std::fill(current.begin(),current.end(),0);
            while (auto flow=send(source,sink,bound)) total+=flow;
        }
        return total;
    }
    void certificate(int targets,int paid) const {
        for (int src=0; src<targets; ++src) {
            for (const auto& edge : arcs[src]) {
                if (edge.target<targets || edge.target>=targets+paid) continue;
                const Count flow=arcs[edge.target][edge.reverse].capacity;
                if (!flow) continue;
                std::cout << src << ' ' << edge.target-targets << ' ';
                print_count(flow);
                std::cout << '\n';
            }
        }
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int targets,paid;
    if (!(std::cin>>targets>>paid) || targets<=0 || paid<=0) return 1;
    const int source=targets+paid, sink=source+1;
    Network graph(sink+1);
    Count demand=0;
    for (int i=0; i<targets; ++i) {
        const Count mass=read_count();
        demand+=mass;
        graph.add(source,i,mass);
    }
    for (int i=0; i<paid; ++i) {
        const Count mass=read_count();
        int size;
        if (!(std::cin>>size) || size<=0) return 2;
        graph.add(targets+i,sink,mass);
        for (int j=0; j<size; ++j) {
            int target;
            if (!(std::cin>>target) || target<0 || target>=targets) return 3;
            graph.add(target,targets+i,demand);
        }
    }
    const Count matched=graph.solve(source,sink,demand);
    print_count(demand-matched);
    std::cout << '\n';
    if (matched==demand) graph.certificate(targets,paid);
}
