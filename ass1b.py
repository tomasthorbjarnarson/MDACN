import csv
from pdb import set_trace
from pprint import pprint
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import math
from random import randint
import random


data = []
nodes = set()
links = set()

with open('manufacturing_emails_temporal_network.csv') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  line_count = 0
  for row in csv_reader:
    if line_count != 0:
      n1 = int(row[0])
      n2 = int(row[1])
      t = int(row[2])
      data.append((n1, n2,t))
      nodes.add(n1)
      nodes.add(n2)
      #links.add('-'.join([row[0],row[1]]))
      links.add((n1,n2))
      
    line_count += 1
G = nx.Graph()
G.add_edges_from(links)

# 9
calc_9 = False
if calc_9:
  N = 100
  T = 57791
  num_nodes = len(nodes)
  num_links = len(links)
  infected_over_time = np.zeros((N, T+1))

  for it in range(N):
    infections = set()
    seed = randint(1, num_nodes)
    #seed = it+1
    infections.add(seed)
    infected_over_time[it,0] = 1
    t = 1
    tmp_infections = set()
    for row in data:
      if row[2] != t:
        infections = infections.union(tmp_infections)
        tmp_infections = set()
        infected_over_time[it,t] = len(infections)
        t = row[2]
      #tmp_infections = set(infections)
      if row[0] in infections:
        tmp_infections.add(row[1])
      if row[1] in infections:
        tmp_infections.add(row[0])
      
    infected_over_time[it,t] = len(infections)

  print(infected_over_time)

  fig = plt.figure(0)
  x = range(0,T+1)
  y = np.mean(infected_over_time,axis=0)
  yerr = np.std(infected_over_time,axis=0)
  plt.xlabel('Timestamps t')
  plt.ylabel('Average number infected nodes E[I(t)]')
  plt.errorbar(x,y,yerr=yerr,ecolor='c')
  #plt.plot(x,y,color='b')
  #plt.plot(x,y-np.power(yerr,1),color='r')
  #plt.plot(x,y+np.power(yerr,1),color='m')
  #for i in range(N):
  #  plt.plot(x,infected_over_time[i])
  #plt.xlim(0,T+1)
  fig = plt.figure(1)
  plt.errorbar(x,y,yerr=yerr,elinewidth=0.05,ecolor='c')
  plt.show()

# 10
T = 57791
thresh = 0.8
num_nodes = len(nodes)
num_links = len(links)
infections = set()
node_influence = []
for node in nodes:
  infections = set([node])
  t = 1
  tmp_infections = set()
  for row in data:
    if row[2] != t:
      if len(infections)/num_nodes >= thresh:
        break
      infections = infections.union(tmp_infections)
      tmp_infections = set()
      t = row[2]
    if row[0] in infections:
      tmp_infections.add(row[1])
    if row[1] in infections:
      tmp_infections.add(row[0])
  node_influence.append(t)
print(node_influence)

# 11
degrees = [0]*(num_nodes + 1)
for i in links:
  degrees[i[0]] += 1
  degrees[i[1]] += 1
degrees = degrees[1:]

adjacency = np.zeros((num_nodes,num_nodes))
for i in links:
  adjacency[i[0]-1,i[1]-1] = 1
  adjacency[i[1]-1,i[0]-1] = 1

clust_coeffs = []
for i in nodes:
  neighbor_links = []
  neighbor_link_count = 0
  for j in filter(lambda x: x[0] == i or x[1] == i, links):
    if j[0] == i:
      neighbor_links.append(j[1])
    else:
      neighbor_links.append(j[0])
  for x in neighbor_links:
    for y in neighbor_links:
      neighbor_link_count += adjacency[x-1,y-1]
  neighbor_link_count = neighbor_link_count/2
  if degrees[i-1] == 1:
    clust_coeffs.append(0)
  else:
    clust_coeffs.append(neighbor_link_count/((degrees[i-1]*(degrees[i-1]-1))/2))
clust_coeff =  np.mean(clust_coeffs)

node_stats = {}
influence_by_node = []
degree_by_node = []
clust_coeff_by_node = []
for node in nodes:
  node_stats[str(node)] = {
    'degree': degrees[node-1],
    'influence': node_influence[node-1],
    'clust_coeff': clust_coeffs[node-1]
  }
  influence_by_node.append((node, node_influence[node-1]))
  degree_by_node.append((node, degrees[node-1]))
  clust_coeff_by_node.append((node, clust_coeffs[node-1]))
influence_by_node = sorted(influence_by_node,key=lambda x: x[1])
degree_by_node = sorted(degree_by_node,key=lambda x: x[1], reverse=True)
clust_coeff_by_node = sorted(clust_coeff_by_node,key=lambda x: x[1], reverse=True)

