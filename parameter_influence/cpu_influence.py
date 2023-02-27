# default path parameter
import os
import sys

work_path = os.getcwd()
os.chdir("../")
print(os.getcwd())
sys.path.insert(0,'.')
from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env

from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial
from db_bench_option import set_parameters_to_env

from db_bench_runner import clean_cgroup
os.chdir(work_path)
if __name__ == '__main__':
    env = HardwareEnvironment()
    parameter_dict = load_config_file('template.json')
    set_parameters_to_env(parameter_dict,env)

    result_dir_prefix = "/media/jinghuan/hdd/cpu_influence"


    io_options = parameter_dict["io_options"]

    for io_option_key in io_options:
        for io_option_value in io_options[io_option_key]:
            result_dir = result_dir_prefix + "/%s/%s" % (io_option_key, str(io_option_value))
            print(result_dir)
            extend_options = {io_option_key:io_option_value}
            runner = DB_launcher(env,result_dir, db_bench=DEFAULT_DB_BENCH,extend_options=extend_options)
            runner.run()
            reset_CPUs()
    # runner.run()
    # reset_CPUs()
    clean_cgroup()
