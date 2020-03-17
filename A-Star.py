"""
        *** Unidirectional A-Star algorithm ***

Useful for real road network graph problems, on a planar map/grid.

n - number of nodes 
m - number of edges

If the graph isn't dense, ie. it's sparse, it's better to implement
priority queue as heap than as array.
A graph is sparse when n and m are of the same order of magnitude.

Here, priority queue is implemented by using module heapq.

We put (dist, name) into heap, where dist is f(v), and f(v) = g(v) + h(v),
that is, known part + heuristic part.
Known part is correct distance from starting vertex, s, to this one, v.
Heuristic part is estimation from this vertex, v, to the target vertex, t.

This version of the algorithm assumes that we are given
coordinates of vertices, so we can calculate Euclidean
distances and use it as our heuristics function.
An alternative heuristic would be Manhattan distance,
but Euclidean is used in a case like this (road network).

This is plain unidirectional A-Star algorithm, without landmarks.
This is directed search, thanks to heuristic (potential) function.
It represents Dijkstra with Potentials.
This means that this is just plain Dijkstra with new edge weights.
Actually, if heuristic (potential) function is identical to 0,
this is identical to the UCS Dijkstra.
The higher the potential function, the smaller the set of vertices
scanned (in the closed set). Of course, it has to be feasible.
It can be shown that any lower-bounding algorithm with a nonnegative
potential function visits no more vertices than Dijkstra's algorithm.

It's probably the best to compute the heuristic on the fly.
A-Star is directed search, which means not many vertices
will be processed. If, one the other hand, we want to precompute
the heuristic function, we have to do that for every vertex of the graph,
because we don't know in advance which vertices will be processed.
In each query, the heuristic will be different, because target vertex
will be different, and heuristic is target-dependent.

A-Star with heuristics doesn't need the preprocessing phase.
We can have it, but it will only make the algorithm slower.
In other words, it doesn't make sense. That's because heuristic values depend
on a single query - they are not common to many queries in a graph.

This version of the algorithm doesn't reconstruct the shortest path.
It only computes its length and returns it.

Fastest if f & g are arrays.
Slightly slower if f & g are maps (dictionaries)
Way slower if f & g are arrays and h == 0 (plain Dijkstra UCS).
Memory consumption is the same in all three cases.
"""


import sys
import math
import heapq



class AStar:
    def __init__(self, n, adj, cost, x, y):
        self.n = n;
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6
        self.f = [self.inf] * n     # f(v) = g(v) + h(v); these are new distances, with potential h (h(v) is computed on the fly); Dijkstra UCS now works with them (this is self.distance in Dijkstra); self.f can be a map (dictionary)
        self.g = [self.inf] * n     # this is the known part of the distance; h is the heuristic part; this is the true distance from starting vertex to v; self.g can be a map (dictionary)
        #self.f = {}
        #self.g = {}
        self.closed = set()
        self.valid = [True] * n     # is vertex (name) valid or not - it's valid while name (vertex) is in open set (in heap)
        # Coordinates of the nodes
        self.x = x
        self.y = y

    def clear(self):
        self.f = [self.inf] * self.n
        self.g = [self.inf] * self.n
        #for i in range(self.n):     # we have to "reset" dictionaries this way, even for the first query; this is proper initialization; we can't use method clear() on these dictionaries here, because that would be a mistake
        #    self.f[i] = self.inf
        #    self.g[i] = self.inf
        self.closed.clear()
        self.valid = [True] * self.n

    # Returns the distance from s to t in the graph, or -1 if t is unreachable from s
    def query(self, s, t):
        self.clear()
        open = []      # elements are tuples (f(v), v)
        
        self.g[s] = 0
        self.f[s] = self.g[s] + math.sqrt((self.x[s] - self.x[t])**2 + (self.y[s] - self.y[t])**2)
        heapq.heappush(open, (self.f[s], s))

        while open:
            # the inner while loop removes and returns the best vertex
            best = None
            name = None
            while open:
                best = heapq.heappop(open)
                name = best[1]
                if self.valid[name]:
                    self.valid[name] = False;
                    break
            if name == t:
                break
            self.closed.add(name)       # also ok: self.closed.add(best)
            for i in range(len(self.adj[name])):
                neighbor = self.adj[name][i]
                if neighbor in self.closed:     # also ok: if (self.f[neighbor], neighbor) in self.closed:
                    continue
                temp_g = self.g[name] + self.cost[name][i]
                if (self.f[neighbor], neighbor) not in open:
                    h = math.sqrt((self.x[neighbor] - self.x[t])**2 + (self.y[neighbor] - self.y[t])**2)
                    self.g[neighbor] = temp_g
                    self.f[neighbor] = temp_g + h
                    heapq.heappush(open, (self.f[neighbor], neighbor))
                    continue
                if self.g[neighbor] > temp_g:
                    h = math.sqrt((self.x[neighbor] - self.x[t])**2 + (self.y[neighbor] - self.y[t])**2)
                    self.g[neighbor] = temp_g
                    self.f[neighbor] = temp_g + h
                    heapq.heappush(open, (self.f[neighbor], neighbor))

        return self.g[t] if self.g[t] < self.inf else -1    #same as: return int(self.f[t]) if self.f[t] < self.inf else -1


if __name__ == '__main__':
    input = sys.stdin.read()    # Python 2
    data = list(map(int, input.split()))
    n, m = data[0:2]    # number of nodes, number of edges; nodes are numbered from 1 to n
    data = data[2:]
    x = [0] * n
    y = [0] * n
    adj = [[] for _ in range(n)]
    cost = [[] for _ in range(n)]
    # coordinates x and y of the corresponding node
    for i in range(n):
        x[i] = data[i << 1]
        y[i] = data[(i << 1) + 1]
    data = data[2*n:]
    # directed edge (u, v) of length c from the node number u to the node number v
    for e in range(m):
        u = data[3*e]
        v = data[3*e+1]
        c = data[3*e+2]
        adj[u-1].append(v-1)
        cost[u-1].append(c)
    astar = AStar(n, adj, cost, x, y)
    data = data[3*m:]
    # the number of queries for computing the distance
    q = data[0]
    data = data[1:]
    # s and t are numbers ("names") of two nodes to compute the distance from s to t
    for i in range(q):
        s = data[i << 1]
        t = data[(i << 1) + 1]
        print(astar.query(s-1, t-1))
