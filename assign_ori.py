# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: assign_ori.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-29 09:51:52
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-04-05 21:50:18
# @Description: Assign orientation read from MTEX to RVE cell.

import json
import secrets

class AssignOriToRve():
    """
        A class for assigning orientation extracted from MTEX
        to RVE cell refering to hierarchical information of 
        the RVE.
    """

    def __init__(self, ori_json_path, hierarch_dict):
        """ initialize the properties """

        # pass arguments to parameters
        self.ori_json_path = ori_json_path
        self.hierarch_dict = hierarch_dict
        # initialize a empty dictionary
        self.mat_ori_dict = None
        self.assigned_ori_dict = {}
        # auto run
        self.__load_ori_json()
        # match list
        (self.match_relationship, self.mat_hierarch_dict) \
             = self.__matching_hierarch_find()
        # assign
        self.__assign_ori()

    def __load_ori_json(self):
        """ load .json file where material orientation was stored in """

        try:
            with open(self.ori_json_path) as mat_ori_json:
                self.mat_ori_dict = json.loads(mat_ori_json.read())
        except FileExistsError or FileNotFoundError:
            print("\n\nError! No Material Orientation Json File was Found! Please Check Input Path Again!\n")

    def __matching_hierarch_find(self):
        """ find best matching relationship between PAG in RVE and the one in material bank """

        # find first layer (PAG) with same package numbers
        available_pag_list = self.__mat_json_layer_match()
        # export hierarchical info of each PAG in available list
        mat_hierarch_dict = self.__mat_pag_hierarch_export(available_pag_list)
        # match dict
        match_dict = {}
        # loop over each PAG in RVE and find which PAG in material bank is best matched
        for rve_pag, pck_list in self.hierarch_dict.items():
            sorted_pck_list = sorted(pck_list, reverse=True)
            crt_match_list = self.__match_list(sorted_pck_list, mat_hierarch_dict)
            # create a key, value couple for current rve PAG
            # where key is RVE PAG name and value is matching list
            match_dict[str(rve_pag)] = {"match_list": crt_match_list, "priority": sum(sorted_pck_list)}
        # sorted match dict by priority 
        priority_sorted_pag_name_ls = sorted(match_dict, key=lambda pag_name:(match_dict[pag_name]["priority"]), reverse=True)
        # select best match PAG in material bank in sequence of priority
        # and stored by tuple list
        final_match_list = []
        for ind in range(len(priority_sorted_pag_name_ls)):
            crt_pag_name = str(priority_sorted_pag_name_ls[ind])
            # select candidate tuple from match list 
            for candidate_tuple in match_dict[crt_pag_name]["match_list"]:
                # if tuple is already selected by PAG with higher priority
                if self.__selected_state_judge(final_match_list, candidate_tuple):
                    continue
                else:
                    crt_match_tpl = (crt_pag_name, candidate_tuple)
                    break
            # append to final match list
            final_match_list.append(crt_match_tpl)
        
        # return final matched list
        return (final_match_list, mat_hierarch_dict)

    def __selected_state_judge(self, match_list, current_candidate_tuple):
        """ tell whether current candidate tuple is already in match list """

        # extract tuple from match list
        try:
            slctd_pag_list = [match_tuple[1][0] for match_tuple in match_list]
            if current_candidate_tuple[0] in slctd_pag_list:
                return True
            else:
                return False
        except KeyError:
            pass

    def __assign_ori(self):
        """ given final match relationship, assign orientation to RVE grains """

        # modify the RVE hierarchical dictionary for further operation
        mdf_rve_hierarch_dict = self.__rve_hierarch_modify(self.hierarch_dict)
        # loop over relationship list to assign orientation
        for relation_tuple in self.match_relationship:
            rve_pag = relation_tuple[0]
            mat_pag = relation_tuple[1][0]
            # loop over all package tuples in current RVE
            for index in range(len(mdf_rve_hierarch_dict[str(rve_pag)])):
                # local variables
                # current RVE package tuple
                crt_pck_tpl = mdf_rve_hierarch_dict[str(rve_pag)][index]
                crt_pck_grs_num = crt_pck_tpl[1]
                crt_pck_beg_ind = crt_pck_tpl[2]
                # current package tuple in material bank
                crt_mat_pck_tpl = self.mat_hierarch_dict[str(mat_pag)][index]
                crt_mat_pck_name = crt_mat_pck_tpl[0]

                # 
                # if grain number in current RVE package is large than it in corresponding package material
                if crt_pck_tpl[1] > crt_mat_pck_tpl[1]:
                    # extending grain number in current package from material bank
                    mat_ori_list = \
                        self.__extend_mat_pck_dict(mat_pag, crt_mat_pck_name, goal_grain_num=\
                            crt_pck_tpl[1])
                # otherwise
                else:
                    mat_ori_list = self.mat_ori_dict[mat_pag][crt_mat_pck_name]
                # assign orientation to grain in current package
                for lc_gr_ind in range(crt_pck_grs_num):
                    # global grain index
                    grain_key =  str(lc_gr_ind + crt_pck_beg_ind)
                    # to assigned orientation
                    ori = mat_ori_list[lc_gr_ind]
                    # append to final dictionary
                    self.assigned_ori_dict[grain_key] = ori


    def __extend_mat_pck_dict(self, material_pag_name, material_pck_name, goal_grain_num):
        """ 
            given material PAG name as well as one of its material package name,
            return a extended orientation list where elements are extended 
            orientation of grains.
        """

        # extract original orientation list
        original_ori_list = self.mat_ori_dict[material_pag_name][material_pck_name]
        # random select orientation and append it to original orientation list
        while len(original_ori_list) < goal_grain_num:
            random_selected_ori = secrets.choice(original_ori_list)
            original_ori_list.append(random_selected_ori)

        return original_ori_list

    def __rve_hierarch_modify(self, rve_hierarchical_dictionary):
        """ 
            given original hierarchical dictionary of RVE,
            modify it for the following assigning operation.
        """

        # create a empty dict as a local variable
        modified_dict = {}
        # loop over given original hierarchical dict
        # grain number of previous PAG
        pre_pag_grs_num = 0
        for rve_pag, pck_list in rve_hierarchical_dictionary.items():
            # create a list as local variable to contain packages info in each PAG
            pck_info_list = []
            # total grains number of previous packages
            pre_pck_grs_num = 1
            # loop over package list
            for i in range(len(pck_list)):
                # current information
                crt_pck_ind = "pck" + str(i)
                # current grain number in package
                crt_pck_grs_num = pck_list[i]
                # the first grain's global index in current package
                crt_pck_beg_ind = pre_pag_grs_num + pre_pck_grs_num
                
                # a tuple for current package's parsed information
                pck_tuple = (crt_pck_ind, crt_pck_grs_num, crt_pck_beg_ind)
                # append current package info tuple to package info list
                pck_info_list.append(pck_tuple)
                # update local variables
                pre_pck_grs_num = pre_pck_grs_num + crt_pck_grs_num
            # sort pck_info_list by grain number in package
            pck_info_list = \
                sorted(pck_info_list, key=lambda tuple:(tuple[1]), reverse=True)
            # append package info list to current PAG
            modified_dict[rve_pag] = pck_info_list
            # update local variable -- grain number of previous PAG
            pre_pag_grs_num = pre_pag_grs_num + sum(pck_list)
        
        #return modified dictionary
        return modified_dict

    def __match_list(self, rve_pck_list, mat_hierarch_dict):
        """ 
            get package list of a RVE PAG and loop over material hierarchical dictionary,
            return a sorted match list where the first element is the best matched PAG in
            material bank whereas the last one is the worse matched PAG.
        """

        # a local container for storing match results
        match_list = []
        for pag_name, hierarch_list in mat_hierarch_dict.items():
            # calculate match degree between current PAG and given RVE PAG
            match_degree = self.__match_degree_calc(rve_pck_list, hierarch_list)
            calc_result_tpl = (str(pag_name), match_degree)
            match_list.append(calc_result_tpl)
        
        #sorted by match degree
        match_list = sorted(match_list, key=lambda tuple:(tuple[1]), reverse=True)
        return match_list

    def __match_degree_calc(self, rve_pck_list, mat_pck_list):
        """ calculate the match degree between given PAG and given RVE PAG """

        match_degree = 0
        # loop over all elements in RVE package list
        for i in range(len(rve_pck_list)):
            crt_rve_pck_grains_num = rve_pck_list[i]
            crt_mat_pck_grains_num = mat_pck_list[i][1]
            crt_degree = crt_mat_pck_grains_num - crt_rve_pck_grains_num
            match_degree = match_degree + crt_degree
        
        return match_degree

    def __mat_pag_hierarch_export(self, available_pag_list):
        """ return a hierarchical dictionary of available PAG """

        mat_hierarch_pag_dict = {}
        for info_tuple in available_pag_list:
            # current pag name
            crt_pag_name = info_tuple[0]
            # container to store hierarchical information
            pck_list =[]
            # loop all packages
            for pck_name, ori_list in self.mat_ori_dict[crt_pag_name].items():
                # tuple for package name and its length
                pck_tuple = (str(pck_name), int(len(ori_list)))
                pck_list.append(pck_tuple)
            # sort list
            pck_list = sorted(pck_list, key=lambda tuple:(tuple[1]), reverse=True)
            # add key,value couple to mat hierarchical dictionary
            mat_hierarch_pag_dict[crt_pag_name] = list(pck_list)

        return mat_hierarch_pag_dict

    def __mat_json_layer_match(self):
        """ return sorted PAG information whose values(packages number) that match package numbers in RVE """

        max_pck_number = self.__max_rve_pck_number()
        ava_list = []
        if max_pck_number == 0:
            print("\nError! No Package Numbers has been Read! Please Check .Stcell File Again.\n")
        else:
            for pag, pck_dict in self.mat_ori_dict.items():
                if len(pck_dict.keys()) < max_pck_number:
                    continue
                else:
                    # how many grains are included in PAG
                    grain_num = 0
                    for pck_name, grains_list in pck_dict.items():
                        grain_num = grain_num + len(grains_list)
                    # append info to tuple
                    info_tuple = (str(pag), len(pck_dict.keys()), grain_num)
                    ava_list.append(info_tuple)
        # sort by package number and grain number
        sorted_list = sorted(ava_list, key=lambda tuple:(tuple[1], tuple[2]), reverse=True)
        
        return sorted_list

    def __max_rve_pck_number(self):
        """ return maximal packages number in RVE's PAG """

        max_number = 0
        for key, item in self.hierarch_dict.items():
            if max_number < len(item):
                max_number = len(item)
            else:
                continue

        return max_number

if __name__ == "__main__":
    # load json file
    ori_json_path = "matbank/Bainite_1300.json"
    # hierarchical dict
    hierarch_dict_path = "trial.json"
    hierarch_dict = None
    with open(hierarch_dict_path) as hierarch_file:
        hierarch_dict = json.loads(hierarch_file.read())
    # trial
    trial = AssignOriToRve(ori_json_path=ori_json_path, hierarch_dict=hierarch_dict)