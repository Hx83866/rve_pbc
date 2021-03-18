# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: file_scanner.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-02-06 10:07:44
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-03-16 19:40:57
# @Description: Parse tess file and stelset file, generate input files.

import os
from grains_parse import GrainsParse
from nodes_parse import NodesParse

class FileScanner():
    """
        Given path of directory, read files in directory;
        Generate input files, including graindata.inp,
        materials.inp, sections.inp, and periodic input files.
    """

    def __init__(self, dir_path):
        """ initialize the properties"""

        # get input arguments
        self.dir_path = dir_path
        # container
        # grains containers
        self.ori_dict = {}
        self.dia_dict = {}
        # nodes containers
        self.face_nodes = {}
        self.edge_nodes = {}
        self.vertice_nodes = {}
        # file path
        self.tess_file_path = None
        self.stelset_file_path = None
        self.final_inp_file_path = None

        # automatically run
        self.__files_scan()
        self.__run()

    def __run(self):
        """ auto run """

        # run if files found
        if self.tess_file_path != None and self.stelset_file_path != None:
            # GrainsParse 
            grains = GrainsParse(self.tess_file_path, self.stelset_file_path)
            self.ori_dict = grains.read_ori()
            self.dia_dict = grains.read_eqvdiam()
            # NodesParse
            nodes = NodesParse(self.final_inp_file_path)
            self.face_nodes = nodes.faces
            self.edge_nodes = nodes.edges
            self.vertice_nodes = nodes.vertices
            # write input files
            if self.final_inp_file_path != None and self.__write_graindata():
                self.__write_grain_input()
                if (len(self.face_nodes) != 0) and (len(self.edge_nodes) != 0) and (len(self.vertice_nodes) != 0):
                    self.__write_face_input()
                    self.__write_edge_input()
                    self.__write_corners_input()
                    self.__write_vertice_input()
                    self.__write_final_input()
                else:
                    print("\nError! No Node Information Have Been Found!\n")
            else:
                print("\nError! Mesh file cannot be parsed!\n\n")
        else:
            print("\nError! Files not Found!\n\n")

    def __files_scan(self):
        """
            Find .tess file in directory
        """

        os.chdir(self.dir_path)

        with os.scandir(os.getcwd()) as current_files:
            for current_file in current_files:
                if current_file.is_file():
                    # extraction file extensions
                    (file_path, file_name) = os.path.split(current_file)
                    (file_name, extension) = os.path.splitext(file_name)
                    if "sections" in file_name or "materials" in file_name:
                        continue
                    else:
                        if extension == ".tess":
                            self.tess_file_path = current_file
                        elif extension == ".stelset":
                            self.stelset_file_path = current_file
                        elif file_name != "graindata" and extension == ".inp":
                            self.final_inp_file_path = current_file
                        else:
                            continue

    def __write_graindata(self):
        """
            Import orientation dictionary and eqv_diameter dictionary
            Merge them and Export to graindata file
        """

        # grain data file name
        output_file = 'graindata.inp'
        # check if the dimensions of two dictionaries are same
        if len(list(self.ori_dict.keys())) != len(list(self.dia_dict.keys())):
            print("\n\nError! Dictionaries Dimensions do not match!\n")
            return False
        else:
            with open(output_file, 'w') as output_file:
                title = "!MMM Crystal Plasticity Input File\n\n"
                output_file.write(title)
                # loop all grains by index
                for key in self.ori_dict.keys():
                    # modify decimal
                    eqv_diam = "%.3f" % float(self.dia_dict[key])
                    phi_1_f = float(self.ori_dict[key]['phi1']) if float(self.ori_dict[key]['phi1']) > 0 else float(self.ori_dict[key]['phi1'])+360.0 
                    phi_1 = "%.3f" % phi_1_f
                    phi_f = float(self.ori_dict[key]['phi']) if float(self.ori_dict[key]['phi']) > 0 else float(self.ori_dict[key]['phi'])+360.0 
                    phi   = "%.3f" % phi_f
                    phi_2_f = float(self.ori_dict[key]['phi2']) if float(self.ori_dict[key]['phi2']) > 0 else float(self.ori_dict[key]['phi2'])+360.0 
                    phi_2 = "%.3f" % phi_2_f
                    # generate line to write
                    to_write_line = "Grain : %(key)s : %(phi1)s : %(phi)s : %(phi2)s : %(eqv_dia)s\n" % \
                        {"key": key, "phi1":phi_1, "phi":phi, "phi2":phi_2, "eqv_dia":eqv_diam}
                    # write line
                    output_file.write(to_write_line)
            
            return True

    def __write_grain_input(self):
        """
            Import grain number, generat input files
            including sections and material information,
            insert rows into input file that will be imported
            to ABAQUS later.
        """

        (file_path, file_name) = os.path.split(self.final_inp_file_path)
        (file_name, extension) = os.path.splitext(file_name)
        # section file
        global section_file
        section_file = file_name + '_sections.inp'
        # material file
        global material_file
        material_file = file_name + '_materials.inp'

        # Flow curve
        flow_curve = "0.00056313, 	0.000\n0.000723443,	0.01\n0.000836414,	0.02\n0.000916023,	0.03\n0.000972122,	0.04\n0.001011655,	0.05\n0.001039513,	0.06\n0.001059145,	0.07\n0.001072979,	0.08\n0.001082727,	0.09\n0.001089597,	0.1\n"

        with open(section_file,'w') as sec_file:
            with open(material_file, 'w') as mat_file:
                for ind in range(1, 1+len(list(self.dia_dict.keys()))):
                    sec_str = "**Section: Section-%(ind)s\n*Solid Section, elset=poly%(ind)s, material=Grain_Mat%(ind)s\n,\n" % \
                        {"ind": str(ind)}
                    # sec_str = "**Section: Section-%(ind)s\n*Solid Section, elset=poly%(ind)s, material=phase1_%(ind)s\n,\n" % \
                    #     {"ind": str(ind)}
                    mat_str = "*Material, name=Grain_Mat%(ind)s\n*Depvar\n\t176,\n*User Material, constants=2\n%(ind)s.,3.\n" % \
                        {"ind": str(ind)}
                    # mat_str = "*Material, name=phase1_%(ind)s\n*Elastic\n 0.21, 0.3\n*Plastic\n" % {"ind":str(ind)} + flow_curve

                    # append string line
                    sec_file.write(sec_str)
                    mat_file.write(mat_str)

    def pattern_str(self, node_positive, node_negative, v_n_pos, v_n_neg, direction):
        """ Generate pattern string, which should be written in input file """
        
        # initial char to indicate direction
        d_ind = ''
        string = ""
        # which direction
        if direction == 'X':
            d_ind = '1'
        elif direction == 'Y':
            d_ind = '2'
        elif direction == 'Z':
            d_ind = '3'
        # pattern string
        if d_ind != '':
            # string pattern
            string = \
                "*Equation \n4 \n%(n1)s,%(dir)s,1 \n%(n2)s,%(dir)s,-1 \n%(v1)s,%(dir)s,-1 \n%(v2)s,%(dir)s,1 \n" % \
                {"n1": str(node_positive), "n2": str(node_negative), \
                    "v1": str(v_n_neg), "v2": str(v_n_pos), \
                            "dir": d_ind}
        else:
            pass

        return string

    def write_node_face_pbc(self, file_name, face_normal_axis):
        """
            Given axis which face node sets belong to, whose 
            information should be written as part of pattern 
            string in new input file through a loop.
        """

        # determine two vertice nodes by set axis
        # if LeftToRight
        if face_normal_axis == 'X':
            vertice_neg = 'V2'
            vertice_pos = 'V1'
            f_pos_set = 'x1'
            f_neg_set = 'x0'
        # if BottomToTop
        elif face_normal_axis == 'Y':
            vertice_neg = 'V1'
            vertice_pos = 'V4'
            f_pos_set = 'y0'
            f_neg_set = 'y1'
        # if FrontToRear
        elif face_normal_axis == 'Z':
            vertice_neg = 'V1'
            vertice_pos = 'H1'
            f_pos_set = 'z1'
            f_neg_set = 'z0'
        else:
            vertice_neg = ''
            vertice_pos = ''
            f_pos_set = ''
            f_neg_set = ''
        # determine face sets
        # try:
        face_set_p = self.face_nodes[f_pos_set]
        face_set_n = self.face_nodes[f_neg_set]
        vertice_pos = self.vertice_nodes[vertice_pos][0]
        vertice_neg = self.vertice_nodes[vertice_neg][0]
        # write face pbc input file
        with open(file_name, 'w') as input_file:
            for direction in ['X', 'Y', 'Z']:
                if direction == 'X':
                    first_line_str = "**** {}-DIR \n".format(direction)
                else:
                    first_line_str = "**** \n**** {}-DIR \n".format(direction)
                # first line
                input_file.write(first_line_str)
                # loop over set
                for i in range(len(face_set_p)):
                    pattern_string = \
                        self.pattern_str(face_set_p[i], face_set_n[i], \
                            v_n_pos=vertice_pos, v_n_neg=vertice_neg, direction=direction)
                    input_file.write(pattern_string)
        # except:
        #     print("\n\nError! Failed to Write Face Periodic Condition Input File!\n")

    def __write_face_input(self):
        """
            Import face sets, generat periodic input files
        """

        # create face input file name dict
        global f_pbc_file_name
        f_pbc_file_name = {'X': "LeftToRight", 'Y': "BottomToTop", 'Z': "FrontToRear"}
        # loop over
        for (normal_axis, file_name) in f_pbc_file_name.items():
            file_name = file_name + '.inp'
            self.write_node_face_pbc(file_name, face_normal_axis=normal_axis)

    def write_node_edge_pbc(self, file_name, edge_pbc_dict):
        """
            Given edge periodic boundary conditions dictionary, in 
            which periodic relationship was stored, and the infomation
            will be part of pattern string that will be written in a
            given input file.
        """

        file_name = file_name + '.inp'
        with open(file_name, 'w') as input_file:
            for (plane, edge_tuple_list) in edge_pbc_dict.items():
                for edge_tuple in edge_tuple_list:
                    # extract information from tuple
                    edge_set_p = self.edge_nodes[edge_tuple[0]]
                    edge_set_n = self.edge_nodes[edge_tuple[1]]
                    vertice_neg = self.vertice_nodes[edge_tuple[2]][0]
                    vertice_pos = self.vertice_nodes['V1'][0]
                    # loop over three basic direction
                    for direction in ['X', 'Y', 'Z']:
                        first_line_str = "**** {}-DIR \n".format(direction)
                        # first line
                        input_file.write(first_line_str)
                        # loop over set
                        for i in range(len(edge_set_p)):
                            pattern_str = \
                                self.pattern_str(edge_set_p[i], edge_set_n[i], \
                                    v_n_pos=vertice_pos, v_n_neg=vertice_neg, direction=direction)
                            input_file.write(pattern_str)

    def __write_edge_input(self):
        """
            Import edge sets, generat periodic input files
        """

        # store periodic condition in a dict
        # key = plane, such as X-Y plane where the edges belong to
        # value = edge tuple list 
        edge_pbc_dict = {'X-Y': [('x1-y1', 'x0-y1', 'V2'), ('x1-y0', 'x0-y0', 'V2'), ('x0-y1', 'x0-y0', 'V4')], \
            'Y-Z': [('y1-z0', 'y1-z1', 'H1'), ('y0-z0', 'y0-z1', 'H1'), ('y1-z1', 'y0-z1', 'V4')], \
                'Z-X': [('x1-z0', 'x0-z0', 'V2'), ('x1-z1', 'x0-z1', 'V2'), ('x0-z0', 'x0-z1', 'H1')]}
        # edge input file
        global edge_inp_file_name
        edge_inp_file_name = "Edges"
        # run
        self.write_node_edge_pbc(edge_inp_file_name, edge_pbc_dict)

    def write_node_vertice_pbc(self, file_name, corners_pbc_dict):
        """
            Given vertice periodic boundary conditions dictionary, in 
            which periodic relationship was stored, and the infomation
            will be part of pattern string that will be written in a
            given input file.
        """

        file_name = file_name + '.inp'
        with open(file_name, 'w') as input_file:
            for (v_couple_name, vertice_tuple) in corners_pbc_dict.items():
                # extract information from tuple
                vertice_1_p = self.vertice_nodes[vertice_tuple[0]][0]
                vertice_1_n = self.vertice_nodes[vertice_tuple[1]][0]
                vertice_2_p = self.vertice_nodes['V1'][0]
                vertice_2_n = self.vertice_nodes[vertice_tuple[2]][0]
                # loop directions
                for direction in ['X', 'Y', 'Z']:
                    first_line_str = "**** {}-DIR \n".format(direction)
                    # first line 
                    input_file.write(first_line_str)
                    # vertices couple
                    pattern_str = \
                        self.pattern_str(vertice_1_p, vertice_1_n, \
                            vertice_2_p, vertice_2_n, \
                                direction=direction)
                    input_file.write(pattern_str)

    def __write_corners_input(self):
        """
            Import vertices sets, generate periodic input file
        """

        corners_pbc_dict = {"V3toV4": ('V3', 'V4', 'V2'), \
            "H4toV4": ('H4', 'V4', 'H1'), "H3toV3": ('H3', 'V3', 'H1'), \
                "H2toV2": ('H2', 'V2', 'H1')}
        # corners input file
        global corners_input_file_name
        corners_input_file_name = "Corners"
        # run
        self.write_node_vertice_pbc(corners_input_file_name, corners_pbc_dict)

    def __write_vertice_input(self):
        """ Import vertices dictionary, generate set input file """

        # vertices input file
        global vertices_input_file_name
        vertices_input_file_name = "VerticeSets"
        instance_name = "TESS-1"
        with open(vertices_input_file_name+'.inp', 'w') as input_file:
            for (vertice_name, vertice_node) in self.vertice_nodes.items():
                v_name = str(vertice_name)
                v_node = str(vertice_node[0]) 
                pattern_str = "*Nset, nset=%(v_name)s, instance=%(ins)s \n%(v_node)s\n" % \
                    {"v_name": v_name, "ins": instance_name, "v_node": v_node}
                input_file.write(pattern_str)

    def __write_final_input(self):
        """
            Write include input files lines into final input file,
            which will be imported to ABAQUS later.
        """

        #TODO: separate this following part as a single method
        with open(self.final_inp_file_path, 'r') as mesh_file:
            lines = mesh_file.read().splitlines()

        # call final method 
        self.write_input_include(lines)

    def __heading_section(self):
        """
            Insert heading lines in final input file
        """
        
        heading_string = \
            "*Heading\n** Job name: Job-1 Model name: multi_scale_rve\n" +\
                "** Generated by: Abaqus/CAE 2017\n" +\
                    "*Preprint, echo=NO, model=NO, history=NO, contact=NO\n" +\
                        "**\n** PARTS\n**\n"
        
        return heading_string

    def write_input_include(self, init_lines):
        """ 
            Including input files generated before, as well as 
            assembly and boundary conditions section in final 
            input file
        """

        # include sec file and mat file in final input file
        tail_str_0 = "\n*Include, Input = {}\n".format(str(section_file)) +\
            "*Include, Input = {}\n".format(str(f_pbc_file_name['X'])+".inp") +\
                "*Include, Input = {}\n".format(str(f_pbc_file_name['Y'])+".inp") +\
                    "*Include, Input = {}\n".format(str(f_pbc_file_name['Z'])+".inp") +\
                        "*Include, Input = {}\n".format(str(edge_inp_file_name)+".inp") +\
                            "*Include, Input = {}\n".format(str(corners_input_file_name)+".inp") +\
                                "*End Part\n*End Part\n"

        with open(self.final_inp_file_path, 'w') as mesh_file:
            # write heading
            mesh_file.write(str(self.__heading_section()))
            # loop over original lines
            for line in init_lines:
                if line.strip('\n') != "*End Part":
                    mesh_file.write(line+'\n')
            # append tail string
            # including input files
            mesh_file.write(tail_str_0)
            # write assembly section
            mesh_file.write(str(self.__assembly_section()))
            # write material section
            mesh_file.write(str(self.__material_section()))
            # write boundary conditions sections
            mesh_file.write(str(self.__bc_section()))
            # write step section
            mesh_file.write(str(self.__step_section()))
            # write output section
            mesh_file.write(str(self.__output_section()))


    def __assembly_section(self):
        """ Generate assembly part as a whole section in final input file """

        assembly_section = \
            "**\n**\n** ASSEMBLY\n**\n*Assembly, name=Assembly\n**\n*Instance, name=TESS-1, part=TESS\n*End Instance\n" +\
                 "**\n*Include, input={}\n".format(str(vertices_input_file_name)+".inp") +\
                     "*End Assembly\n"
        # return string
        return assembly_section

    def __material_section(self):
        """ Generate material part as a whole section in final input file """

        material_section = \
            "**\n**Materials\n" + \
                "*Include, input={}\n".format(str(material_file))
        
        return material_section

    def __bc_section(self):
        """ Generate boundary conditions as a whole section in final input file """

        bc_section = \
            "**\n**BOUNDARY CONDITIONS\n**\n" +\
                "** Name: H1 Type: Displacement/Rotation\n*Boundary \nH1, 1, 1 \nH1, 2, 2 \n" +\
                    "** Name: V1 Type: Displacement/Rotation\n*Boundary \nV1, 1, 1 \nV1, 2, 2 \nV1, 3, 3 \n" +\
                        "** Name: V2 Type: Displacement/Rotation\n*Boundary \nV2, 2, 2 \nV2, 3, 3 \n" +\
                            "** Name: V4 Type: Displacement/Rotation\n*Boundary \nV4, 1, 1 \nV4, 3, 3 \n"
        
        return bc_section

    def __step_section(self):
        """
            Generate step, as well as boundary condition, 
            as a whole section in final input file.
        """

        step_section = \
            "** ----------------------------------------------------------------\n" +\
                "**\n** STEP: Step-1\n**\n*Step, name=Step-1, nlgeom=YES, inc=10000000\n" +\
                    "*Static\n0.0002, 4., 1e-20, 0.05\n" +\
                        "**\n** BOUNDARY CONDITIONS\n** \n** Name: Load Type: Displacement/Rotation \n" +\
                            "*Boundary\nV2, 1, 1, 5.\n"
        return step_section

    def __output_section(self):
        """ Generate putput section as a whole section in final input file. """

        output_section = \
            "**\n** OUTPUT REQUESTS\n** \n*Restart, write, frequency=0\n" +\
                "** \n** FIELD OUTPUT: F-Output-1\n** \n" +\
                    "*Output, field\n*Node Output\nRF, U\n" +\
                        "*Element Output, direction=YES\nLE, MISES, PE, PEEQ, S, SDV78, SDV79\n" +\
                            "** \n** HISTORY OUTPUT: H-Output-1\n** \n*Output, history, variable=PRESELECT\n" +\
                                "*End Step\n"
        return output_section

if __name__== "__main__":

    dir_path = "/mnt/d/Git/rve_pbc/multi_scale_04"
    Trial =  FileScanner(dir_path)