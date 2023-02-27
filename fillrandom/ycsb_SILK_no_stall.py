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
    parameter_dict = load_config_file('SILK_config.json')
    set_parameters_to_env(parameter_dict, env)

    result_dir = "PM_fillrandom/SILK_no_stall/"

    target_dir = result_dir
    runner = DB_launcher(
            env, target_dir, db_bench="/home/supermt/git/SILK-USENIXATC2019/db_bench", extend_options={
            "key_size":16,
            "value_size":1000,
            "duration":3600,
            "report_interval_seconds": 1,
            "benchmarks":"fillrandom,stats",
            "subcompactions":20,
            "level0_slowdown_writes_trigger":2000,
            "level0_stop_writes_trigger":3600,
        })
    runner.run()
    reset_CPUs()
    clean_cgroup()
