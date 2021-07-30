# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: avrg_pck_num.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-04-28 09:35:50
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-04-28 09:56:20
# @Description: Export average package number of PAG from material bank json.

import json
import os

def load_json(json_path):
    """ load .json file and export it as dictionary """

    # create a empty dictionary
    ori_dict = {}
    # open json
    try:
        with open(json_path) as ori_json:
            ori_dict = json.loads(ori_json.read())
    except FileExistsError or FileNotFoundError:
        print("\n\nError! No Material Orientation Json File was Found! Please Check Input Path Again!\n")

    # return dict
    return ori_dict

def calc_mean_pck(ori_dict):
    """ given orientation dictionary and calculate average package number in all PAG """

    # sum
    sum = 0
    # PAG number
    pag_num = len(ori_dict.keys())
    # loop over
    for pag_name, pag_dict in ori_dict.items():
        # current package number
        pck_num = len(pag_dict.keys())
        # sum up
        sum = sum + pck_num
    # calculate mean package number
    try:
        avrg_pck_num = float(sum / pag_num)
        return avrg_pck_num
    except ZeroDivisionError:
        print("\nError! Failed to calculate average package number: **Zero Division**\n")
        return 0

if __name__ == "__main__":
    # material bank path
    json_path = "matbank/Bainite_1300.json"
    # material name
    (file_path, file_name) = os.path.split(json_path)
    (mat_name, extension) = os.path.splitext(file_name)
    # ori dict
    ori_dict = load_json(json_path=json_path)
    # calculation
    mean_pck = calc_mean_pck(ori_dict=ori_dict)
    # print
    print("\nAverage Package Number of material {} is: {}".format(mat_name, str(mean_pck)))

