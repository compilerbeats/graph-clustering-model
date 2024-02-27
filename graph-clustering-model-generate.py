# usage: python3 graph-clustering-model-generate.py <communities-file> <overlaps-file>
import sys
import numpy as np
import copy
import random
import math

communities_file = sys.argv[1]
overlaps_file = sys.argv[2]

# read communities
with open(communities_file, 'r') as fp:
    communities_raw = fp.readlines()

# create 3-tupel for every community
# ( community id | number of members | members of community as set )
communities = {k: [k, len(communities_raw[k].replace('\n', '').split(' ')),
                   set(communities_raw[k].replace('\n', '').split(' '))] for k in range(0, len(communities_raw))}

number_of_total_matches = sum(community[1] for community in communities.values())

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
    community_stub[1][2] = set()

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

print("number of total matches to be reached: " + str(number_of_total_matches))


# alternative version of the algo:
def random_matching(communities, members, communities_stubs, members_stubs, h, h_generated):
    number_of_matches = 0
    while True:
        # Choose a random member m
        m = random.choice(list(members_stubs.keys()))

        # Check if m already has enough memberships
        if members[m][0] == members_stubs[m][0]:
            print("matched all communities for member: " + str(m))
            continue

        # Choose a random community n
        n = random.choice(list(communities_stubs.keys()))

        # Check if community n already has enough members
        if communities[n][1] == communities_stubs[n][1]:
            print("matched all members for community: " + str(n))
            continue

        # Check if matching m and n would break the threshold of h(i, j) for all new overlaps
        overlapping_communities = members_stubs[m][1]
        threshold_reached = False
        for overlapping_community in overlapping_communities:
            community_size = communities_stubs[n][1]
            overlap_size = len(communities_stubs[overlapping_community][2]
                               .intersection((communities_stubs[n][2]).union({m})))

            # calculate 10% of the value in h, add it to h, and round up to get the threshold
            threshold = math.floor(h[community_size][overlap_size] * 1.1)

            if h_generated[community_size][overlap_size] + 1 > threshold:
                threshold_reached = True

            community_size = communities_stubs[overlapping_community][1]

            if h_generated[community_size][overlap_size] + 1 > threshold:
                threshold_reached = True

            if threshold_reached:
                print("reached threshold for community size: " + str(community_size) + " and size of overlap: "
                      + str(overlap_size))
                break

        # restart loop from the beginning if the current matching would reach the threshold
        if threshold_reached:
            continue

        members_stubs[m][0] += 1
        members_stubs[m][1].add(n)
        communities_stubs[n][1] += 1
        communities_stubs[n][2].add(m)

        number_of_matches += 1

        if number_of_matches % 10000 == 0:
            print("reached " + str(number_of_matches) + " matches")

        overlapping_communities = members_stubs[m][1]

        # create entry in communities "adjacency list"
        for overlapping_community in overlapping_communities:
            if any(community_adjacency_list_entry[0] == overlapping_community
                   for community_adjacency_list_entry in community_adjacency_list[n]):
                if not any(community_adjacency_list_entry[0] == n
                           for community_adjacency_list_entry in community_adjacency_list[overlapping_community]):
                    print("ERROR! Symmetry of community adjacency list broken!")
                    break

                # update community adjacency entries (symmetry)
                for community_adjacency_list_entry in community_adjacency_list[n]:
                    if community_adjacency_list_entry[0] == overlapping_community:
                        community_adjacency_list_entry[1] += 1
                        # we can exit here since we only have one entry per community
                        break

                for community_adjacency_list_entry in community_adjacency_list[overlapping_community]:
                    if community_adjacency_list_entry[0] == n:
                        community_adjacency_list_entry[1] += 1
                        # we can exit here since we only have one entry per community
                        break

                # increase h_generated value but decrease value for previous overlap size
                community_size = communities_stubs[n][1]
                overlap_size = len(communities_stubs[overlapping_community][2].intersection(communities_stubs[n][2]))

                h_generated[community_size][overlap_size] += 1
                h_generated[community_size][overlap_size - 1] -= 1

                community_size = communities_stubs[overlapping_community][1]

                h_generated[community_size][overlap_size] += 1
                h_generated[community_size][overlap_size - 1] -= 1

                print("did matching between n: " + str(n) + " and m: " + str(m) + " with already existing overlap")
            else:
                list_entry = list()
                list_entry.append(overlapping_community)
                list_entry.append(len(communities_stubs[overlapping_community][2].intersection(communities_stubs[n][2])))
                community_adjacency_list[n].append(list_entry)

                # must be symmetric
                list_entry = list()
                list_entry.append(n)
                list_entry.append(len(communities_stubs[overlapping_community][2].intersection(communities_stubs[n][2])))
                community_adjacency_list[overlapping_community].append(list_entry)

                # increase h_generated value
                community_size = communities_stubs[n][1]
                overlap_size = len(communities_stubs[overlapping_community][2].intersection(communities_stubs[n][2]))

                h_generated[community_size][overlap_size] += 1

                community_size = communities_stubs[overlapping_community][1]

                h_generated[community_size][overlap_size] += 1

                # print("did matching between n: " + str(n) + " and m: " + str(m))

        # check for completion
        if all([members_stubs[m][0] == members[m][0] for m in members_stubs]):
            break


# Example of calling the function
random_matching(communities, members, communities_stubs, members_stubs, h, h_generated)

print('all members and communities matched!')


def write_h_generated_to_file(h_generated, filename="/home/d3000/d300342/mach2-home/mpicomm/scripts/test/h_generated_output.txt"):
    with open(filename, 'w') as file:
        for community_size in range(h_generated.shape[0]):
            for overlap_size in range(h_generated.shape[1]):
                number_of_overlaps = h_generated[community_size, overlap_size]
                if number_of_overlaps > 0:  # optionally, only write non-zero values
                    file.write(f"{overlap_size}, {community_size}, {int(number_of_overlaps)}\n")


write_h_generated_to_file(h_generated)

# TODO: print graph of h_generated