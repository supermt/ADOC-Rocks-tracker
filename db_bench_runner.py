import os
import pathlib
import subprocess
from shutil import copyfile, rmtree
import re
import copy
import psutil
import time

import db_bench_option

from db_bench_option import *
# from db_bench_option import CPU_IN_TOTAL
# from db_bench_option import SUDO_PASSWD
# from db_bench_option import CPU_RESTRICTING_TYPE
from parameter_generator import HardwareEnvironment

CGROUP_NAME = "test_group1"
# flags: dRsuvr
# lines: cpu, memory, stack, io, kernel, thread_pri
PID_STAT_DATALINES = [1, 3, 5, 7, 9, 11]

METRICS_MAP = {0: [0, 1, 3, 4],  # %usr,%sys,%CPU
               1: [0, 1, 2, 4],  # minflt/s, majflt/s, VSZ ,%MEM,
               # (minor fault and major fault, major falut will
               #  load a memory page from disk)
               2: [],  # stack line is ignored
               3: [0, 1, 2, 3],  # read, write,
               # canceled write, iodelay
               # canceled writes are caused by page fault
               4: [],  # kernel table, ignored
               5: []  # scheudling table, ignored}
               }


def turn_on_cpu(id):
    # command = "echo 1 | sudo tee /sys/devices/system/cpu/cpu1/online"
    os.system(
        "echo %s|sudo -S %s" % (SUDO_PASSWD, "echo 1 | sudo tee /sys/devices/system/cpu/cpu" + str(id) + "/online"))


def turn_off_cpu(id):
    # command = "echo 1 | sudo tee /sys/devices/system/cpu/cpu1/online"
    os.system(
        "echo %s|sudo -S %s" % (SUDO_PASSWD, "echo 0 | sudo tee /sys/devices/system/cpu/cpu" + str(id) + "/online"))


def restrict_cpus(count, type=0):
    if type == 0:
        restrict_cpus_by_cgroup(count)
    elif type == 1:
        restrict_cpus_by_turning(count)
    elif type == -1:
        pass  # no restricting_cpus, only change the bg threads


def restrict_cpus_by_cgroup(count):
    cgget_result = subprocess.run(
        ['cgget', '-g', 'cpu:'+CGROUP_NAME], stdout=subprocess.PIPE)
    result_strings = cgget_result.stdout.decode('utf-8').split("\n")
    cpu_period_time = 0
    for result_string in result_strings:
        if "cpu.cfs_period_us" in result_string:
            cpu_period_time = int(result_string.split(" ")[1])
    cpu_period_time = cpu_period_time
    print("CPU period time is %d ms" % cpu_period_time)
    cgset_result = subprocess.run(
        ['cgset', '-r', 'cpu.cfs_period_us='+str(cpu_period_time), CGROUP_NAME], stdout=subprocess.PIPE)

    cgset_result = subprocess.run(
        ['cgset', '-r', 'cpu.cfs_quota_us='+str(count*cpu_period_time), CGROUP_NAME], stdout=subprocess.PIPE)

    back_string = cgset_result.stdout.decode('utf-8')
    if back_string == "":
        print("Restrict the CPU period to "+str(count)+" times of CPU quota")
    else:
        print("Restrcting failed due to"+back_string)


def restrict_cpus_by_turning(count):
    reset_CPUs()
    count = int(count)
    if (count > CPU_IN_TOTAL):
        # too many cores asked
        print("no that many cpu cores", count)
        return
    else:
        print("restricting the CPU cores to ", count)
        for id in range(count, CPU_IN_TOTAL):
            turn_off_cpu(id)
        print("finished")


def reset_CPUs(out_control=False,limit_type=1):
    
    if not out_control:
        limit_type = CPU_RESTRICTING_TYPE

    if limit_type == 1:
        for id in range(1, CPU_IN_TOTAL):
            turn_on_cpu(id)
    elif limit_type == 0:
        subprocess.run(
            ['cgset', '-r', 'cpu.cfs_quota_us=-1', CGROUP_NAME])
    else:
        print("CPU not restricted")
        pass
    print("Reset all cpus")

def create_db_path(db_path):
    try:
        pathlib.Path(db_path).mkdir(parents=True, exist_ok=False)
    except Exception:
        print("Path Exists, clearing the files")
        rmtree(db_path)
        pathlib.Path(db_path).mkdir(parents=True, exist_ok=False)


def initial_cgroup():
    cgcreate_result = subprocess.run(
        ['cgcreate', '-g', 'blkio,cpu:/'+CGROUP_NAME], stdout=subprocess.PIPE)
    if cgcreate_result.stdout.decode('utf-8') != "":
        raise Exception("Cgreate failed due to:" +
                        cgcreate_result.stdout.decode('utf-8'))


