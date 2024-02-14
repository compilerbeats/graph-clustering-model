# usage: python3 graph-clustering-model-generate.py <communities-file> <overlaps-file>
import sys
import numpy as np
import copy
import random

communities_file = sys.argv[1]
overlaps_file = sys.argv[2]

# read communities
with open(communities_file, 'r') as fp:
    communities_raw = fp.readlines()

# create 4-tupel for every community
# ( community id | number of members | members of community as set )
communities = {k: [k, len(communities_raw[k].replace('\n', '').split(' ')),
                   list(communities_raw[k].replace('\n', '').split(' '))] for k in range(0, len(communities_raw))}

# create members structure (dict)
# each entry members[some_id] = list( number of memberships | communities in which the member is included)
members = {}
for i in range(0, len(communities)):
    for member in communities[i][2]:
        if int(member) not in members:
            members[int(member)] = list()
            members[int(member)].append(0)
            members[int(member)].append(set())

        members[int(member)][0] += 1
        members[int(member)][1].add(i)

# create h(i, j) structure and read relevant value of our original clustering
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
h = np.zeros((max_community_size + 1, max_overlap + 1))

for overlaps_line in overlaps_raw:
    # one line of parts is represented as size_of_overlap, size_of_community, count
    parts = overlaps_line.strip().split(',')

    h[int(parts[1]), int(parts[0])] = int(parts[2])

print(h[6][5])

# create stubs for communities and members
communities_stubs = copy.deepcopy(communities)

# set number of members in community to 0, we will increase this number in the matching phase in order to reflect
# the structure of our original communities
for community_stub in communities_stubs.items():
    community_stub[1][1] = 0
    community_stub[1][2] = list()

# set number of memberships to 0, we will increase this number in the matching phase in order to reflect
# the structure of our original communities
members_stubs = copy.deepcopy(members)
for member_stub in members_stubs:
    members_stubs[member_stub][0] = 0
    members_stubs[member_stub][1] = set()

#### RANDOM MATCHING ####
# first we create a structure to keep track of the communities that are connected with each other based on overlaps
# in their members
community_adjacency_list = dict()
for community in communities.items():
    community_adjacency_list[community[1][0]] = list()

# we initialize our generated h(i, j) function, which should match the one of our original data
h_generated = np.zeros((max_community_size + 1, max_overlap + 1))

# print(len(community_adjacency_list))


def match_random_member(random_member_key):
    if members_stubs[random_member_key][0] == members[random_member_key][0]:
        return False

    random_community_key = random.choice(list(communities.keys()))


    # here we try to do the matching, in case we obtain a value abov eof our threshold we reverse the changes
    # if try_matching_check_h_values(random_member_key, random_community_key):


#def try_matching_check_h_values(member_key, community_key):



# matching algo:
all_matched = False
while not all_matched:
    random_member_key = random.choice(list(members.keys()))

    if not match_random_member(random_member_key):
        for member_stub in members_stubs:
            all_matched = members_stubs[random_member_key][0] == members[random_member_key][0]
            if not all_matched:
                break

        if not all_matched:
            continue

        for community_stub in communities_stubs.items():
            all_matched = community_stub[1][1] == communities_stubs[community_stub[0]][1][1]
            if not all_matched:
                break

        if not all_matched:
            continue

print('all members and communities matched!')

# print graph of generated stubs and save to file

# take random member m
# check if m already has enough memberships (i.e. members[m][0] == members_stubs[m][0])
# if yes
## choose another random member m'
# if no
## choose random community n
## does the community already have enough members (i.e. communities[n][1][1] == communities_stubs[n][1][1])?
## if yes
### choose another random community n'
## if no
### check if matching m and n would break the threshold of h(i, j)
### if yes
#### try other combination?
### if no
#### do matching of m and n (i.e. update stubs structures), and update h_generated accordingly


# alternative version of the algo:
def random_matching(communities, members, communities_stubs, members_stubs, h, h_generated):
    while True:
        # Choose a random member m
        m = random.choice(list(members_stubs.keys()))

        # Check if m already has enough memberships
        if members[m][0] == members_stubs[m][0]:
            continue

        # Choose a random community n
        n = random.choice(list(communities_stubs.keys()))

        # Check if community n already has enough members
        if communities[n][1] == communities_stubs[n][1]:
            continue

        # Check if matching m and n would break the threshold of h(i, j)
        community_size = communities_stubs[n][1]
        overlap_size = len(members_stubs[m][1].intersection(communities[n][2]))

        # TODO: check not only the current overlap, but check all overlaps of the newly added community with the ones
        # that the member is already a part of (adjacency data structure)

        # TODO: Wenn Overlap zwischen zwei Communities größer wird, dann muss man den Wert von h(i, j) mit overlap - 1
        # zuerst runterzählen, weil dieser Overlap existiert ja dann eigentlich nicht mehr
        for community_adj_candidate in members_stubs[m][1]:
            if h_generated[community_size][overlap_size] + 1 > h[community_size][overlap_size]:
                continue

        # Do matching of m and n
        community_adjacency_list[n].append(members_stubs[m][1])
        # TODO: h_generated hier updaten + Update von adjacency_list Struktur + h_generate von allen neu verbundenen
        # Communities updaten

        members_stubs[m][0] += 1
        members_stubs[m][1].add(n)
        communities_stubs[n][1] += 1
        communities_stubs[n][2].append(m)

        # Update h_generated
        h_generated[community_size][overlap_size] += 1

        # Check for completion
        if all([members_stubs[m][0] == members[m][0] for m in members_stubs]):
            break

# Example of calling the function
# random_matching(communities, members, communities_stubs, members_stubs, h, h_generated)
