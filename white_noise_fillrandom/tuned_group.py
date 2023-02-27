import os
import sys

work_path = os.getcwd()
os.chdir("../")
print(os.getcwd())
sys.path.insert(0, '.')

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env
from db_bench_sine_runner import DB_launcher
from db_bench_sine_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial
from db_bench_runner import clean_cgroup

os.chdir(work_path)
if __name__ == '__main__':
   

    tuned_groups={}
    devices_config = {"nvme":{
            "path":"/home/supermt/rocksdb_nvme",
            "device":StorageMaterial.NVMeSSD,
            "cpu_count":6,
            "batch_size":512*1024*1024
        },
        "pm":{
            "path":"/home/supermt/rocksdb_pm",
            "device":StorageMaterial.PM,
            "cpu_count":8,
            "batch_size":256*1024*1024
        },
        "ssd":{
            "path":"/home/supermt/rocksdb_ssd",
            "device":StorageMaterial.SATASSD,
            "cpu_count":4,
            "batch_size":512*1024*1024
        },
        "hdd":{
            "path":"/home/supermt/rocksdb_hdd",
            "device":StorageMaterial.SATAHDD,
            "cpu_count":3,
            "batch_size":512*1024*1024
        }

    }
    for config in devices_config:
        env = HardwareEnvironment()
        entry = devices_config[config]
        env.path_list = [(entry["path"],entry["device"])]
        env.CPU_experiment_set = [entry["cpu_count"]]
        env.Memory_experiment_set = [entry["batch_size"]]
        tuned_groups[config]=env


    os.system("cgcreate -g blkio:/test_group1")
    result_dir = "sine_bandwidth_60GB/tuned/"
    for device in tuned_groups:  
        print(tuned_groups[device].path_list)
        runner = DB_launcher(
            tuned_groups[device], result_dir, db_bench=DEFAULT_DB_BENCH, extend_options={
            "num":60*1000*1000,
            "duration":3600,
            "report_interval_seconds": 1,
            "value_size":1000,
            "key_size":16,
            "subcompactions":20,
            "mutable_compaction_thread_prior": "false",
            "benchmarks":"fillrandom,stats",
            "report_bg_io_stats":"true",
            "histogram":True,
            "report_thread_idle":False,
            "histogram":True,
            })
        runner.run()
        reset_CPUs()
    clean_cgroup()
