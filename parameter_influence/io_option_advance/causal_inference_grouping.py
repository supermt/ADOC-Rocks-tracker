import pandas as pd

SOURCE_DATA = "IOPS_12CPU.csv"

df = pd.read_csv(SOURCE_DATA)

df_ssd_only = df[df["media"] == "SATAHDD"]

grouped = df_ssd_only.groupby("io_option")

# test the l0 l1 size problem first
# l0 file size
# write_buffer_size * min_write_buffer_number_to_merge * level0_file_num_compaction_trigger
# l1 file size
# target_file_size_base for single
# max_bytes_for_level_base for all
size_ratio_related_options = ["write_buffer_size", "min_write_buffer_number_to_merge",
                              "level0_file_num_compaction_trigger", "max_bytes_for_level_base"]
df_l0_l1 = df_ssd_only[df_ssd_only["io_option"].isin(size_ratio_related_options)]

print(df_l0_l1)

