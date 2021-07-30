# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: nodes_parse.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-05 10:32:50
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-03-17 19:25:52
# @Description: Parse .inp file and create edges, vertices, and BCs input files.

import os

import numpy as np


class NodesParse():
    """
        Given path of original input file, parse information
        in it, extract nodes information and create edges sets,
        vertices sets, as well as boundary conditions files.
    """

    def __init__(self, init_inp_path):
        """ Initialize the properties"""

        # get input arguments
        #NOTE: get from InputFileGen().final_inp_file_path
        self.init_inp_path = init_inp_path
        # initialize parameters
        self.nodes_dict = {} # store nodes information in a dictionary, in which indices are keys
        # face sets dict
        self.faces = {}
        # edge sets dict
        self.edges = {}
        # vertices dict
        self.vertices = {}
        # auto run
        if self.__file_check():
            self.read_nodes()
            self.read_nsets()
            self.edges_find()
            self.vertices_find()
            self.internodes_remove()
            self.nodes_sort()

    def __file_check(self):
        """ check whether initial input file exits or readable"""

        try:
            with open(self.init_inp_path, 'r') as init_inp:
                return True
        except (FileExistsError, FileNotFoundError):
            print("\n\nError! Input File cannot be opened! Please Check It Again!\n")
            return False

    def read_nodes(self):
        """ parse nodes information and store them in dictionary """

        # match strings
        match_str = "*Node"
        stop_str = "*Element, type="
        # parse begin and stop signals
        parse_beg = False
        parse_stp = False
        # open file and parse
        with open(self.init_inp_path, 'r') as init_inp:
            # begin loop lines
            for line in init_inp:
                line = line.rstrip()
                if parse_stp:
                    break
                else:
                    # parse begin
                    if parse_beg:
                        if stop_str in line:
                            parse_stp = True
                            continue
                        else:
                            line_list = list(line.split(', '))
                            if len(line_list) != 1:
                                self.nodes_dict[str(line_list[0])] = {"x": float(line_list[1]), \
                                    "y": float(line_list[2]), "z": float(line_list[3])}
                    elif match_str in line:
                        parse_beg = True
                        continue
                    else:
                        continue

    def __nset_extract(self, nset_dict, set_name):
        """ given a empty set list and the set name, then extract nodes set as list """ 

        # match strings
        match_str = "*Nset, nset=" + str(set_name)
        # set list
        set_list = []
        # parse begin and stop signals
        parse_beg = False
        parse_stp = False
        # open file and parse
        with open(self.init_inp_path, 'r') as init_inp:
            # begin loop lines
            for line in init_inp:
                line = line.rstrip()
                if parse_stp:
                    break
                else:
                    # parse begin
                    if parse_beg:
                        if len(line) == 0:
                            parse_stp = True
                            continue
                        else:
                            line_list = list(line.split(' '))
                            line_list = [node.replace(',', '') for node in line_list]
                            if len(line_list) != 0 and line_list[0] != '':
                                set_list.extend(line_list)
                    elif match_str in line:
                        parse_beg = True
                        continue
                    else:
                        continue
        
        # store the set list into faces dict
        nset_dict[set_name] = set_list

    def read_nsets(self):
        """ parse nodes sets information and store them in lists """

        faces = self.__3d_cubic_faces()
        for face in faces:
            self.__nset_extract(self.faces, set_name=face)

    def __intersection(self, set_1, set_2):
        """ find the intersection of two set and extract the intersection """

        inter_ls = np.intersect1d(set_1, set_2).tolist()
        return inter_ls

    def __3d_cubic_faces(self):
        """ stack 6 faces name in a list and return the list """
        
        # cubic indices
        cubic_axes = ['x', 'y', 'z']
        pos_neg = ['0', '1']
        # face names list
        f_list = []

        # get all faces names
        for axis in cubic_axes:
            for dir in pos_neg:
                f_list.append(str(axis + dir))
        
        return f_list

    def __3d_cubic_edges(self, cubic_faces):
        """ stack 12 edges names in a list """

        # keys list
        edge_list = []

        # get all edges names
        for face in cubic_faces:
            for ind in range(0, len(cubic_faces)):
                # axes identical
                if str(face)[0] == str(cubic_faces[ind])[0]:
                    continue
                else:
                    f_1 = str(face)
                    f_2 = str(cubic_faces[ind])
                    edge_name = f_1 + '-' + f_2
                    rvs_edge_name = f_2 + '-' + f_1
                    # if edge already in list
                    if ( edge_name in edge_list ) or (rvs_edge_name in edge_list):
                        continue
                    else:
                        edge_list.append(edge_name)

        return edge_list

    def __3d_cubic_vertices(self,cubic_edges):
        """ stack 8 vertices names in a list """

        # vertices list
        vertices_list = []

        # get all vertices names
        for prefix in ['V', 'H']:
            for postfix in range(1, 5):
                vertices_list.append(prefix + str(postfix))
        
        return vertices_list

    def edges_find(self):
        """ find and define edge nodes sets """

        faces = self.__3d_cubic_faces()
        edges = self.__3d_cubic_edges(cubic_faces=faces)
        for edge in edges:
            (f_1, f_2) = edge.split('-')
            self.edges[edge] = self.__intersection(self.faces[f_1], self.faces[f_2])

    def vertices_find(self):
        """ find and define vertices nodes """

        post_num = 5
        pre_char = ''
        # loop over all edges and find vertices
        for z_ind in range(0, 2):
            for x_ind in range(0, 2):
                for y_ind in range(0, 2):
                    # define the postfix number
                    if (x_ind == y_ind):
                        if x_ind == 0:
                            # point 1
                            post_num = 1
                        else:
                            # point 3
                            post_num = 3
                    else:
                        if x_ind == 1 and y_ind == 0:
                            # point 2
                            post_num = 2
                        elif x_ind == 0 and y_ind == 1:
                            # point 4
                            post_num = 4
                    # define the prefix char
                    # H-vertices
                    if z_ind == 0:
                        pre_char = 'H'
                    # V-vertices
                    else:
                        pre_char = 'V'
                    # final vertice name
                    vertice = pre_char + str(post_num)
                    # intersection point find
                    if post_num != 5:
                        self.vertices[vertice] = self.__intersection(self.__intersection(\
                            self.faces['z'+str(z_ind)], self.faces['x'+str(x_ind)]), \
                            self.faces['y'+str(y_ind)])
                    else:
                        break

    def __inter_rm(self, set_1, set_2):
        """ 
            Given set_1 as a subset of set 2, 
            and remove all elements which in set_1 from set_2
        """

        # if set_1 is a subset of set_2
        inter_list = self.__intersection(set_1, set_2)
        
        for item in inter_list:
            # remove item in subset
            set_2.remove(item)
        # return set_2
        return set_2

    def internodes_remove(self):
        """ remove edge nodes from faces, and vertice nodes from edges """

        # remove edge nodes from face nodes
        for (edge_name, edge_set) in self.edges.items():
            for face_name in edge_name.split('-'):
                self.faces[face_name] = self.__inter_rm(edge_set, self.faces[face_name])
        # remove vertice nodes from edge nodes
        for (vertice_name, vertice_node) in self.vertices.items():
            for (edge_name, edge_set) in self.edges.items():
                self.edges[edge_name] = self.__inter_rm(vertice_node, edge_set)

    def __set_sort(self, set):
        """ Given set and sort it by coordinates from nodes dictionary """

        # get nodes information
        node_info = {}
        for node_ind in set:
            node_info[node_ind] = self.nodes_dict[node_ind]
        # sort keys by coordinates
        sorted_set = sorted(node_info, key=lambda node_ind: (node_info[node_ind]['x'],\
            node_info[node_ind]['y'], node_info[node_ind]['z']))

        return sorted_set
    
    def nodes_sort(self):
        """ Sort all the nodes set, including face and edge sets """

        # sort face sets
        for (face_name, f_node_set) in self.faces.items():
            self.faces[face_name] = self.__set_sort(f_node_set)
        # sort edge sets
        for (edge_name, e_node_set) in self.edges.items():
            self.edges[edge_name] = self.__set_sort(e_node_set)

if __name__== "__main__":

    input_path = "/mnt/d/User_Hu_Xiang/Neper/Trial/cae/python_files/multi_scale_01/multi_scale_01.inp"
    Trial =  NodesParse(input_path)
