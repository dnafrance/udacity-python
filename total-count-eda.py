import unicodecsv
from datetime import datetime as dt

filelist =["enrollments.csv","daily_engagement.csv","project_submissions.csv"]

# Takes a date as string and returns a Python date object
def parse_date(date):
    if date=='':
        return None # returns none if no date given
    else:
        return dt.strptime(date, '%Y-%m-%d')

def parse_maybe_int(i):
    if i =='':
        return None
    else:
        return int(i)

def linecount(filename):
    with open(filename, 'rb') as f:
        reader = list(unicodecsv.DictReader(f))
        return reader
        #return len(reader), reader[0]

def uniquevals(listname,keyname):
    uniquelist = set()
    for row in listname:
        uniquelist.add(row[keyname])
    return uniquelist

def remove_udacity_accounts(data):
    non_udacity_data = []
    for data_point in data:
        if data_point['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(data_point)
    return non_udacity_data

def remove_unpaid(data):
    paid_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            paid_data.append(data_point)
    return paid_data

def within_one_week(join_date, engagement_date):
    time_delta = (engagement_date - join_date).days
    return time_delta < 7 and time_delta >= 0

enrollments = linecount(filelist[0])
# Clean up data types
for enrolment in enrollments:
    enrolment['join_date']=parse_date(enrolment['join_date'])
    enrolment['cancel_date']=parse_date(enrolment['cancel_date'])
    enrolment['days_to_cancel']=parse_maybe_int(enrolment['days_to_cancel'])
    enrolment['is_udacity']=enrolment['is_udacity'] == 'True'
    enrolment['is_canceled']=enrolment['is_canceled'] =='True'

unique_enrollments = uniquevals(enrollments,'account_key')
print filelist[0],len(enrollments),len(unique_enrollments),"\n"

daily_engagement = linecount(filelist[1])
# Clean up data types
for engagement in daily_engagement:
    engagement['account_key'] = engagement['acct']
    del engagement['acct']
    engagement['utc_date']=parse_date(engagement['utc_date'])
    engagement['num_courses_visited']=int(float(engagement['num_courses_visited']))
    engagement['total_minutes_visited']=int(float(engagement['total_minutes_visited']))
    engagement['lessons_completed']=int(float(engagement['lessons_completed']))
    engagement['projects_completed']=int(float(engagement['projects_completed']))
    # Add flag for visit
    engagement['has_visited'] = 0
    if engagement['num_courses_visited']>0:
        engagement['has_visited']=1

unique_daily_engagement = uniquevals(daily_engagement,'account_key')
print filelist[1],len(daily_engagement),len(unique_daily_engagement),"\n"

project_submissions = linecount(filelist[2])
# Clean up data types
for submission in project_submissions:
    submission['creation_date']=parse_date(submission['creation_date'])
    submission['completion_date']=parse_date(submission['completion_date'])

unique_project_subissions = uniquevals(project_submissions,'account_key')
print filelist[2], len(project_submissions),len(unique_project_subissions),"\n"

# Filter students which are not present in daily_engagement
problem_students =0
for enrolment in enrollments:
    student = enrolment['account_key']
    if student not in unique_daily_engagement \
            and enrolment['join_date'] != enrolment['cancel_date']:
        print enrolment
        problem_students += 1
print '# Problem students:',problem_students

# Filter Udacity test students
udacity_test_accounts = set()
for enrolment in enrollments:
    if enrolment['is_udacity']:
        udacity_test_accounts.add(enrolment['account_key'])
print 'Test accounts:',len(udacity_test_accounts)

non_udacity_enrollments = remove_udacity_accounts(enrollments)
non_udacity_engagement = remove_udacity_accounts(daily_engagement)
non_udacity_submissions = remove_udacity_accounts(project_submissions)

print 'Non udacity enrollments:',len(non_udacity_enrollments)
print 'Non udacity engagement:',len(non_udacity_engagement)
print 'Non udacity submissions:',len(non_udacity_submissions)


# Get students who haven't canceled yet or stayed enrolled > 7 days
paid_students = {}
for enrolment in non_udacity_enrollments:
    if not enrolment['is_canceled'] or enrolment['days_to_cancel'] >7:
        account_key = enrolment['account_key']
        enrolment_date = enrolment['join_date']
        paid_students[account_key] = enrolment_date
        # Update with most recent enrolment_date
        if account_key not in paid_students or \
                enrolment_date > paid_students[account_key]:
            paid_students[account_key] = enrolment_date
print '# Paid students',len(paid_students)

# Get engagement for first week

paid_enrollments = remove_unpaid(non_udacity_enrollments)
paid_engagement = remove_unpaid(non_udacity_engagement)
paid_submissions = remove_unpaid(non_udacity_submissions)

print 'Paid enrollments:',len(paid_enrollments)
print 'Paid engagement:',len(paid_engagement)
print 'Paid submissions:',len(paid_submissions)

first_week = []

for engagement in paid_engagement:
    account_key = engagement['account_key']
    join_date = paid_students[account_key]
    engagement_date = engagement['utc_date']
    if within_one_week(join_date,engagement_date):
        first_week.append(engagement)
print '# Paid engagement in first week', len(first_week)

# Get average minutes spent per account
from collections import defaultdict

engagement_by_account = defaultdict(list)
for engagement in first_week:
    account_key = engagement['account_key']
    engagement_by_account[account_key].append(engagement)

# total_minutes_by_account = {}
# for account_key, engagement in engagement_by_account.items():
#     total_minutes = 0
#     for row in engagement:
#         total_minutes += row['total_minutes_visited']
#     total_minutes_by_account[account_key] = total_minutes
#
# total_minutes = total_minutes_by_account.values()

def totals_by_account(parameter):
    total_values_by_account = {}
    for account_key, engagement in engagement_by_account.items():
        total_values = 0
        for row in engagement:
            total_values += row[parameter]
        total_values_by_account[account_key] = total_values
    return total_values_by_account

total_minutes_by_account = totals_by_account('total_minutes_visited')
#total_minutes = total_minutes_by_account.values()
total_lessons_by_account = totals_by_account('lessons_completed')
#total_lessons = total_lessons_by_account.values()

def print_data(data):
    import numpy as np
    max_data = np.max(data.values())
    print '\nAverage:',np.mean(data.values()), \
            '\nStandard deviation:',np.std(data.values()),\
            '\nMaximum:',np.max(data.values()), \
            '\nMinimum:',np.min(data.values())
    return max_data

# Print minutes used
max_data = print_data(total_minutes_by_account)

for account_key, minutes in total_minutes_by_account.items():
    if minutes == max_data:
        print len(engagement_by_account[account_key])

# Get lessons completed
print_data(total_lessons_by_account)

# Get days the student visited the classroom
total_visits_by_account = totals_by_account('has_visited')
print_data(total_visits_by_account)

# Split first week engagement into 2 groups - passed and not-passed
subway_project_lesson_keys = ['746169184','3176718735']
passing_engagement =[]
non_passing_engagement = []
passing_submission = defaultdict(list)
for submission in project_submissions:
    lesson_key = submission['lesson_key']
    rating = submission['assigned_rating']
    if (rating =='PASSED' or rating == 'DISTINCTION') \
            and lesson_key in subway_project_lesson_keys:
        account_key = submission['account_key']
        passing_submission[account_key].append(submission['account_key'])
print 'Passing submissions', len(passing_submission)
for engagement in first_week:
    if engagement['account_key'] in passing_submission:
        passing_engagement.append(engagement)
    else:
        non_passing_engagement.append(engagement)

print 'Passing',len(passing_engagement)
print 'Non-passing',len(non_passing_engagement)