x = np.linspace(0.05,0.5,10)
y1 = []
y2 = []
for f in x:
  f_nodes = math.floor(f*num_nodes)
  inf_nodes = [n for (n,val) in influence_by_node[0:f_nodes]]
  deg_nodes = [n for (n,val) in degree_by_node[0:f_nodes]]
  clust_nodes = [n for (n,val) in clust_coeff_by_node[0:f_nodes]]
  deg_intersect = set(inf_nodes).intersection(set(deg_nodes))
  clust_intersect = set(inf_nodes).intersection(set(clust_nodes))
  y1.append(len(deg_intersect)/f_nodes)
  y2.append(len(clust_intersect)/f_nodes)

# 12
hops = nx.shortest_path(G)
hopcount_by_node = []
for i in nodes:
  hopcount = 0
  for j in nodes:
    hopcount += len(hops[i][j])
  hopcount_by_node.append((i,hopcount))
hopcount_by_node = sorted(hopcount_by_node,key=lambda x: x[1])

y3 = []
for f in x:
  f_nodes = math.floor(f*num_nodes)
  inf_nodes = [n for (n,val) in influence_by_node[0:f_nodes]]
  hop_nodes = [n for (n,val) in hopcount_by_node[0:f_nodes]]
  hop_intersect = set(inf_nodes).intersection(set(hop_nodes))
  y3.append(len(hop_intersect)/f_nodes)

connections_by_node = []
for i in nodes:
  conns = [l for l in data if l[0] == i or l[1] == i]
  connections_by_node.append((i,len(conns)))
connections_by_node = sorted(connections_by_node,key=lambda x: x[1],reverse=True)

y4 = []
for f in x:
  f_nodes = math.floor(f*num_nodes)
  inf_nodes = [n for (n,val) in influence_by_node[0:f_nodes]]
  conn_nodes = [n for (n,val) in connections_by_node[0:f_nodes]]
  conn_intersect = set(inf_nodes).intersection(set(conn_nodes))
  y4.append(len(conn_intersect)/f_nodes)

fig = plt.figure(2)
plt.plot(x,y1,color='r') # Degrees # This is higher so degrees are better?
plt.plot(x,y2,color='b') # Clustering coefficient
plt.plot(x,y3,color='g') # Hop counts
plt.plot(x,y4,color='m') # Temporal links ????
plt.xlabel('Fraction f')
plt.ylabel('Recognition rate')
plt.legend(['Degrees', 'Clustering coefficient', 'Hop counts', 'Number of temporal links'])
plt.show()
# 13
T = 57791
thresh = 0.8
num_nodes = len(nodes)
num_links = len(links)
infections = set()
inf_times_by_node = []
for node in nodes:
  infections = set([node])
  infection_times = [(node,0)]
  t = 1
  tmp_infections = set()
  for row in data:
    if row[2] != t:
      if len(infections)/num_nodes >= thresh:
        break
      infections = infections.union(tmp_infections)
      tmp_infections = set()
      t = row[2]
    if row[0] in infections:
      tmp_infections.add(row[1])
      if row[1] not in [a[0] for a in infection_times]:
        infection_times.append((row[1],t))
    if row[1] in infections:
      tmp_infections.add(row[0])
      if row[0] not in [a[0] for a in infection_times]:
        infection_times.append((row[0],t))
  avg = np.mean([a[1] for a in infection_times])
  inf_times_by_node.append((node,avg))
inf_times_by_node = sorted(inf_times_by_node,key=lambda x: x[1])

y5 = []
y6 = []
y7 = []
for f in x:
  f_nodes = math.floor(f*num_nodes)
  inf_time_nodes = [n for (n,val) in inf_times_by_node[0:f_nodes]]
  inf_nodes = [n for (n,val) in influence_by_node[0:f_nodes]]
  deg_nodes = [n for (n,val) in degree_by_node[0:f_nodes]]
  clust_nodes = [n for (n,val) in clust_coeff_by_node[0:f_nodes]]
  inf_intersect = set(inf_time_nodes).intersection(set(inf_nodes))
  deg_intersect = set(inf_time_nodes).intersection(set(deg_nodes))
  clust_intersect = set(inf_time_nodes).intersection(set(clust_nodes))
  y5.append(len(inf_intersect)/f_nodes)
  y6.append(len(deg_intersect)/f_nodes)
  y7.append(len(clust_intersect)/f_nodes)

fig = plt.figure(3)
plt.plot(x,y5,color='r') # R by R' # BEST!
plt.plot(x,y6,color='b') # Deg by R'
plt.plot(x,y7,color='g') # Cluslt by R'
plt.xlabel('Fraction f')
plt.ylabel('Recognition rate')
plt.legend(['Influence R', 'Degrees', 'Clustering coefficient'])
plt.show()

#14

timestamps = [conn[2] for conn in data]
random.shuffle(timestamps)
g2 = []
for i,conn in enumerate(data):
  g2.append((conn[0],conn[1],timestamps[i]))
g3 = []
links_list = list(links)
for i in [conn[2] for conn in data]:
  rand_link = random.choice(links_list)
  g3.append((rand_link[0],rand_link[1],i))
#15