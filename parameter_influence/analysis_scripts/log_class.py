import pandas as pd

import re

import numpy as np
import datetime
import time
import json
import gzip

MS_TO_SEC = 1000000


class log_recorder:
    start_time_micros = 0
    log_lines = []
    flush_df = pd.DataFrame(
        columns=["job", "start_time", "end_time", "flush_size"])
    # compaction_df = pd.DataFrame(
    #     columns=["job", "start_time", "end_time", "input_data_size","compaction_time_cpu_micros","total_output_size"])
    compaction_df = pd.DataFrame()
    qps_df = pd.DataFrame()
    end_time_micros = 0
    bucket_df = pd.DataFrame()

    def get_time_from_line(self, log_line):
        regex = r"\d+\/\d+\/\d+-\d+:\d+:\d+\.\d+"
        matches = re.search(regex, log_line, re.MULTILINE)
        machine_start_time = matches.group(0)
        start_time = datetime.datetime.strptime(
            machine_start_time, "%Y/%m/%d-%H:%M:%S.%f")
        start_time_micros = int(time.mktime(
            start_time.timetuple())) * MS_TO_SEC + start_time.microsecond
        return start_time_micros

    def pair_the_flush_jobs(self):
        flush_start_array = [
            x for x in self.log_lines if x["event"] == "flush_started"]
        # job_id = [x["job"] for x in flush_start_array]
        # print(job_id)
        flush_end_array = [
            x for x in self.log_lines if x["event"] == "flush_finished"]
        # flush_df = pd.DataFrame(["job","start_time","end_time","flush_size"])
        for start_event, index in zip(flush_start_array, range(len(flush_start_array))):
            self.flush_df.loc[index] = [start_event["job"],
                                        start_event['time_micros'] -
                                        self.start_time_micros,
                                        flush_end_array[index]["time_micros"]-self.start_time_micros, start_event["total_data_size"]]
        # print(self.flush_df)

    def get_the_compaction_jobs(self):

        # unlike flush, the compaction processes can be run in parallel,
        # which means one compaction that starts later can be finished eariler
        # so we need to sort it by the time_micros first
        compaction_start_df = pd.DataFrame(
            [x for x in self.log_lines if x["event"] == "compaction_started"]).sort_values("job")
        compaction_end_df = pd.DataFrame(
            [x for x in self.log_lines if x["event"] == "compaction_finished"]).sort_values("job")
        # choose the useful columns only
        compaction_start_df = compaction_start_df[[
            "time_micros", "input_data_size", "job","compaction_reason"]]
        compaction_end_df = compaction_end_df[[
            "time_micros", "compaction_time_micros", "compaction_time_cpu_micros", "total_output_size", ]]
        compaction_start_df["time_micros"] -= self.start_time_micros
        compaction_end_df["time_micros"] -= self.start_time_micros

        # let the time_micros minus the start time,

        compaction_start_df = compaction_start_df.rename(
            columns={"time_micros": "start_time"})

        compaction_end_df = compaction_end_df.rename(
            columns={"time_micros": "end_time"})
        # concat the data frames
        self.compaction_df = pd.concat(
            [compaction_start_df, compaction_end_df], axis=1)
        pass

    def record_real_time_qps(self, record_file):
        self.qps_df = pd.read_csv(record_file)
        pass

    def __init__(self, log_file, record_file=""):
        file_lines = []
        if "gz" in log_file:
            f = gzip.open(log_file, "rt")
            file_lines = f.readlines()
        else:
            file_lines = open(log_file, "r").readlines()
        self.start_time_micros = self.get_time_from_line(file_lines[0])
        self.end_time_micros = self.get_time_from_line(file_lines[-1])
        for line in file_lines:
            line = re.search('(\{.+\})', line)
            if line:
                log_row = json.loads(line[0])
                self.log_lines.append(log_row)
        self.pair_the_flush_jobs()
        self.get_the_compaction_jobs()
        if record_file != "":
            self.record_real_time_qps(record_file)
        else:
            # the target dir doesn't have a qps csv
            pass

    def to_vector(self, time_slice=1000000):  # 1 second as time slice by default
        duration_sec = int((self.end_time_micros - self.start_time_micros) / MS_TO_SEC) + 1
        switch_ratio = MS_TO_SEC / time_slice
        feature_columns = ["flushes", "l0compactions",
                           "other_compactions", "read", "write"]
        # flushes, l0compaction,other_compaction,read,write
        # example_row = [0, 0, 0, 0, 0]
        bucket = np.zeros(
            [duration_sec * switch_ratio, len(feature_columns)], dtype=float)
        
        for index, flush_job in self.flush_df.iterrows():
            # bytes/ms , equals to MB/sec
            flush_speed = round(
                flush_job["flush_size"] / (flush_job["end_time"] - flush_job["start_time"]), 2)
            start_index = int(flush_job["start_time"]/time_slice)
            end_index = int(flush_job["end_time"]/time_slice) + 1
            # the tail part is not accurant
            # if start_index >= len(bucket)-10 or end_index >= len(bucket)-5:
            #     break
            for element in bucket[start_index:end_index]:
                element[0] += 1
                element[-1] += flush_speed

        # then we use a bucket sort idea to count down the rest things
        for index, compaction_job in self.compaction_df.iterrows():
            compaction_read_speed = round(compaction_job["input_data_size"] / (
                compaction_job["compaction_time_micros"]), 2)  # bytes/ms , equals to MB/sec
            compaction_write_speed = round(compaction_job["total_output_size"] / (
                compaction_job["compaction_time_micros"]), 2)  # bytes/ms , equals to MB/sec
            start_index = int(compaction_job["start_time"]/time_slice)
            end_index = int(compaction_job["end_time"]/time_slice) + 1

            # the tail part is not accurant
            # if start_index >= len(bucket)-10 or end_index >= len(bucket)-5:
            #     break
            for element in bucket[start_index:end_index]:
                element[0] += 0
                if compaction_job["compaction_reason"] == "LevelL0FilesNum":
                    element[1] += 1
                else:
                    element[2] += 1
                element[-2] += compaction_read_speed
                element[-1] += compaction_write_speed

        bucket_df = pd.DataFrame(bucket, columns=feature_columns)
        self.bucket_df = bucket_df
        return bucket_df
