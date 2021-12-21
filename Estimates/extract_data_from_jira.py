from jira_lib.jira_interface import *
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from jira_history import *
import getpass

def extract_epic_data(master_file_path, jira_password):
    conn = JiraInterface()
    conn.connect(jira_password)

    master_file = master_file_path
    master_data_df = pd.read_csv(master_file)

    my_cols = ["doc_key", "story_points", "lead_time", "resolution_date"]
    my_df = pd.DataFrame(columns=my_cols)

    for key, row in master_data_df.iterrows():
        jira_key = row['Key']
        # if row['Usable'] == 'N':
        #     continue

        search_string = 'issuetype = Story and "Epic Link" = {}'.format(jira_key)
        results = conn.jira.search_issues(search_string)

        # Sum all story points for this Epic
        sum_of_story_points = 0
        for issue in results:
            if issue.fields.customfield_11202 is not None: # add also into as attribute
                sum_of_story_points += issue.fields.customfield_11202
            else:
                sum_of_story_points += 0

        # find Lead Time (Days)
        fmt = '%Y-%m-%d'
        creation_dates = [x.fields.created for x in results]
        if creation_dates:
            min_creation_date = min(creation_dates)
        else:
            min_creation_date = datetime.now().strftime(fmt)

        # Issues might not be resolved yet
        resolution_dates = [x.fields.resolutiondate for x in results if x.fields.resolutiondate is not None]
        if resolution_dates:
            max_resolution_date = max(resolution_dates)
        else:
            max_resolution_date = datetime.now().strftime(fmt)

        lead_time = datetime.strptime(max_resolution_date[0:10], fmt) - datetime.strptime(min_creation_date[0:10], fmt)

        if sum_of_story_points == 0:
            lead_time = timedelta(days=0)

        print("Epic {}. Total SP {}. Lead time {}. Resolution Date {}".format(jira_key, sum_of_story_points, lead_time.days, \
                                                                              max_resolution_date[0:10]))

        # add to data frame
        doc_key = {'doc_key': jira_key}
        sp = {'story_points': int(sum_of_story_points)}
        lt = {'lead_time': lead_time.days}
        rd = {'resolution_date': max_resolution_date[0:10]}

        # row
        row = {**doc_key, **sp, **lt, **rd}
        my_df = my_df.append(row, ignore_index=True)

    # dump to csv
    my_df.to_csv("./data/jira_epic_data.csv")

    # close JIRA
    conn.close_connection()


def extract_user_stories_data(jira_password):
    conn = JiraInterface()
    conn.connect(jira_password)

    # Completed stories in the last two years
    search_string = 'project = SOL AND issuetype = Story AND status in (Done, Closed) AND Created > "2013/01/01" and "Story Points" is not EMPTY'
    #search_string = 'project = MemberPortal  AND issuetype = Story AND status in (Done, Closed) AND resolutiondate > -720d and "Story Points"  is not EMPTY'
    results = conn.jira.search_issues(search_string,  maxResults=4000, expand="changelog")
    col_labels = ['doc_key', 'Points', 'Lead Time', 'Cycle Time']
    df = pd.DataFrame(columns=col_labels)

    for issue in results:
        add_history(issue)

        state_changes_items = []
        for change in issue.history.changes:
            for item in change.items:
                if item.field == 'status':
                    state_changes_items.append(change)

        if len(state_changes_items) == 0:
            continue

        key = {'doc_key': str(issue)}
        sp = {'Points': issue.fields.customfield_11202}

        # Lead Time (Days)
        lt = {'Lead Time': compute_lead_time(issue)}

        # Cycle Time (Days)
        ct = {'Cycle Time': compute_cycle_time(state_changes_items)}

        if lt['Lead Time'] < ct['Cycle Time']:
            print("Ops this shouldn't happen... Lead < Cycle for {}".format(issue))

        # row
        row = {**key, **sp, **lt, **ct}
        df = df.append(row, ignore_index=True)

    df.to_csv('./data/jira_story_data.csv')

    # plots
    # import matplotlib.pyplot as plt
    # import seaborn as sns

    # from scipy import stats
    # df = df.drop(columns=['doc_key'])
    # df = df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]

    # corr = df.corr().abs()
    # plt.figure(1)
    # sns.boxplot(x=df['Lead Time'])
    # # scatter plot
    #
    # #plt.scatter(df['Lead Time'], df['Points'])
    #
    # #plt.figure(2)
    # #plt.scatter(df['Cycle Time'], df['Points'])
    # plt.show()

    conn.close_connection()

