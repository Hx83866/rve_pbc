# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: main.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-17 08:29:24
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-04-07 16:32:20
# @Description: get input directory path in main program.

import os
import time
from file_scanner import FileScanner

def bool_convert(input_char):
    """ convert character into boolean variable """

    try:
        if str(input_char) == 'y' or str(input_char) == 'Y':
            return True
        elif str(input_char) == 'n' or str(input_char) == 'N':
            return False
    except TypeError:
        return None

def standard_run():
    """ run standard process """

    while True:
        # read rve input directory
        dir_path_str = input(
            "\nPlease input the complete folder path where the raw data are saved in, Enter 'q' to quit:\n"
        )
        
        if dir_path_str == 'q':
            break
        elif dir_path_str == '':
            print("\nError! No Valid Input! Try Again!\n")
            continue
        else:
            only_graindata_or_not = input(
                "\nOnly graindata.inp is required?[Y/n]:\n"
            )
            pbc_or_not = input(
                "\nPeriodical boundary conditions are required?[Y/n]:\n"
            )
            only_gr_signal = bool_convert(only_graindata_or_not)
            pbc_signal = bool_convert(pbc_or_not)
            # if answer in correct type
            if type(only_gr_signal) == bool and type(pbc_signal)== bool:
                # start time
                start_time = time.time()
                # avoid slash problem
                dir_path = dir_path_str.replace('\\', '/')
                # run file scanning
                rve_inp_gen = FileScanner(\
                    dir_path, only_graindata=only_gr_signal, pbc=pbc_signal)
                # end time
                end_time = time.time()
                print("\nTotal Run Time: \t {} Seconds.\n".format(float(end_time - start_time)), end='\n')
            else:
                continue

if __name__ == "__main__":
    # call standard run
    standard_run()