import unicodecsv

filelist =["enrollments.csv","daily_engagement.csv","project_submissions.csv","table_descriptions.txt"]

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

for f in filelist:
    vals = linecount(f)
    print 'Filename:',f, "\nNumber of rows:", len(vals), "\nFirst row:", vals[0]
    if f == filelist[1]:
        keyname = 'acct'
    else:
        keyname = 'account_key'
    if f != filelist[3]:
        print 'Number of unique rows:',len(uniquevals(vals,keyname)),"\n"
