import configparser
from jira import JIRA


class JiraInterface:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('local.cfg')
        self.Server = 'http://10.124.125.122'
        self.jira = None

    def connect(self, jira_password):
        self.jira = JIRA(self.Server,
                    basic_auth=(self.config['JiraCredentials']['Username'], jira_password))

    def close_connection(self):
        self.jira.close()





