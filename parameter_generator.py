from enum import Enum

import numpy as np
import psutil


class StorageMaterial(Enum):
    PM = 1
    NVMeSSD = 2
    SATASSD = 3
    SATAHDD = 4
    PM_NOVA = 5
    HYBRID = 6


class HardwareEnvironment:
    # MemSetNo = 5
    # MemSetBase = 8
    # MemSetGap = 2
    #
    # CPUSetNo = 3
    # CPUSetBase = 0
    # CPUSetGap = 2
    def __init__(self):
 
        self.MaxAvaliableCPU = psutil.cpu_count()
        self.MaxAvaliableMemory = psutil.virtual_memory().total

        self.CPU_experiment_set = []
        self.Memory_experiment_set = []
        self.path_list = []

        return

    def config_CPU_by_list(self, cpu_set=[]):
        self.CPU_experiment_set.extend(cpu_set)

    def config_Memory_by_list(self, mem_list=[]):
        self.Memory_experiment_set.extend(mem_list)

    def config_Memory(self, min_mem, set_size):
        # memory can not be given by default, for it's related to the Memtable copy number
        # use log scale to generate parameter set
        result = []
        for i in range(0, set_size):
            result.append(min_mem * (2**i))
        self.Memory_experiment_set = result

    def get_current_memory_experiment_set(self):
        return self.Memory_experiment_set

    def get_current_CPU_experiment_set(self):
        return self.CPU_experiment_set

    def add_storage_path(self, db_path, storage_material):
        self.path_list.append((db_path, storage_material))

    def add_storage_path_with_bandwidth(self,db_path,storage_material,SILK_bandwidth):
        self.path_list.append((db_path,storage_material,SILK_bandwidth))


    def set_storage_path(self,db_path,storage_material):
        self.path_list = [(db_path,storage_material)]

    def get_storage_paths(self):
        return self.path_list
