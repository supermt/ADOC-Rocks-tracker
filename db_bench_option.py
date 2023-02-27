import multiprocessing
from configparser import ConfigParser
import json
from parameter_generator import StorageMaterial

default_cfg = ConfigParser()
default_cfg.read("default.ini")

SUDO_PASSWD = default_cfg.get("Permission", "passwd")
DEFAULT_DB_BENCH = default_cfg.get("Paths", "db_bench_path")

CPU_RESTRICTING_TYPE = int(default_cfg.get("CPU", "limit_type"))

print("config loaded")
print("CPU limiting type :", CPU_RESTRICTING_TYPE)

# default Memory parameter
DEFAULT_MEMTABLE_SIZE = 64 * 1024 * 2014  # 256M, memtable size
DEFAULT_IMMU_COUNT = 2  # how many immutable tables
DEFAULT_IMMU_COMBIN = 1  # forget about this
DEFAULT_COMPACTION_TRIGGER = 4  # how many l0 compacted to l1
DEFAULT_L1_SIZE = 64 * 1024 * 1024


# default disk options
DEFAULT_BLOCK_SIZE = 64 * 1024  # 64 KB block
DEFAULT_COMPRESSION = "none"

# default disk caching options, runtime memory overhead
DEFAULT_BLOOM_BIT = 10

# default entry options
DEFAULT_KEY_SIZE = 8
DEFAULT_VALUE_SIZE = 100
DEFAULT_DB_SIZE = int(default_cfg.get("Entry Control", "db_size"))
DEFAULT_ENTRY_COUNT = int(DEFAULT_DB_SIZE / DEFAULT_VALUE_SIZE)

# default CPU options
DEFAULT_COMPACTION_WORKER = str(multiprocessing.cpu_count())
CPU_IN_TOTAL = int(default_cfg.get("CPU", "cpu_in_total"))

ori_parameter_list = {
    "db": DEFAULT_DB_BENCH,
    "benchmarks": "fillrandom",
    "num": DEFAULT_ENTRY_COUNT,
    "key_size": DEFAULT_KEY_SIZE,
    "value_size": DEFAULT_VALUE_SIZE,
    "write_buffer_size": DEFAULT_MEMTABLE_SIZE,  # Memtable Size, 256 M
    "target_file_size_base": str(DEFAULT_L1_SIZE),  # L1 FILE
    "min_write_buffer_number_to_merge": DEFAULT_IMMU_COMBIN,
    "max_write_buffer_number": DEFAULT_IMMU_COUNT,
    "level0_file_num_compaction_trigger": DEFAULT_COMPACTION_TRIGGER,
    "level0_slowdown_writes_trigger": 20,
    "max_background_compactions": DEFAULT_COMPACTION_WORKER,
    "max_background_flushes": 1,  # we are focus on single material environment
    "threads": 1,  # control the input pressure, increase all resource requirement
    "bloom_bits": str(DEFAULT_BLOOM_BIT),
    "compression_type": DEFAULT_COMPRESSION,
    "base_background_compactions": 1,
    "report_bg_io_stats": False,
    # "detailed_running_stats":True
}


def load_config_file(filename='template.json'):
    f = open(filename,)
    return json.load(f)


def set_parameters_to_env(cfg, env):
    try:
        env.config_CPU_by_list(cfg['cpu_set'])
        mem_list = cfg['memtable_size_set']

        mem_size_list = []

        for mem_size in mem_list:
            if type(mem_size) == str:
                mem_size_list.append(eval(mem_size))
            else:
                mem_size_list.append(mem_size)
        # print(mem_size_list)

        env.config_Memory_by_list(mem_size_list)

        if "db_path" in cfg:
            pass
            # for path_combine in cfg["db_path"]:
            #     env.add_storage_path(path_combine[0]['path'],StorageMaterial.HYBRID)
        else:
            for storage_path in cfg['storage_paths']:
                if "bandwidth" in storage_path:
                    env.add_storage_path_with_bandwidth(storage_path['path'],StorageMaterial[storage_path['media_type']],storage_path['bandwidth'])
                else:
                    env.add_storage_path(
                    storage_path['path'], StorageMaterial[storage_path['media_type']])
    except KeyError as errormsg:
        print("Missing configuration entry or error configuration entry: " +
              str(errormsg)+" please read the template.json file as a reference")
    else:
        print("All parameter loaded")