def clean_cgroup():
    cgdelete_result = subprocess.run(
        ['cgdelete', '-r', 'blkio,cpu:/'+CGROUP_NAME], stdout=subprocess.PIPE)
    if cgdelete_result.stdout.decode('utf-8') != "":
        raise Exception("Cgreate failed due to:" +
                        cgdelete_result.stdout.decode('utf-8'))


def start_iostat(db_path):
    with open(db_path + "/iostat.txt", "wb") as out, open(db_path + "/iostat_err.txt", "wb") as err:
        print("iostat starting")

        device_map = {"pm":"pmem1","nvme":"nvme0n1","ssd":"sda","hdd":"sdc1"}

        iostat_list = ["iostat","1","-m"]

        for target_device in device_map:
            if target_device in db_path:
                iostat_list.append(device_map[target_device])

        iostat_process = subprocess.Popen(iostat_list,stdout=out,stderr = err)

    print(iostat_process.pid)
    return iostat_process

def start_db_bench(db_bench_exec, db_path, options={}, cgroup={}, perf={}):
    """
    Starting the db_bench thread by subprocess.popen(), return the Popen object
    ./db_bench --benchmarks="fillrandom" --key_size=16 --value_size=1024 --db="/media/supermt/hdd/rocksdb"
    """
    if not cgroup:
        cgroup = {"cgexec": "/usr/bin/cgexec",
                  "argument": "-g",
                  "groups": "blkio,cpu:"+CGROUP_NAME
                  }
    # print(options["db"])
    db_path = os.path.abspath(db_path)
    options["db"] = db_path
    create_target_dir(db_path)
    with open(db_path + "/stdout.txt", "wb") as out, open(db_path + "/stderr.txt", "wb") as err:
        print("DB_BENCH starting, with parameters:")
        db_bench_options = parameter_tuning(
            os.path.abspath(db_bench_exec), para_dic=options)
        bootstrap_list = []

        if cgroup:
            # cgroup = {"cgexec":"/usr/bin/cgexec","argument","-g","groups","blkio,cpu:a_group"}
            bootstrap_list.extend(cgroup.values())

        bootstrap_list.extend(db_bench_options)

        db_bench_process = subprocess.Popen(
            bootstrap_list, stdout=out, stderr=err)

        # db_bench_process = subprocess.Popen(db_bench_options, stdout=out, stderr=err)
        print(parameter_printer(db_bench_options))
        # in case there are too many opened files
        os.system('echo %s|sudo -S %s' % (SUDO_PASSWD, "prlimit --pid " +
                                          str(db_bench_process.pid) + " --nofile=20480:40960"))

    print(db_bench_process.pid)
    return db_bench_process


def copy_current_data(src_dir, dst_dir, timestamp, file_names=["MEMORY_USAGE0"]):
    if src_dir[-1] != '/':
        src_dir = src_dir + "/"
    if dst_dir[-1] != '/':
        dst_dir = dst_dir + "/"
    print(file_names)
    for file_name in file_names:
        print("Copying", file_name)
        print(timestamp)
        copyfile(src_dir + file_name, dst_dir +
                 file_name + "_" + str(timestamp))
    return


def create_target_dir(target_path):
    # try:
    pathlib.Path(target_path).mkdir(parents=True, exist_ok=True)
    if len(os.listdir(target_path)) != 0:
        return True
    else:
        return False


