# default path parameter

import os
import sys


work_path = os.getcwd()
os.chdir("../")
print(os.getcwd())
sys.path.insert(0,'.')

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import CPU_IN_TOTAL
from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial

os.chdir(work_path)

if __name__ == '__main__':
    env = HardwareEnvironment()
    CPU_IN_TOTAL = 12
    io_bandwidth=[100,200,400]
    path_suffix = [str(band)+"mb" for band in io_bandwidth] 
    
    env.config_CPU_by_list([1,4,8,12])
    env.config_Memory(min_mem=(16 * 1024 * 1024), set_size=4)

    env.add_storage_path("/home/jinghuan/rocksdb_hdd",StorageMaterial.SATAHDD)
    env.add_storage_path("/home/jinghuan/rocksdb_sata",StorageMaterial.SATASSD)
    env.add_storage_path("/home/jinghuan/rocksdb_nvme",StorageMaterial.NVMeSSD)
    # env.add_storage_path("/home/jinghuan/rocksdb_pmem",StorageMaterial.NVMeSSD)

    reset_CPUs()
   
    os.system("cgcreate -g blkio:/test_group1")
    for bandwidth in io_bandwidth:
        # Limit for HDD
        os.system('cgset -r blkio.throttle.write_bps_device="8:0 '+str(bandwidth*1024*1024)+'" test_group1')
        # Limit for SATA SSD
        os.system('cgset -r blkio.throttle.write_bps_device="8:16 '+str(bandwidth*1024*1024)+'" test_group1')
        # Limit for NVMe SSD
        os.system('cgset -r blkio.throttle.write_bps_device="259:0 '+str(bandwidth*1024*1024)+'" test_group1')
        # test for the limiting
        os.system('cat /sys/fs/cgroup/blkio/test_group1/blkio.throttle.write_bps_device')
        DB_launcher(env,"/home/jinghuan/2gb/bandwidth_limiting/"+str(bandwidth)+"mb", db_bench= DEFAULT_DB_BENCH).run()
    os.system("cgdelete blkio:/test_group1")
#    DB_launcher(env,"/home/jinghuan/5gb/bandwidth_limiting/"+"unlimited", db_bench= DEFAULT_DB_BENCH).run()
    reset_CPUs()
