import os
import sys

work_path = os.getcwd()
os.chdir("../")
print(os.getcwd())
sys.path.insert(0, '.')

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env
from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial
from db_bench_runner import clean_cgroup

os.chdir(work_path)
if __name__ == '__main__':
    env = HardwareEnvironment()
    parameter_dict = load_config_file('config.json')
    set_parameters_to_env(parameter_dict, env)

    result_dir = "PM_fillrandom/"

    common_opt = {
            "duration":3600,
            "report_interval_seconds": 1,
            "value_size":1000,
            "key_size":16,
            "core_num":20,
            "subcompactions":1,
            "mutable_compaction_thread_prior": "false",
            "benchmarks":"fillrandom,stats",
            "report_bg_io_stats":"true",
            "histogram":True,
            "report_thread_idle":False 
    }

    experiment_sets={
<<<<<<< HEAD
#            "baseline":{"FEA_enable":False,"TEA_enable":False},
#            "FEA":{"FEA_enable":True,"TEA_enable":False},
#            "TEA":{"FEA_enable":False,"TEA_enable":True},
            "FEAT":{"FEA_enable":True,"TEA_enable":True},
=======
            "baseline":{"FEA_enable":False,"TEA_enable":False},
            "FEA":{"FEA_enable":True,"TEA_enable":False},
            "TEA":{"FEA_enable":False,"TEA_enable":True},
#            "FEAT":{"FEA_enable":True,"TEA_enable":True},
>>>>>>> 3a066e1468f7caceb151d5a73a77d3d81fb0ab0d
            }

    for experiment in experiment_sets:

        benchmark_opt =  common_opt
        benchmark_opt.update(experiment_sets[experiment])

        temp_result_dir = result_dir +experiment+"/"
        runner = DB_launcher(
            env, temp_result_dir, db_bench=DEFAULT_DB_BENCH, extend_options=benchmark_opt)
        runner.run()
    reset_CPUs()
    clean_cgroup()