class DB_TASK:
#    db_bench = ""
#    result_dir = ""
#    parameter_list = {}
#    cpu_cores = 1
#
    def __init__(self, para_list, db_bench, result_dir, cpu_cores):
        self.parameter_list = copy.deepcopy(para_list)
        self.db_bench = copy.deepcopy(db_bench)
        self.result_dir = copy.deepcopy(result_dir)
        self.cpu_cores = copy.deepcopy(cpu_cores)

    def error_handling(self, db_bench_process, timer, exception):
        p = psutil.Process(db_bench_process.pid)
        print("stopping db_bench: " + str(db_bench_process.pid))
        print(str(exception))
        p.terminate()  # or p.kill()
        reset_CPUs()

    def copy_result_files(self, db_bench_process, gap, timer):
        db_bench_process.wait(gap)
        print("mission complete")

        result_files = ["stderr.txt", "stdout.txt", "LOG","iostat.txt"]

        for file in os.listdir(self.parameter_list["db"]):
            if "report.csv" in file:
                result_files.append(file)

        if self.cpu_cores == CPU_IN_TOTAL or CPU_RESTRICTING_TYPE == -1:
            print("copying with system stat")
            result_files.append("stat_result.csv")
        else:
            pass
        copy_current_data(self.parameter_list["db"], self.result_dir, timer,result_files)


    def run_in_limited_cpu(self, gap=10):
        restrict_cpus(self.cpu_cores, CPU_RESTRICTING_TYPE)
        self.parameter_list["max_background_compactions"] = self.cpu_cores

        try:
            timer = 0
            db_bench_process = start_db_bench(
                self.db_bench, self.parameter_list["db"], self.parameter_list)
            print("Mission started, output is in:%s" % self.result_dir)
            # create_target_dir(self.result_dir)
            while True:
                try:
                    self.copy_result_files(db_bench_process, gap, timer)
                    break
                except subprocess.TimeoutExpired:
                    timer = timer + gap
                    pass
        except Exception as e:
            self.error_handling(db_bench_process, timer, e)
            iostat_process.kill()
        return

    def add_header_psutil(self, stat_recorder):
        stat_recorder.write("secs,"
                            + "user_cpu,sys_cpu,io_wait,cpu_percent,cpu_num,"
                            + "rss,vms,dirty,"
                            + "read_count,write_count,disk_read_bytes,disk_write_bytes,syscall_read_bytes,syscall_write_bytes,"
                            + "num_threads"
                            + "\n")

    def record_psutils(self, timer, p, stat_recorder, gap):
        result_line = []
        result_line.append(timer)
        with p.oneshot():
            # cpu info
            cpu_info = p.cpu_times()._asdict()
            result_line.append(cpu_info["user"])
            result_line.append(cpu_info["system"])
            result_line.append(cpu_info["iowait"])
            result_line.append(float(p.cpu_percent(interval=None))/gap)
            result_line.append(int(p.cpu_num()))
            # mem info
            mem_info = p.memory_info()._asdict()
            result_line.append(mem_info["rss"])
            result_line.append(mem_info["vms"])
            result_line.append(mem_info["dirty"])
            # io_counter
            io_counter = p.io_counters()._asdict()
            result_line.append(io_counter["read_count"])
            result_line.append(io_counter["write_count"])
            result_line.append(io_counter["read_bytes"])
            result_line.append(io_counter["write_bytes"])
            result_line.append(io_counter["read_chars"])
            result_line.append(io_counter["write_chars"])
            # thread_stats
            result_line.append(p.num_threads())
        # print(result_line)
        stat_recorder.write(str(result_line)[1:-1]+"\n")
        return

    def add_header_pidstat(self, stat_recorder):
        stat_recorder.write(
            "timestamp,usr,sys,wait,CPU_utils,minflt,majflt,VSZ,MEM_utils,read_kb,write_kb,ccwr_kb,iodelay\n"
        )

    def record_pidstat(self, timer, db_bench_process, stat_recorder):
        result_line = []
        command_return = os.popen("pidstat -p %d -dRsuvr 1 1 -H" %  # 1 log per sec
                                  db_bench_process.pid).read().splitlines()
        # 03:47:17 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command

        # 03:47:17 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command

        # 03:47:17 PM   UID       PID StkSize  StkRef  Command

        # 03:47:17 PM   UID       PID   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command

        # 03:47:17 PM   UID       PID threads   fd-nr  Command

        # 03:47:17 PM   UID       PID prio policy  Command

        # remove empty lines
        useful_lines = [x for x in command_return[1:] if x]
        # remove column name lines
        data_lines = [useful_lines[x] for x in PID_STAT_DATALINES]
        result_line.append(data_lines[1].split(" ")[0])

        for i in range(len(data_lines)):
            # split the entry according to the spaces
            line_entries = data_lines[i].split(" ")
            # remove empty strings, and remove the Time, UID and PID
            line_entries = [x for x in line_entries if x][3:]
            for metrics in METRICS_MAP[i]:
                entry = line_entries[metrics]
                result_line.append(entry)
        stat_recorder.write(str(result_line)[1:-1]+"\n")
        return

    def record_system_stat(self, timer, db_paths, gap, db_bench_process, devices, stat_recorder):
        Warning.warn(
            "out-of-date function, use the pidstat that may give out all we need", DeprecationWarning)
        result_line = [timer]
        # for db_path in db_paths:
        #     du_line = os.popen("du -s %s" % db_path).read()
        #     du_result = du_line.split()[0]
        #     if not du_result.isnumeric():
        #         return
        #     result_line.append(db_path)
        #     result_line.append(int(du_result))

        # if len(db_paths) == 0:
        #     db_path = self.parameter_list["db"]
        #     du_line = os.popen("du -s %s/" % db_path).read()
        #     # print(du_line)
        #     du_result = du_line.split()[0]
        #     if not du_result.isnumeric():
        #         return

        #     result_line.append(db_path)
        #     result_line.append(int(du_result))

        top_lines = os.popen("top -d %d -b -n 1 -p %d" %
                             (gap, db_bench_process.pid)).read().splitlines()
        cpu_util = float(top_lines[-1].split()[-4])
        result_line.append(cpu_util)
        # io_counter_dict = psutil.disk_io_counters(perdisk=True)
        # for device in devices:
        #     result_line.append(device),
        #     result_line.append(io_counter_dict[device].read_bytes),
        #     result_line.append(io_counter_dict[device].write_bytes)
        result_line = str(result_line)[1:-1]
        stat_recorder.write(result_line+"\n")
        return

    def run_in_full_cpu(self, gap=1):
        restrict_cpus(self.cpu_cores, CPU_RESTRICTING_TYPE)
        self.parameter_list["max_background_compactions"] = self.cpu_cores
        devices = ["sda", "sdb", "nvme0n1"]
        db_paths = []

        if "db_path" in self.parameter_list:
            print("db_paths: %s" % self.parameter_list["db_path"])
            regex = r"(\.\/\w+)*(\/\w+)+"
            matches = re.finditer(
                regex, self.parameter_list["db_path"], re.MULTILINE)
            for m in matches:
                db_paths.append("%s/" % m.group(0))
            for db_path in db_paths:
                os.system("rm -f %s*" % db_path)

        try:
            timer = 0
            db_bench_process = start_db_bench(
                self.db_bench, self.parameter_list["db"], self.parameter_list)
            iostat_process = start_iostat(self.parameter_list["db"],)

            stat_recorder = open(
                self.parameter_list["db"]+"/stat_result.csv", "w")
            # add the header line
            stat_recorder.write("secs,"
                                + "user_cpu,sys_cpu,io_wait,cpu_percent,cpu_num,"
                                + "rss,vms,dirty,"
                                + "read_count,write_count,disk_read_bytes,disk_write_bytes,syscall_read_bytes,syscall_write_bytes,"
                                + "num_threads"
                                + "\n")

            psutil_db_bench = psutil.Process(db_bench_process.pid)

            print("Mission started, output is in:%s" % self.result_dir)
            # create_target_dir(self.result_dir)

            from math import sin
            while True:
                try:
                    stat_recorder.flush()
                    self.copy_result_files(db_bench_process, gap, timer)
                    iostat_process.kill()
                    break
                except subprocess.TimeoutExpired:
                    timer = timer + gap 
                    self.record_psutils(timer, psutil_db_bench, stat_recorder, gap)
                    pass
        except Exception as e:
            self.error_handling(db_bench_process, timer, e)
        # reset_CPUs()
        return

    def run(self, gap=1, force_record=False):
        # clear the cache, or the read bytes will be influenced to be 0 in most cases.
        print("clear the memory cache since all input is the same")
        os.system("sync; echo 1 > /proc/sys/vm/drop_caches")
        if self.cpu_cores == CPU_IN_TOTAL or force_record == True or CPU_RESTRICTING_TYPE == -1:
            self.run_in_full_cpu(gap)
        else:
            self.run_in_limited_cpu(1)


