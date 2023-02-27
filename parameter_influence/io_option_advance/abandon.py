from traversal import *
import sqlite3
import plotly.express as px
from functools import cmp_to_key

COLUMN_NUM = 5


def create_data_table(conn):
    c = conn.cursor()

    c.execute('''Drop Table if exists speed_results''')
    c.execute("CREATE TABLE speed_results (io_option text, io_option_value, media text, cpu text, batch_size text," +
              "IOPS INT, average_latency_ms REAL" +
              # ",compaction_frequency INT, overall_compaction_latency INT" +
              # ",overall_compaction_cpu_latency INT"+
              # ",overall_input_record INT"+
              # ",overall_output_record INT"+
              # ",overall_redundant_record INT"+
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split("/")[-COLUMN_NUM:]
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


def plot_by_io_option(io_option):
    df = pd.read_sql_query(
        "SELECT * FROM speed_results where io_option = '%s' and cpu != '1CPU' " % io_option, db_conn)

    legends = df["io_option_value"].unique()
    legends = sorted(legends, key=cmp_to_key(legend_sorter))

    fig = px.bar(df, x="cpu", y="IOPS", color="io_option_value", barmode="group",
                 facet_col="io_option",
                 facet_row="media",
                 category_orders={
                     "cpu": cpu_group,
                     "batch_size": batch_size_group,
                     "media": media,
                     "io_option_value": legends
                 },
                 labels={"cpu": "", "IOPS": "Throughput (OPs/sec)"},
                 #  color_discrete_map=batch_size_to_color_map
                 )
    fontsize = 20

    fig.update_layout(
        autosize=False,
        width=1600,
        height=900,
        font=dict(size=fontsize),
        plot_bgcolor='white',
    )
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    # fig.show()
    fig_name = "image/%s.pdf" % io_option
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)


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
#     bandwidth_group = ['400', '800', '1200', '1600', '2000']
#     bandwidth_group = [x + "mb" for x in bandwidth_group]
    size_color = {16: "rgb(66,106,199)", 32: "rgb(254,117,0)",
                  64: "rgb(165,165,165)", 128: "rgb(255,194,0)"}
    batch_size_to_color_map = {
        "16MB": "rgb(66,106,199)",
        "32MB": "rgb(254,117,0)",
        "64MB": "rgb(165,165,165)",
        "128MB": "rgb(255,194,0)"
    }
    media = ["SATASSD", "SATAHDD", "NVMeSSD"]
    batch_size_group = ["64MB"]

    io_options = pd.read_sql_query(
        "SELECT io_option FROM speed_results group by io_option ", db_conn)

    for io_option in io_options["io_option"]:
        plot_by_io_option(io_option)
    # plot_by_io_option("block_size")
