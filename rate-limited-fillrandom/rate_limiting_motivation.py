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

    result_dir = "pm_results_rate_limiting_600_1000_bytes/"
    write_in_rates = parameter_dict["benchmark_write_rate_limit"]

    for write_in_rate in write_in_rates:    
        target_result_dir = result_dir+str(write_in_rate)
        print(target_result_dir)
        runner = DB_launcher(
            env, target_result_dir, db_bench=DEFAULT_DB_BENCH, extend_options={
                "value_size":1000,
                "key_size":16,
                "report_interval_seconds": 1,
                "duration": 600,
                "benchmarks":"fillrandom,stats",
                "statistics":"true",
                "benchmark_write_rate_limit":write_in_rate
            })
        runner.run()

    reset_CPUs()
    clean_cgroup()
