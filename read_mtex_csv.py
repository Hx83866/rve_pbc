# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: read_mtex_csv.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-25 10:47:46
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-03-29 11:38:22
# @Description: Read csv file exported from MTEX and save hierarchical information as json file.

import os
import csv
import json

class CreateHierarchOriJson():
    """
        A class for reading csv file exported from MTEX,
        which contains hierarchical information, as well as
        orientation information. And save information in a 
        json file.
    """

    def __init__(self, csv_file_path, mat_name):
        """ Initialize the parameters """

        # pass arguments to parameters
        self.csv_file_path = csv_file_path
        self.mat_name = mat_name
        # initialize a empty dictionary 
        self.info_dict = {}
        # initialize a empty list to store lines
        self.lines = []
        # initialize file path and file name
        self.dir_path = None
        self.csv_file = None

        # auto run
        if self.check():
            self.__write_dict()
            self.__pop_items()
            self.__save_json()
        else:
            print("\n\nError! Failed to Read CSV-Format file! Please Check File Again!\n")

    def check(self):
        """ Check if file path is valid and file is openable. """

        # split path and file name
        (self.dir_path, self.csv_file) = os.path.split(self.csv_file_path)
        
        # try open
        try:
            # change working directory
            os.chdir(self.dir_path)
            # if file is a csv file
            (file_name, extension) = os.path.splitext(self.csv_file)
            if extension == ".csv":
                with open(self.csv_file, 'r') as csv_file:
                    # begin loop lines
                    for line in csv_file:
                        # append to lines list
                        self.lines.append(line.rsplit())
            # if more than one line was read
            if len(self.lines) > 1:
                return True
            else:
                return False
        except FileNotFoundError or FileExistsError:
            return False

    def __write_dict(self):
        """ write information stored in list into dictionary """

        for line in self.lines:
            # split line
            info_list = line[0].split(',')
            # info
            grain_ind = info_list[0]
            crt_pag_id = "PAG_" + str(info_list[1])
            crt_pck_id = "PCK_" + str(info_list[2])
            phi_1 = float(info_list[3])
            Phi = float(info_list[4])
            phi_2 = float(info_list[5])
            # create a empty dict to store orientation info of single grain
            grain_ori_dict = {"phi1": phi_1, "phi": Phi, "phi2": phi_2}
            # if PAG index already in info dict
            if crt_pag_id in self.info_dict:
                #if PCK index already in PAG dict
                if crt_pck_id in self.info_dict[crt_pag_id]:
                    # pass
                    pass
                # otherwise
                else:
                    self.info_dict[crt_pag_id][crt_pck_id] = []
                    
            # otherwise
            else:
                # create PAG dict
                self.info_dict[crt_pag_id] = {}
                # create PCK dict
                self.info_dict[crt_pag_id][crt_pck_id] = []

            self.info_dict[crt_pag_id][crt_pck_id].append(grain_ori_dict)

    def __pop_items(self):
        """
            delete the items, which contain only one single PCK dict
            or delete its PCK dict, which contain one single grain
        """

        for pag_name in list(self.info_dict.keys()):
            if len(self.info_dict[pag_name].keys()) <= 1:
                self.info_dict.pop(pag_name)
            else:
                for pck_name in list(self.info_dict[pag_name].keys()):
                    if len(self.info_dict[pag_name][pck_name]) <= 1:
                        self.info_dict[pag_name].pop(pck_name)


    def __save_json(self):
        """ export dictionary as json file """

        filename = str(self.mat_name)
        output_path = os.path.join(self.dir_path, filename)
        with open(output_path, 'w') as output:
            json.dump(self.info_dict, output, sort_keys=True, indent=4)

if __name__ == "__main__":

    csv_file_path = "/mnt/d/Git/rve_pbc/grains_ori.csv"
    test = CreateHierarchOriJson(csv_file_path, "Bainite_1300.json")