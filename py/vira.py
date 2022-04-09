#!/usr/bin/env python2
'''
Internals and API functions for vira
'''

# File: py/vira.vim {{{1
# Description: Internals and API functions for vira
# Authors:
#   n0v1c3 (Travis Gall) <https://github.com/n0v1c3>
#   mike.boiko (Mike Boiko) <https://github.com/mikeboiko>
# Version: 0.0.1

# Imports {{{1
from jira import JIRA
import argparse
import datetime
import getpass

# Arguments {{{1
# Parse arguments and show __doc__ and defaults in --help
# Parser {{{2
parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# User {{{2
parser.add_argument(
    '-u', '--user', action='store', default='travis.gall', help='Jira username')

parser.add_argument('-p', '--password', action='store', help='Jira password')

# Server {{{2
parser.add_argument(
    '-s',
    '--server',
    action='store',
    default='https://jira.boiko.online',
    help='URL of jira server')

# Connect {{{1
def vira_connect(server, user, pw):
    '''
    Connect to Jira server with supplied auth details
    '''

    return JIRA(options={'server': server}, auth=(user, pw))

# Issues {{{1
# My Issues {{{2
def vira_my_issues():
    '''
    Get my issues with JQL
    '''

    issues = jira.search_issues(
        'project = AC AND resolution = Unresolved AND assignee in (currentUser()) ORDER BY priority DESC, updated DESC',
        fields='summary,comment',
        json_result='True')

    match = []
    for issue in issues["issues"]:
        print(issue['key'] + ' | ' + issue['fields']['summary'])
        match.append("{\"abbr\": \"%s\", \"menu\": \"%s\"}" % (str(
            issue["key"]), issue["fields"]["summary"].replace("\"", "\\\"")))

    return ','.join(match)

# Issue {{{2
def vira_get_issue(issue):
    '''
    Get single issue by isuue id
    '''

    return jira.issue(issue)

# Comments {{{1
def vira_add_comment(issue, comment):
    '''
    Comment on specified issue
    '''

    jira.add_comment(issue, comment)

def vira_get_comments(issue):
    '''
    Get all the comments for an issue
    '''

    issues = jira.search_issues(
        'issue = "' + issue.key +
        '" AND project = AC AND resolution = Unresolved ORDER BY priority DESC, updated DESC',
        fields='summary,comment',
        json_result='True')
    comments = ''
    for comment in issues["issues"][0]["fields"]["comment"]["comments"]:
        comments += comment['author']['displayName'] + ' | ' + comment['updated'][
            0:10] + ' @ ' + comment['updated'][11:16] + ' | ' + comment['body'] + '\n'

    return comments

# Worklog {{{1
def vira_add_worklog(issue, timeSpentSeconds, comment):
    '''
    Calculate the offset for the start time of the time tracking
    '''

    earlier = datetime.datetime.now() - datetime.timedelta(seconds=timeSpentSeconds)

    jira.add_worklog(
        issue=issue, timeSpentSeconds=timeSpentSeconds, comment=comment, started=earlier)

# Status {{{1
def vira_set_status(issue, status):
    '''
    Selected for Development
    In Progress
    Done
    '''

    jira.transition_issue(issue, status)

# Main {{{1
def main():
    '''
    Main script entry point
    '''

    global jira

    # Get pw if not passed with --password
    mypass = args.password if args.password else getpass.getpass(
        prompt='Password: ', stream=None)

    # Establish connection to JIRA
    jira = vira_connect(args.server, args.user, mypass)

    print('')
    print('Active Issues')
    print('=============')
    vira_my_issues()
    print('')
    issue = vira_get_issue('AC-186')
    print('Issue: ' + issue.key)
    print(vira_get_comments(issue))

    print('')
    issue = vira_get_issue('AC-159')
    print('Issue: ' + issue.key)
    print(vira_get_comments(issue))

# Run script if this file is executed directly
if __name__ == '__main__':
    args = parser.parse_args()
    main()
