# Copyright (c) 2021 Xiang Hu
#
# -*- coding:utf-8 -*-
# @Script: main.py
# @Author: Xiang Hu
# @Email: xiang.hu@rwth-aachen.de
# @Create At: 2021-03-17 08:29:24
# @Last Modified By: Xiang Hu
# @Last Modified At: 2021-03-17 09:07:18
# @Description: get input directory path in main program.

import os
import time
from file_scanner import FileScanner

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
            # start time
            start_time = time.time()
            # avoid slash problem
            dir_path = dir_path_str.replace('\\', '/')
            # run file scanning
            rve_inp_gen = FileScanner(dir_path)
            # end time
            end_time = time.time()
            print("\nTotal Run Time: \t {} Seconds.\n".format(float(end_time - start_time)), end='\n')

if __name__ == "__main__":
    # call standard run
    standard_run()