def dual_option_optimizes(parameter_list):
    # this function is used to set the options that has influence between each others, some options may depend on another option to be triggered.
    if 'use_cuckoo_table' in parameter_list:
        parameter_list['mmap_write'] = True
        parameter_list['mmap_read'] = True
    if 'use_hash_search' in parameter_list:
        parameter_list['prefix_size'] = 4


def tuning_strategy_l0_equals_l1(parameter_list):
    parameter_list["max_bytes_for_level_base"] = int(parameter_list["write_buffer_size"]) * int(
        parameter_list["min_write_buffer_number_to_merge"]) * int(parameter_list["level0_file_num_compaction_trigger"])


def basic_tuning(parameter_list,sync_sst_size=True):
    dual_option_optimizes(parameter_list)
    if sync_sst_size:
        parameter_list["target_file_size_base"] = int(
            parameter_list["write_buffer_size"])
    pass

def set_qps_report_location(parameter_list):
    if "report_interval_seconds" in parameter_list:
        print("report qps in report.csv")
        parameter_list["report_file"] = parameter_list["db"]+"/report.csv"


def parameter_tuning(db_bench, para_dic={}):
    print(db_bench)
    if db_bench == "":
        db_bench = DEFAULT_DB_BENCH
    #filled_para_list = ["cgexec -g blkio:test_group1",db_bench]
    # filled_para_list = ['/usr/bin/cgexec','-g','blkio:test_group1',db_bench]
    filled_para_list = [db_bench]
    # use para_dic to modify the default parameter
    parameter_list = {}
    parameter_list.update(ori_parameter_list)
    for para in para_dic:
        parameter_list[para] = str(para_dic[para])
    
    # passed from outer function, set false if not provided
    if "sync_sst_size" in para_dic:
        parameter_list.pop("sync_sst_size",None)
    else:
        para_dic["sync_sst_size"]=True

    if "single_threaded_flush" in para_dic:
        parameter_list.pop("single_threaded_flush",None)
        # parameter_list["base_background_compactions"] = parameter_list["max_background_compactions"] 
        parameter_list["max_background_jobs"] = int(parameter_list["max_background_compactions"]) + int(parameter_list["max_background_flushes"])
    else:
        if parameter_list["max_background_compactions"] == 1:
            parameter_list["max_background_jobs"] = int(parameter_list["max_background_compactions"]) + 1
        else:
            parameter_list["max_background_jobs"] =  int(parameter_list["max_background_compactions"])

        parameter_list.pop("max_background_compactions",None)
        parameter_list.pop("max_background_flushes",None)



    basic_tuning(parameter_list,para_dic["sync_sst_size"])
    tuning_strategy_l0_equals_l1(parameter_list)
    
    set_qps_report_location(parameter_list)

    # some values need calculation
    parameter_list["num"] = str(para_dic.get("num", str(
        int(DEFAULT_DB_SIZE / int(parameter_list["value_size"])))))
    parameter_list["level0_stop_writes_trigger"] = int(
        int(parameter_list["level0_slowdown_writes_trigger"])*36/20)

    # transform into string format
    for parameter in parameter_list:
        filled_para = "--" + parameter + "=" + str(parameter_list[parameter])
        filled_para_list.append(filled_para)

    return filled_para_list


def parameter_printer(filled_para_list):
    command = ""
    for para in filled_para_list:
        command += (para + " ")
    return command
