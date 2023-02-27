#!/usr/bin/env python3
import os
import sqlite3
import pandas as pd


def get_log_dirs(prefix="."):
    result_dirs = []
    for root, dirs, files in os.walk(prefix, topdown=False):
        for dir in dirs:
            if "MB" in dir:
                result_dirs.append(os.path.join(root, dir))
    return result_dirs


def get_log_and_std_files(prefix="."):
    LOG_FILES = []
    stdout_files = []
    for root, dirs, files in os.walk(prefix, topdown=False):
        for filename in files:
            if "stdout" in filename:
                stdout_files.append(os.path.join(root, filename))
            if "LOG" in filename:
                LOG_FILES.append(os.path.join(root, filename))
    return stdout_files, LOG_FILES[0]


class traveler_class:
    LOG_dirs = []
    file_dict = {}  # stderr:"",stdout:"",LOG:"",qps:""

    def __init__(self, base_dir):
        self.LOG_dirs.extend(get_log_dirs(base_dir))
        for log_dir in self.LOG_dirs:
            # print("get files in %s" % log_dir)
            stdout_files, LOG_file = get_log_and_std_files(log_dir)
            self.file_dict[log_dir] = dict(
                stdout_files=stdout_files[0], LOG=LOG_file)
