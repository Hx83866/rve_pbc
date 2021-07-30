# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: grains_parse.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-02-06 10:07:44
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-03-28 17:15:05
# @Description: Parse tess file and stelset file, generate input files.

import os

class GrainsParse():
    """
        Given path of .tess file and .stelset file,
        extract textile and equivalent diameter info
    """

    def __init__(self, tess_file_path, stelset_file_path):
        """ initialize the properties"""

        # get input arguments
        self.tess_file_path = tess_file_path
        self.stelset_file_path = stelset_file_path
        # containers
        self.ori_dict = {}
        self.dia_dict = {}

    def read_ori(self):
        """
            Parse tess file, and extract euler orientation info as dictionary
        """

        # match strings
        match_str = "euler-bunge"
        stop_str = "**"
        # read begin and stop signals
        rd_beg = False
        rd_stp = False
        # open input tess file
        try:
            with open(self.tess_file_path, 'r') as tess_file:
                # grain index
                grain_ind = 1
                # begin loop lines in tess file
                for line in tess_file:
                    line = line.rstrip()
                    # stop loop signal
                    if rd_stp:
                        break
                    # continue loop
                    else:
                        # read line
                        if rd_beg:
                            if stop_str in line:
                                rd_stp = True
                                continue
                            else:
                                # read current euler angles when signal true
                                grain_key = str(grain_ind)
                                angles_list = line.split()
                                self.ori_dict[grain_key] = {"phi1":angles_list[0], "phi":angles_list[1], "phi2": angles_list[2]}
                                # update index
                                grain_ind = grain_ind + 1

                        # match string is found, begin parse and extract
                        elif match_str in line:
                            rd_beg = True
                            continue
                        else:
                            continue
        except (FileNotFoundError, FileExistsError):
            print("\n\nError! No File was Found! Please Check Input Path Again!\n")

        return self.ori_dict

    def read_eqvdiam(self):
        """
            Extract Equivalent Diameter from stelset file as dictionary
        """

        try:
            with open(self.stelset_file_path, 'r') as self.stelset_file:
                grain_index = 1
                for line in self.stelset_file:
                    line = line.rstrip()
                    self.dia_dict[str(grain_index)] = line
                    grain_index = grain_index + 1
        except (FileExistsError, FileNotFoundError):
            print("\n\nError! No File was Found! Please Check Input Path Again!\n")
        
        return self.dia_dict

if __name__== "__main__":

    dir_path = "/mnt/d/User_Hu_Xiang/Neper/Trial/cae/python_files/multi_scale_01"
    Trial =  InputFileGen(dir_path)