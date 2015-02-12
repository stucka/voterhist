#!/home/mstucka/bin/python
import glob
import csv
import MySQLdb
import datetime
import urllib
import sys
import zipfile
import os
import creds

## Note "import creds" refers to MySQL credentials to be entered in creds.py
## chmod creds.py 700 for more security on Unix machines.

## The Georgia Secretary of State's office has monkeyed with the files but not
## documented what is going on. Filename schema were changed from 2013 on.
## Date formats were changed from 2014 on.
## Other changes, like how election types are reported, are not documented.
## The office has not responded to multiple requests for documentation.

## This keeps old ZIP files, but purges text files including large parsed file.

hostdir=creds.access['hostdir']
dbhost=creds.access['dbhost']
dbuser=creds.access['dbuser']
dbpassword=creds.access['dbpassword']
dbdatabase=creds.access['dbdatabase']

dbhost=MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpassword, db=dbdatabase)
db=dbhost.cursor()

def main():
    print "Starting program ..."
    global MyYears
# Do we have a database? Check. If not, get all the history from 1996. 
    db.execute('''show tables like 'voterhist';''')
    dbreturn=db.fetchone()
    if not dbreturn:
        print "No database found. Starting a new one."
        print "I'll fetch voter history data from 1996."
        MyYears = range(1996, datetime.datetime.today().year + 1)
        RestartDatabaseFromScratch()
    else:
        print "Database found."
        print "I'll update voter history data from the last two years."
        FirstYearICareAbout = datetime.datetime.today().year - 1
        MyYears = range(FirstYearICareAbout, datetime.datetime.today().year + 1)
    DownloadHistory()
    UnzipHistory()
    ParseHistory()
    ImportHistory()
    return


def RestartDatabaseFromScratch():    
    print "Trying to start a new database ..."
#    try:
#        db.execute("""drop table if exists voterhist;""")
#        print "Rows affected in database drop: %d" % db.rowcount
#    except MySQLdb.Error, e:
#        print "Error occurred: %s " % e.args[0]
#        print e
#        
    db.execute("""create table voterhist (CountyCode varchar(3),
        RegistrationNumber varchar(8), ElectionDate date,
        ElectionType varchar(3), Party varchar(1),
        Absentee varchar(1), ElectionYear int);""")

    db.execute("""alter table voterhist add index(RegistrationNumber);""")

    prestring = []
    prestring.append("alter table voterhist partition by range(ElectionYear) (")
    for i in MyYears:
        newyear = i + 1
        prestring.append('partition p' + str(i) + ' values less than (' +
            str(newyear) + '), ')

    for i in range((datetime.datetime.today().year + 1), (datetime.datetime.today().year + 11)):
        newyear = i + 1
        prestring.append('partition p' + str(i) + ' values less than (' +
            str(newyear) + '), ')

    prestring.append("partition pmax values less than (2345));")
    fullstring = ''.join(prestring)
    fullstring = ''.join(prestring)
    print "Trying to execute a really big SQL command: " + fullstring;
#    db.execute("%s", [fullstring])
    db.execute(fullstring)

    return

def DownloadHistory():
    print "Beginning to download history files ..."
#    urlprefix = "http://www.sos.georgia.gov/elections/voter_registration/VoterHistory/"
    urlprefix = "http://sos.ga.gov/Elections/VoterHistoryFiles/"
    for MyYear in MyYears:
        try:
            fullurl = urlprefix + str(MyYear) + ".zip"
            print "    Downloading data: " + fullurl
            fullfile = hostdir + "/VoterHistory" + str(MyYear) + ".zip"
            urllib.urlretrieve(fullurl, fullfile)
        except:
            print "Something went wrong with download."

    return

def UnzipHistory():
    print "Beginning to unzip history files ..."
    for MyYear in MyYears:
        print "    Unzipping data for " + str(MyYear)
        mysourcefile = hostdir + "/VoterHistory" + str(MyYear) + ".zip"
        if os.path.exists(mysourcefile):
            try:
                zip = zipfile.ZipFile(mysourcefile)
                for subfile in zip.namelist():
                        zip.extract(subfile, hostdir)
            except:
                print "Problems unzipping " + mysourcefile
                    
    return

def ParseHistory():
    print "Beginning to parse history files ..."
    bigfilehandle = open('bighistory.txt', 'wb')
    big = csv.writer(bigfilehandle, delimiter = '\t' )
    for MyYear in MyYears:
        if MyYear >= 2013:
	    mysourcefile = hostdir + "/VOTER_HISTORY_" + str(MyYear) + ".TXT"
        else:
            mysourcefile = hostdir + "/Voter History " + str(MyYear) + ".txt"

        print "    Beginning to parse " + mysourcefile
#        print "    Beginning to parse " + str(MyYear) + " now ..."
        if os.path.exists(mysourcefile):
            source = open(mysourcefile, 'r')
            for line in source:
                countycode=line[0:3]
                registrationnumber=line[3:11]
#### HEY! Yes. Yes, 2013 uses the new filename but not the new date structure.
		if MyYear > 2013:
                    electiondate=line[11:15] + "-" + line[15:17] + "-" + line[17:19]
		else:
                    electiondate=line[15:19] + "-" + line[11:13] + "-" + line[13:15]

                electiontype=line[19:22]
                party=line[22]
                absentee=line[23]
                electionyear=line[15:19]
                big.writerow([countycode, registrationnumber,
                                         electiondate, electiontype, party,
                                         absentee, electionyear])

            source.close()
            print "    Deleting file " + mysourcefile
            os.remove(mysourcefile)   # Delete annual text file

    bigfilehandle.close()
    return


def ImportHistory():
    print "Beginning to import parsed voter history ..."
    db.execute("""set autocommit=0;""")
    db.execute("""alter table voterhist disable keys;""")
    for MyYear in MyYears:
        print "    Deleting database records, if any, for year " + str(MyYear)
        db.execute('delete from voterhist where ElectionYear=%s', str(MyYear))
    print "Beginning to import the big file."
    db.execute("""LOAD DATA LOCAL INFILE 'bighistory.txt' into table voterhist fields terminated by "\t";""")
    print "    Rows affected in database add: %d" % db.rowcount
#    print "    Committing to database. Should be quick."
    print "    Re-enabling keys and commiting. This could take a while." 
    db.execute("""commit;""")
    db.execute("""alter table voterhist enable keys;""")
    db.execute("""set autocommit=1;""")
    print "    Deleting parsed history file bighistory.txt"
    os.remove("bighistory.txt")   # Delete annual text file
    print "Wow. I think we might be done."
    return


if __name__ == '__main__':
    main()
