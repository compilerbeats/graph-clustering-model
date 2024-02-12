# usage: python3 graph-clustering-model-generate.py <communities-file> <overlaps-file>
import sys
import numpy as np

communities_file = sys.argv[1]
overlaps_file = sys.argv[2]

# read communities
with open(communities_file, 'r') as fp:
    communities_raw = fp.readlines()

# create 4-tupel for every community
# ( community id | number of members | size of overlap | members of community as set )
communities = {k: [k, len(communities_raw[k].replace('\n', '').split(' ')), 0,
                   list(communities_raw[k].replace('\n', '').split(' '))] for k in range(0, len(communities_raw))}

# create members structure (dict)
# each entry members[some_id] reflects the number of memberships
members = {}
for i in range(0, len(communities)):
    for member in communities[i][3]:
        if int(member) not in members:
            members[int(member)] = 0

        members[int(member)] += 1

# create h(i) structure and read relevant value of our original clustering
with open(overlaps_file) as fp:
    overlaps_raw = fp.readlines()

max_community_size = max(communities[k][1] for k in communities)

max_overlap = 0
for overlaps_line in overlaps_raw:
    parts = overlaps_line.strip().split(',')
    if max_overlap < int(parts[0]):
        max_overlap = int(parts[0])

print(max_overlap)

# dimensions: y, x
# thus, community_size, overlap_size
h_i = np.zeros((max_community_size + 1, max_overlap + 1))

for overlaps_line in overlaps_raw:
    # one line of parts is represented as size_of_overlap, size_of_community, count
    parts = overlaps_line.strip().split(',')

    h_i[int(parts[1]), int(parts[0])] = int(parts[2])

print(h_i[6][5])

h_i_generated = np.zeros((max_community_size + 1, max_overlap + 1))

# create stubs for communities and members
# TODO