def extract_bug_data(jira_password):
    conn = JiraInterface()
    conn.connect(jira_password)

    # Completed bugs in the from 2013 with an Epic link
    search_string = 'project in (SOL,SOLQA) AND issuetype = Bug AND status in (Done, Closed) AND Created > "2013/01/01" and "Epic Link" is not EMPTY'
    #search_string = 'project = MemberPortal  AND issuetype = Story AND status in (Done, Closed) AND resolutiondate > -720d and "Story Points"  is not EMPTY'
    results = conn.jira.search_issues(search_string,  maxResults=400, expand="changelog")
    col_labels = ['doc_key', 'Lead Time', 'Cycle Time', 'Epic Link']
    df = pd.DataFrame(columns=col_labels)

    for issue in results:
        add_history(issue)

        state_changes_items = []
        for change in issue.history.changes:
            for item in change.items:
                if item.field == 'status':
                    state_changes_items.append(change)

        if len(state_changes_items) == 0:
            continue

        key = {'doc_key': str(issue)}
        epic_link = {'Epic Link': str(issue.fields.customfield_11205)}

        # Lead Time (Days)
        lt = {'Lead Time': compute_lead_time(issue)}

        # Cycle Time (Days)
        res = compute_cycle_time(state_changes_items)
        # check for dubious cycle time
        if res == 0:
            print("Strange Cycle Time for {}".format(issue))
        ct = {'Cycle Time': res}

        if lt['Lead Time'] < ct['Cycle Time']:
            print("Ops this shouldn't happen... Lead < Cycle for {}".format(issue))

        # row
        row = {**key, **lt, **ct, **epic_link}
        df = df.append(row, ignore_index=True)

    df.to_csv('./data/jira_bug_data.csv')

    conn.close_connection()

def compute_lead_time(issue):
    fmt = '%Y-%m-%d'
    timespan = datetime.strptime(issue.fields.resolutiondate[0:10], fmt) - \
                    datetime.strptime(issue.fields.created[0:10], fmt)
    return abs(float(timespan.days))

def compute_cycle_time(state_changes_list):
    ct = 0
    analysis_start = 0
    analysis_end = 0
    dev_start = 0
    dev_end = 0
    qa_start = 0
    qa_end = 0
    for change in state_changes_list:
        # Not a real change
        if any(item.field == 'Workflow' for item in change.items):
                continue
        for item in change.items:            
            if item.toString == 'Under Dev':
                    dev_start = change.created
            if item.fromString == 'Under Dev' and dev_start != 0:
                    dev_end = change.created                    
                    ct += (dev_end-dev_start).days
            if item.toString == 'Under QA':
                    qa_start = change.created
            if item.fromString == 'Under QA' and qa_start != 0:
                    qa_end = change.created
                    ct += (qa_end-qa_start).days
            if item.toString == 'Review Failed':
                    analysis_start = change.created
            if item.fromString == 'Review Failed' and analysis_start != 0:
                    analysis_end = change.created
                    ct += (analysis_end-analysis_start).days
            # to cover legacy workflow
            if item.toString == 'In Progress':
                    dev_start = change.created
            if item.fromString == 'In Progress' and dev_start != 0:
                    dev_end = change.created
                    ct += (dev_end-dev_start).days
            if item.toString == 'Pending':
                    qa_start = change.created
            if item.fromString == 'In Progress' and qa_start != 0:
                    qa_end = change.created
                    ct += (qa_end-qa_start).days
            else:
                continue
    return ct


def main():
    master_file_path = "./master_data_file.csv"
    jira_pass = getpass.getpass(prompt='Tell me your Jira Pass: ', stream=None)
    extract_bug_data(jira_pass)
    extract_user_stories_data(jira_pass)
    extract_epic_data(master_file_path, jira_pass)


if __name__ == "__main__":
    main()
