# -*- coding: utf-8 -*-
import json
import pandas as pd
from pandas.io.json import json_normalize
import networkx as nx

class DataSet():

    def __init__(self, file_path1, file_path2):

        self.file_path1 = file_path1
        self.file_path2 = file_path2
        self.paper_authorlist_dict = {}
        self.paper_list = []
        self.coauthor_list = []
        self.label_list = []
        self.C_Graph = nx.Graph()
        self.D_Graph = nx.Graph()
        self.num_nnz = 0
        self.author_list = []

    def reader_arnetminer(self):
        paper_index = 0
        coauthor_set = set()

        with open(self.file_path2, 'r') as f:
            json_file2 = json.load(f)
            df2 = json_normalize(json_file2)

        with open(self.file_path1, 'r') as filetoread:
            json_file = json.load(filetoread)
            df1 = json_normalize(json_file)

        print 'read file done.'    

        for key, value in df1.iteritems():
            if key == 'c_c_wang':
                s1 = key.title().replace('_', ' ')
                s2 = ''
                for w in s1.split(' '):
                    if len(w) == 1:
                        w = w + '.'
                        s2 = s2+w
                    else:
                        s2 = s2 + ' '+ w
                # print type(value[0])
                # print value[0][1]
                ego_name = s2.strip()
                for i in value[0].__iter__():
                    for key2, value2 in i.iteritems():
                        if key2 == 'authors':
                            
                            self.author_list = []
                            paper_index += 1
                            self.paper_list.append(paper_index)

                            for j in value2.__iter__():
                                self.author_list.append(j['name'])

                            if len(self.author_list) > 1:
                                if ego_name in self.author_list:
                                    self.author_list.remove(ego_name)
                                    self.paper_authorlist_dict[paper_index] = self.author_list
                                elif '.' in ego_name :
                                    ego_name2 = ego_name.replace('.','.-',1)
                                    if ego_name2 in self.author_list:
                                        self.author_list.remove(ego_name2)
                                        self.paper_authorlist_dict[paper_index] = self.author_list
                                    else:
                                        print 'can not find ego_name2 :', ego_name2
                                        print self.author_list
                                        self.paper_authorlist_dict[paper_index] = self.author_list
                                else:
                                    print 'can not find ego_name :', ego_name1, ego_name2
                                    print self.author_list
                                    self.paper_authorlist_dict[paper_index] = self.author_list

                                for co_author in self.author_list:
                                    coauthor_set.add(co_author)

                                # construct the coauthorship graph
                                for pos in xrange(0, len(self.author_list) - 1):
                                    for inpos in xrange(pos+1, len(self.author_list)):
                                        src_node = self.author_list[pos]
                                        dest_node = self.author_list[inpos]
                                        if not self.C_Graph.has_edge(src_node, dest_node):
                                            self.C_Graph.add_edge(src_node, dest_node, weight = 1)
                                        else:
                                            edge_weight = self.C_Graph[src_node][dest_node]['weight']
                                            edge_weight += 1
                                            self.C_Graph[src_node][dest_node]['weight'] = edge_weight   
                            else:
                                self.paper_authorlist_dict[paper_index] = []

                        if key2 == 'id':
                            for item in df2[key][0].__iter__():
                                for j in item.__iter__():
                                    if j == value2:
                                        # print type(df2[key][0])
                                        # print df2[key][0]
                                        # print j
                                        label = df2[key][0].index(item)
                                        self.label_list.append(label)

        print 'build list done.'
        print 'paper_author: ', self.paper_authorlist_dict
        print 'paper_list：', self.paper_list
        self.coauthor_list = list(coauthor_set)
        """
        compute the 2-extension coauthorship for each paper
        generate doc-doc network
        edge weight is based on 2-coauthorship relation
        edge weight details are in paper definition 3.3
        """
        paper_2hop_dict = {}
        for paper_idx in self.paper_list:
            temp = set()
            if self.paper_authorlist_dict[paper_idx] != []:
                for first_hop in self.paper_authorlist_dict[paper_idx]:
                    temp.add(first_hop)
                    if self.C_Graph.has_node(first_hop):
                        for snd_hop in self.C_Graph.neighbors(first_hop):
                            temp.add(snd_hop)
            paper_2hop_dict[paper_idx] = temp

        for idx1 in xrange(0, len(self.paper_list) - 1):
            for idx2 in xrange(idx1 + 1, len(self.paper_list)):
                temp_set1 = paper_2hop_dict[self.paper_list[idx1]]
                temp_set2 = paper_2hop_dict[self.paper_list[idx2]]

                edge_weight = len(temp_set1.intersection(temp_set2))
                if edge_weight != 0:
                    self.D_Graph.add_edge(self.paper_list[idx1],
                                          self.paper_list[idx2],
                                          weight = edge_weight)
        bipartite_num_edge = 0
        for key, val in self.paper_authorlist_dict.items():
            if val != []:
                bipartite_num_edge += len(val)

        self.num_nnz = self.D_Graph.number_of_edges() + \
                       self.C_Graph.number_of_edges() + \
                       bipartite_num_edge

