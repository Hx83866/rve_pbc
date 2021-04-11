# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: read_hierarchical.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-26 21:18:58
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-04-05 22:53:59
# @Description: Read .stcell file and parse hierarchical info of RVE

import json

class HierarchicalRead():
    """
        A class for read .stcell file generated from Neper,
        which contains hierarchical information of RVE. And
        save information in json file.
    """

    #NOTE: call this class and create example in  file_scanner.py
    def __init__(self, stcell_file_path):
        """ Initialize the parameters """
        
        # pass arguments to parameters
        self.stcell_file = stcell_file_path
        # container
        self.hierarchical_dict = {}

    def read_hierarch(self):
        """ Parse .stcell file, and extract hierarchical information as a dictionary """
        
        # open .stcell file
        try:
            with open(self.stcell_file, 'r') as stcell_file:
                # previous parameters
                pre_pag_ind = None
                pre_pck_ind = None
                pre_bnt_ind = None
                # loop over lines
                for line in stcell_file:
                    line = line.rstrip()
                    line_list = line.split()
                    # if empty line
                    if len(line_list) == 0:
                        continue
                    # otherwise
                    else:
                        # current parameters
                        crt_pag_ind = line_list[0]
                        crt_pck_ind = line_list[1]
                        crt_bnt_ind = line_list[2]

                        # if new pag
                        if crt_pag_ind != pre_pag_ind:
                            # create empty list
                            self.hierarchical_dict["PAG_"+str(crt_pag_ind)] = []
                            # if not first run
                            if pre_pck_ind != None:
                                # append max. grain number as element in list to pag
                                self.hierarchical_dict["PAG_"+str(pre_pag_ind)].append(int(pre_bnt_ind))
                            else:
                                pass
                        # otherwise
                        else:
                            if crt_pck_ind != pre_pck_ind:
                                # append max. grain number as element in list to pag
                                self.hierarchical_dict["PAG_"+str(pre_pag_ind)].append(int(pre_bnt_ind))
                            else:
                                pass
                        # pass current to previous
                        pre_pag_ind = crt_pag_ind
                        pre_pck_ind = crt_pck_ind
                        pre_bnt_ind = crt_bnt_ind
                # add the last line information to hierarch dict
                self.hierarchical_dict["PAG_"+str(pre_pag_ind)].append(int(pre_bnt_ind))
        # if Error
        except FileExistsError or FileNotFoundError:
            print("\n\nError! No .Stcell File was Found! Please Check Input Path Again!\n")

        # return dict
        return self.hierarchical_dict

if __name__ == "__main__":
    file_path = "/mnt/d/User_Hu_Xiang/Neper/Trial/gene/voronoi/2.5D/sheet_05/sheet_05.stcell"
    stcell = HierarchicalRead(stcell_file_path=file_path)
    dict = stcell.read_hierarch()
    output_path = "/mnt/d/User_Hu_Xiang/Neper/Trial/gene/voronoi/2.5D/sheet_05/trial.json"
    with open(output_path, 'w') as output:
        json.dump(dict, output, sort_keys=True, indent=4)