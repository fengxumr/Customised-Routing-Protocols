import sys, numpy, math, collections

NETWORK = sys.argv[1]
ROUTING = sys.argv[2]
T_FILE = sys.argv[3]
W_FILE = sys.argv[4]
RATE = sys.argv[5]                  # the number of packets per second
CONS = 1 / int(RATE)

def dijktra(routing, topo_keys, src, dest):
    dist = dict((k, math.inf) for k in topo_keys)
    dist[src] = 0
    pred = dict((k, '') for k in topo_keys)
    vSet = set(topo_keys)
    while vSet:
        vMin = ''
        vMinVal = math.inf
        for v in vSet:
            if dist[v] < vMinVal:
                vMin = v
                vMinVal = dist[v]
        if vMin:
            for v in topo[vMin]:
                if routing == 'SHP':
                    if dist[vMin] + 1 < dist[v]:
                        dist[v] = dist[vMin] + 1
                        pred[v] = vMin
                elif routing == 'SDP':
                    if dist[vMin] + topo[vMin][v][0] < dist[v]:
                        dist[v] = dist[vMin] + topo[vMin][v][0]
                        pred[v] = vMin
                elif routing == 'LLP':
                    new_value = topo[vMin][v][2] / topo[vMin][v][1]
                    if dist[vMin] < dist[v] and new_value < dist[v]:
                        dist[v] = dist[vMin] if new_value < dist[vMin] else new_value
                        pred[v] = vMin      
                else:
                    raise ValueError
            vSet.remove(vMin)
        else:
            vSet = set()
    cur = dest
    path = [dest]
    while not (cur == '' or cur == src):
        cur = pred[cur]
        path.insert(0, cur)
    ran = range(len(path) - 1)
    for i in ran:
        if topo[path[i]][path[i + 1]][2] >= topo[path[i]][path[i + 1]][1]:
            return False
    return path if path[0] == src else False

def simulation(path, flag):                     # flag = -1: release; flag = 1: execute
    ran = range(len(path) - 1)
    for i in ran:
        topo[path[i]][path[i + 1]][2] += flag

def sort_insert(workload, path):
    ran = range(len(workload))
    for i in ran:
        if workload[i][0] >= path[0]:
            workload.insert(i, path)
            return

with open(T_FILE) as f:             # topo[node_A_index][node_B_index] = [propagation_delay, N_circuit, N_circuit_cal]
    topology = {(b[0], b[1]): [int(b[2]), int(b[3]), 0] for b in [a.split() for a in f.read().split("\n")]}
    topo = collections.defaultdict(dict)
    for i in topology.keys():
        topo[i[0]][i[1]] = topology[i]
        topo[i[1]][i[0]] = topology[i]

with open(W_FILE) as f:             # [[start_time, end_time, source_node_index, destination_node_index], ...]
    workload = [[float(b[0]), float(b[0]) + float(b[3]), b[1], b[2]] for b in [a.split() for a in f.read().split("\n")]]      # circuit
    total_request = len(workload)
    if NETWORK == 'PACKET':
        workload = sorted([[b, b + CONS, a[2], a[3]] for a in workload for b in list(numpy.arange(a[0], a[1], CONS))])        # packet

topo_keys = topo.keys()
success_times = 0
block_times = 0
total_hops = 0
total_delay = 0

while workload:
    item = workload.pop(0)
    if len(item) == 4:                          # item = [start_time, end_time, source_node_index, destination_node_index]]
        path = dijktra(ROUTING, topo_keys, item[2], item[3])
        
        if path:
            total_hops += len(path) - 1

            ran = range(len(path) - 1)
            for i in ran:
                total_delay += topo[path[i]][path[i + 1]][0]

            success_times += 1
            simulation(path, 1)                 # 1 for execute
            path_release = [item[1], path]      # [end_time, path]
            sort_insert(workload, path_release)
        else:
            block_times += 1
    else:                                       # item = [end_time, path]
        path = item[1]
        simulation(path, -1)                    # -1 for release

if NETWORK == 'CIRCUIT':
    print('total number of virtual circuit requests:', total_request)
    print('number of successfully routed requests:', success_times)
    print('percentage of routed request: {:.6f}'.format(success_times / total_request * 100))
    print('number of blocked requests:', block_times)
    print('percentage of blocked request: {:.6f}'.format(block_times / total_request * 100))
    print('average number of hops per circuit: {:.7f}'.format(total_hops / success_times))
    print('average cumulative propagation delay per circuit: {:.5f}'.format(total_delay / success_times))
    print()

if NETWORK == 'PACKET':
    print('total number of virtual circuit requests:', total_request)
    print('total number of packets:', success_times + block_times)
    print('number of successfully routed packets:', success_times)
    print('percentage of routed packets: {:.6f}'.format(success_times / (success_times + block_times) * 100))
    print('number of blocked packets:', block_times)
    print('percentage of blocked packets: {:.6f}'.format(block_times / (success_times + block_times) * 100))
    print('average number of hops per circuit: {:.7f}'.format(total_hops / success_times))
    print('average cumulative propagation delay per circuit: {:.5f}'.format(total_delay / success_times))
    print()
































