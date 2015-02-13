## What is this I don't even

This Python script is to ingest the Georgia Secretary of State's
voter history records into a large (~60 million row) MySQL database.

### Installation

Install it through Github or download the ZIP.

Install Python dependencies.

Edit creds.py to give it your MySQL credentials and set the working directory.

### Execution

The first time you run voterhist.py, it will set up the database, then 
download and ingest voter histories from 1996 on.

The next time you run it, it will get rid of the current and previous 
years' histories, then fetch and ingest those. In other words, it's 
built to do incremental updates for the current and previous years.

So try to run it at least once a year. If you miss that, you can always 
drop the voterhist table through MySQL, and it will start fresh.

If you corrupt anything, drop the voterhist table through MySQL and it 
will start fresh.

=== Cleanup

This thing is set to download ZIPs with each year's records in a text 
file; process those annual text files and parse them into a single large 
text file; then ingest that text file. When it's done, it trashes the 
parsed and annual text files, but leaves the annual ZIP files intact.

Why, yes, at some point I ought to put in mirroring, such that it won't 
download or process ZIP files that haven't been updated.

Pull requests, comments and suggestions are welcomed.
