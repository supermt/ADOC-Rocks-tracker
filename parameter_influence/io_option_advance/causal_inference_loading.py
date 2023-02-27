import scipy.stats as stats
import csv
from traversal import *
import sqlite3
from functools import cmp_to_key

COLUMN_NUM = 5


def create_data_table(conn):
    c = conn.cursor()

    c.execute('''Drop Table if exists speed_results''')
    c.execute("CREATE TABLE speed_results (io_option text, io_option_value, media text, cpu text, batch_size text," +
              "IOPS INT, average_latency_ms REAL" +
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split("/")[-COLUMN_NUM:]
    if "jinghuan" in primary_key_list:	
        primary_key_list = dir_path.split("/")[-(COLUMN_NUM+2):]
        option_path = primary_key_list[1]+primary_key_list[2]+primary_key_list[3]
        primary_key_list = [primary_key_list[0]]+ [option_path] + primary_key_list[4:]
        print(primary_key_list)
    data_row = ""
    for split in primary_key_list:
        data_row += "'"+split.replace("StorageMaterial.", "")+"',"

    iops, avg_latency = std_reader.get_iops_and_avg_latency(stdfile[0])

    data_row += str(iops) + "," + str(avg_latency)

    return data_row


def legend_sorter(x, y):
    if x.isnumeric():
        return float(x) - float(y)
    else:
        return x < y

def anova_one_option(io_option):
    media_list=['SATAHDD','SATASSD','NVMeSSD']
    result_list = []
    for media in media_list:
        df = pd.read_sql_query(
             "SELECT * FROM speed_results where io_option = '%s' and cpu = '12CPU' and media = '%s'" % (io_option,media), db_conn)
        # result_line = "%s,%s,%f" %(media,io_option,df.std()['IOPS'])
        for index,row in df.iterrows():    
            result_line = [row["media"],row["cpu"],row["io_option"],row['io_option_value'],row['IOPS']]
            result_list.append(result_line)
    return result_list

if __name__ == "__main__":
    dirs = get_log_dirs()
    print("Directory Scanned")

    db_conn = sqlite3.connect('speed_info.db')

    create_data_table(db_conn)

    insert_sql_head = "INSERT INTO speed_results VALUES"

    for dir in dirs:
        sql_data_row = get_row(dir)
        sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
        db_conn.execute(sql_sentence)

    print("DB Loaded")

    cursor = db_conn.cursor()

    cpu_group = [2, 4, 8, 12]

    cpu_group = [str(x) + "CPU" for x in cpu_group]

    media = ["SATASSD", "SATAHDD", "NVMeSSD"]
    batch_size_group = ["64MB"]

    io_options = pd.read_sql_query(
        "SELECT io_option FROM speed_results group by io_option ", db_conn)

    # for io_option in io_options["io_option"]:
    #     anova_one_option(io_option)
    csv_file = open('IOPS_12CPU.csv','w',newline='')
    csv_writer = csv.writer(csv_file,dialect='excel')
    csv_writer.writerow(['media','cpu','io_option','option_value','IOPS'])
    for io_option in io_options["io_option"]:
        result_lines = anova_one_option(io_option)
        for result in result_lines:
            csv_writer.writerow(result)
