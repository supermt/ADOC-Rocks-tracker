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
    env = HardwareEnvironment()
    parameter_dict = load_config_file('SILK_config.json')
    set_parameters_to_env(parameter_dict, env)

    print(env.path_list) 
    result_dir = "sine_bandwidth_60GB/SILK/"

    value_sizes = [1000]

    os.system("cgcreate -g blkio:/test_group1")

    for value_size in value_sizes:
        target_dir = result_dir + str(value_size)+"/" 
        benchmark_opt =  {
            }
        runner = DB_launcher(
           env, target_dir, db_bench=DEFAULT_DB_BENCH, extend_options={
               "duration":3600,
                "num":60*1000*1000,
               "value_size":value_size,
               "key_size":16,
               "SILK_triggered":True,
               "benchmarks":"fillrandom,stats",
               "report_bg_io_stats":"true",
               "histogram":True,
               "report_interval_seconds": 1,
               "subcompactions":20,
               "report_bg_io_stats":True,
          })
        runner.run()      
    reset_CPUs()
    clean_cgroup()
