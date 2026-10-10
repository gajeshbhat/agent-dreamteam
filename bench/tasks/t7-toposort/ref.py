import heapq
def toposort(graph):
    nodes = set(graph) | {d for ds in graph.values() for d in ds}
    deps = {n: set(graph.get(n, [])) for n in nodes}
    ready = [n for n in nodes if not deps[n]]; heapq.heapify(ready)
    out = []
    while ready:
        n = heapq.heappop(ready); out.append(n)
        for m in nodes:
            if n in deps[m]:
                deps[m].discard(n)
                if not deps[m]: heapq.heappush(ready, m)
    if len(out) != len(nodes): raise ValueError('cycle')
    return out
