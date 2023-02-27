def get_iops_and_avg_latency(file_name):
    print(file_name)
    iops = 0
    avg_latency = 0
    record = open(file_name,"r").readlines()[-1]
    data = record.split(" ")
    data = [x for x in data if x !=""]
    avg_latency = float(data[2])
    iops = int(data[4])
    return iops,avg_latency