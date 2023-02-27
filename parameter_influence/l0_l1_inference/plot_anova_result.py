import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('one-way-anova.csv')
print(df)
df = df.dropna()
sorted_df = df.sort_values(by='std_of_IOPS')


media_list=['SATAHDD','SATASSD','NVMeSSD']

for media in media_list:
    plot_df = sorted_df[sorted_df.media==media]
    fig = plt.figure(figsize=(16,9))
    ax = plt.subplot(111)
    ax.bar(plot_df['io_option'],plot_df['std_of_IOPS'])
    ax.set_ylabel("std deviation of IOPS")
    ax2 = ax.twinx()
    ax2.plot(plot_df['io_option'],plot_df['mean_of_IOPS'],color='red')
    ax2.set_ylabel("mean of IOPS",color='red')
    ax.set_xticklabels(labels=plot_df['io_option'],rotation=-90)
    fig.savefig(media+".pdf",bbox_inches='tight')
    plot_df["io_option"].to_csv("option_rank_in_%s.csv"%media)
#sorted_df.plot(x='io_option',y='std_of_IOPS',kind='bar')

#plt.show()
