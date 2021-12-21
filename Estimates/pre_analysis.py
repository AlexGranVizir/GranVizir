import pandas as pd
from collections import Counter

from datetime import datetime


def epic_estimated_vs_actual(team_size, avg_wip_stories, avg_wip_bugs, avg_days_story, bugs_df=None):
    conv_factor_eff_days = 0.8

    data_epic_jira = pd.read_csv("./data/jira_epic_data.csv", index_col=0)
    master_data_file = pd.read_csv("master_data_file.csv", index_col=0)

    data_cols = ['Epic-Key', 'Estimated', 'Actual', 'Lead Time', 'Points', 'Error (%)', 'Error (days)',
                 'Resolution Date']
    data_out = pd.DataFrame()

    for index, row in data_epic_jira.iterrows():
        item = row
        jira_data = data_epic_jira.loc[data_epic_jira['doc_key'] == item['doc_key']]
        if jira_data.empty:
            continue
        elif int(jira_data['story_points'].values[0]) == 0:
            continue
        # count also time spent on bugs
        bugs_data = bugs_df[bugs_df['Epic Link'] == item['doc_key']]
        if bugs_data.size != 0:
            avg_ct_bugs = bugs_data['Cycle Time'].mean()
        else:
            avg_ct_bugs = 0

        actual_by_sp = int(jira_data['story_points'].values[0])*((team_size-avg_wip_bugs)/avg_wip_stories)*avg_days_story*conv_factor_eff_days
        actual_by_bugs = bugs_data.shape[0]*avg_wip_bugs*avg_ct_bugs*conv_factor_eff_days
        total_real = actual_by_bugs + actual_by_sp
        estimate_by_md = master_data_file.loc[item['doc_key'],'Estimate']

        print("\nEpic: %s " % row['doc_key'])
        print("Total Story Points: %s " % int(jira_data['story_points'].values[0]))
        print("Original Estimate: %s" % estimate_by_md)
        print("Actual from Stories: %0.0f" % actual_by_sp)
        print("Actual from Bugs: %0.0f" % actual_by_bugs)
        print("Total Actual: %0.0f" % (total_real))
        error_md = total_real-estimate_by_md
        print("Error (Man/Days): %0.0f" %  error_md)

        rd_int = int(jira_data['resolution_date'].values[0].replace('-',''))
        
        error_pct = 100*(total_real/estimate_by_md - 1.0)
        
        print("Error (%%): %0.0f" %  error_pct)

        data_out = data_out.append({'Epic-Key': row['doc_key'],
            'Points': int(jira_data['story_points'].values[0]) ,
            'Estimated': estimate_by_md,
            'Actual': total_real,
            'Lead Time': jira_data['lead_time'].values[0],
            'Error (%)': error_pct,
            'Error (days)': error_md,
            'Resolution Date': rd_int}, ignore_index=True)
    
    data_out = data_out.reindex(columns=data_cols)
    histogram_from_dataframe(data_out, data_cols[2:], './outputs/epic_hist.png')
    correlation_heatmap_from_dataframe(data_out.drop(columns=['Epic-Key']), './outputs/epic_corr_heat.png')
    regression_plot_from_dataframe(data_out, 'Estimated', 'Actual', 'Epic-Key', './outputs/epic_reg_plot.png')
    data_out.to_csv('./data/pre_analysis_raw_data.csv')

def histogram_from_dataframe(df, features, out_file_name):
    import matplotlib.pyplot as plt
    plt.figure()
    df.hist(column=features)
    plt.savefig(out_file_name)

def correlation_heatmap_from_dataframe(df, out_file_name):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    matrix = np.triu(df.corr())
    plt.figure(figsize=(16, 9))

    corr_mtx = df.corr()
    sns.heatmap(corr_mtx,annot = True, mask=matrix, cmap="RdYlBu",
            xticklabels=corr_mtx.columns,
            yticklabels=corr_mtx.columns)
    plt.yticks(rotation=0)
    plt.savefig(out_file_name)

def regression_plot_from_dataframe(df, x_col, y_col, labels_col, out_file_name):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import seaborn as sns
    import numpy as np
    plt.figure(figsize=(12, 6.75))

    ci_plot=95
    
    ax = sns.regplot(x=x_col, y=y_col, ci=ci_plot, data=df, line_kws={'label': 'Regression'})
    ax.collections[1].set_label('Confidence interval {}%'.format(ci_plot))
    ax.legend(loc='upper left')

    # axis formating TODO: make this a automatic
    ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
    
    #  x and y limits
    plt.ylim(0, None)
    plt.xlim(0, None)
    
    
    for x,y,label in zip(df[x_col],df[y_col],df[labels_col]):
        label = str(label)

        plt.annotate(label, # this is the text
                    (x,y), # this is the point to label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center

    plt.minorticks_on()
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.savefig(out_file_name)



def main():
    data_stories = pd.read_csv("./data/jira_story_data.csv", index_col=0)
    print("Stats for Story Cycle Time") 
    print(data_stories['Cycle Time'].describe())

    data_bugs = pd.read_csv("./data/jira_bug_data.csv", index_col=0)
    print("Stats for Bug Cycle Time") 
    print(data_bugs['Cycle Time'].describe())

    # TODO: get this from the above data
    start = '2016-06-24'
    end = '2020-09-02'

    fmt = '%Y-%m-%d'

    delta_days = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    delta_work_days = abs(float(delta_days.days))*(5/7)
    total_stories = float(data_stories.shape[0])
    total_bugs = float(data_bugs.shape[0])

    team_size = 14
    
    avg_tp_stories = total_stories/delta_work_days
    avg_tp_bugs = total_bugs/delta_work_days
    avg_ct_stories = data_stories["Cycle Time"].mean()
    avg_ct_bugs = data_bugs["Cycle Time"].mean()
    
    total_sp = data_stories["Points"].sum()

    avg_wip_stories = avg_ct_stories*avg_tp_stories    
    avg_wip_bugs = avg_ct_bugs*avg_tp_bugs

    tm_story = team_size/avg_wip_stories
    tm_bugs = avg_wip_bugs

    sp_day = total_sp/delta_work_days
    avg_days_sp = data_stories["Cycle Time"].mean()/data_stories["Points"].mean()
    print("Total timespan in work days: %d" % delta_work_days)
    print("Average Team Size: %d" % team_size)
    print("Average Throughput (Stories/Day): %0.2f" % avg_tp_stories)
    print("Average Throughput (Story Points/Day): %0.2f" % sp_day)
    print("Average Story Cycle Time (Days): %0.2f" % avg_ct_stories)
    print("Average Bug Cycle Time (Days): %0.2f" % avg_ct_bugs)
    print("Average Work-In-Progress Stories: %0.2f" % avg_wip_stories)
    print("Average Work-In-Progress Bugs: %0.2f" % avg_wip_bugs)
    print("Average Allocation of Team Members / Story : %0.2f" % tm_story)
    print("Average Allocation of Team Members / Bugs : %0.2f" % tm_bugs)
    print("Average  Days / Story Point: %0.2f" % avg_days_sp)

    epic_estimated_vs_actual(team_size, avg_wip_stories, avg_wip_bugs, avg_days_sp, data_bugs)



if __name__ == "__main__":
    main()