class DB_launcher:
    db_bench_tasks = []
    db_bench = ""
    options = {}

    def __init__(self, env: HardwareEnvironment, result_base, db_bench=DEFAULT_DB_BENCH, extend_options={}):
        self.db_bench_tasks = []
        self.db_bench = db_bench
        self.options = copy.deepcopy(extend_options)
        self.prepare_directories(env, result_base)
        initial_cgroup()
        return

    def prepare_directories(self, env: HardwareEnvironment, work_dir="./db"):
        work_dir = os.path.abspath(work_dir)
        # do not clean this directory
        pathlib.Path(work_dir).mkdir(parents=True, exist_ok=True)

        # check all parameters, prepare the directories and init the tasks

        sub_path = work_dir + "/"

        temp_para_dict = {}

        for material in env.path_list:
            material_dir = sub_path + str(material[1])
            if len(material) == 3:
                temp_para_dict["SILK_bandwidth_limitation"]=material[2]
            pathlib.Path(material_dir).mkdir(parents=True, exist_ok=True)
            temp_para_dict["db"] = str(material[0])
            for cpu_count in env.get_current_CPU_experiment_set():
                result_dir = material_dir + "/" + str(cpu_count) + "CPU"
                temp_para_dict["max_background_compactions"] = str(cpu_count)
                for memory_budget in env.get_current_memory_experiment_set():
                    temp_para_dict["write_buffer_size"] = memory_budget
                    target_dir = result_dir + "/" + \
                        str(int(memory_budget / 1024 / 1024)) + "MB"
                    if create_target_dir(target_dir):
                        print("existing files in %s" % target_dir)
                    else:
                        temp_para_dict.update(self.options)
                        job = DB_TASK(temp_para_dict,
                                        self.db_bench, target_dir, cpu_count)
                        self.db_bench_tasks.append(job)
        return

    def run(self):
        for task in self.db_bench_tasks:
            print("-----------------------------------------")
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            print("-----------------------------------------")
            task.run()
            # print(self.options)
            # pass
