# Processing main voter file

Here are some simple instructions for processing the main voter 
registration file, which is quite distinct from, but related to, the 
voter history file. Most of the work in this project is for the voter 
history file.

Voter history should be around 60 million rows. Voter file's going to be 
more like 6 million rows, but much much wider.

## Shouldn't this be a separate project from voterhist?

Yes. Hush.

### Grab a county lookup table, import into SQL.

https://gist.githubusercontent.com/stucka/d094e072d50ffc58d820/raw/f7c5739f168f5e0c285a2b351f3db1d2df6f179f/fips.sql

### Configuring import, first time

    drop table if exists voters;

    CREATE TABLE voters (
	`CountyCode` VARCHAR(3) NOT NULL, 
	`RegistrationNumber` VARCHAR(8) NOT NULL, 
	`VoterStatus` VARCHAR(1) NOT NULL, 
	`LastName` VARCHAR(20) NOT NULL, 
	`FirstName` VARCHAR(20) NOT NULL, 
	`MiddleMaidenName` VARCHAR(20), 
	`NameSuffix` VARCHAR(4), 
	`NameTitle` VARCHAR(32), 
	`ResidenceHouseNumber` VARCHAR(6) NOT NULL, 
	`ResidenceStreetName` VARCHAR(30) NOT NULL, 
	`ResidenceStreetSuffix` VARCHAR(4), 
	`ResidenceAptUnitNumber` VARCHAR(8), 
	`ResidenceCity` VARCHAR(17) NOT NULL, 
	`ResidenceZip5` varchar(5), 
	`ResidenceZip4` varchar(4), 
	`MIDRFlag` varchar(1), 
	`PollWorker` varchar(1), 
	`TransactionCode` VARCHAR(1) NOT NULL, 
	`TransMonthYear` VARCHAR(6) NOT NULL, 
	`Filler2` VARCHAR(4), 
	`Birthdate` INTEGER NOT NULL, 
	`RegistrationDate` INTEGER NOT NULL, 
	`Race` VARCHAR(1) NOT NULL, 
	`Gender` VARCHAR(1) NOT NULL, 
	`Filler2A` VARCHAR(32), 
	`LandDistrict` VARCHAR(4), 
	`LandLot` VARCHAR(4), 
	`OldRegistrationDate` INTEGER NOT NULL, 
	`StatusReason` VARCHAR(9), 
	`Filler2B` VARCHAR(32), 
	`CountyPrecinctID` VARCHAR(5) NOT NULL, 
	`CityPrecinctID` VARCHAR(5), 
	`CongressionalDistrict` VARCHAR(3) NOT NULL, 
	`SenateDistrict` VARCHAR(3) NOT NULL, 
	`HouseDistrict` VARCHAR(3) NOT NULL, 
	`JudicialDistrict` VARCHAR(3) NOT NULL, 
	`CommissionDistrict` VARCHAR(3) NOT NULL, 
	`SchoolDistrict` VARCHAR(4), 
	`CountyDistAName` VARCHAR(13), 
	`CountyDistAValue` VARCHAR(4), 
	`CountyDistBName` VARCHAR(13), 
	`CountyDistBValue` varchar(32), 
	`MunicipalName` VARCHAR(17), 
	`MunicipalCode` VARCHAR(3) NOT NULL, 
	`WardCityCouncilName` VARCHAR(13), 
	`WardCityCouncilCode` VARCHAR(4), 
	`CitySchoolDistrictName` VARCHAR(13), 
	`CitySchoolDistrictValue` VARCHAR(4), 
	`CityDistAName` VARCHAR(13), 
	`CityDistAValue` VARCHAR(4), 
	`CityDistBName` VARCHAR(32), 
	`CityDistBValue` VARCHAR(32), 
	`CityDistCName` VARCHAR(32), 
	`CityDistCValue` VARCHAR(32), 
	`CityDistDName` VARCHAR(32), 
	`CityDistDValue` VARCHAR(32), 
	`DateLastVoted` INTEGER NOT NULL, 
	`TypeOfElection` VARCHAR(4), 
	`PartyLastVoted` VARCHAR(4), 
	`LastContactDate` INTEGER NOT NULL, 
	`MailHouseNumber` VARCHAR(6), 
	`MailStreetName` VARCHAR(30), 
	`MailStreetSuffix` VARCHAR(4), 
	`MailAptUnitNumber` VARCHAR(8), 
	`MailCity` VARCHAR(17) NOT NULL, 
	`MailState` VARCHAR(4), 
	`MailZip5` varchar(5), 
	`MailZip4` VARCHAR(4), 
	`Filler3` VARCHAR(32), 
	`MailAddress2` VARCHAR(32), 
	`MailAddress3` VARCHAR(32), 
	`MailCountry` VARCHAR(32), 
	`DateAdded` INTEGER NOT NULL, 
	`DateChanged` INTEGER NOT NULL, 
	`DistrictCombo` VARCHAR(3) NOT NULL, 
	`ResBuilding` VARCHAR(32), 
	`MailRRoutePOBox` VARCHAR(8), 
	`CombinedStreetAddress` VARCHAR(60) NOT NULL 
    );

    alter table voters add index (ResidenceStreetName), add index (CountyCode);

## Getting data prepared

These voter records come in two varieties -- fixed-width and delimited. 
Why? Hush.

But the delimited files have a problem with extraneous quote marks that will mess things up.

### Importing delimited data

In command line, run fixdelim.py to strip out the quote marks.

Import routine: 

    truncate table voters;

    LOAD DATA LOCAL INFILE 'DelimV2.txt' INTO TABLE voters FIELDS 
TERMINATED BY '|' enclosed by '"' LINES TERMINATED by "\r\n" ignore 1 
lines;

    commit;

    optimize table voters;
 
### Importing fixed-width data

    truncate table voters;

    set autocommit=0;

    LOAD DATA LOCAL INFILE 'DailyVoterBase_Fixed.txt' INTO TABLE voters FIELDS TERMINATED BY '' LINES TERMINATED by "\r\n";

    show warnings;
   
    commit;

    alter table voters enable keys;

    optimize table voters;

    set autocommit=1;

### Optional: Create local voters table

Customize as you will. "voterslocal" would be a better name; your mileage may vary. Find county codes in the FIPS table you built off the GIST from the above URL.

   drop table if exists votersmidga;

   create table votersmidga AS select * from voters where countycode IN 
("005", "011", "012", "039", "076", "084", "087", "102", "111", "143", 
"158");

    alter table votersmidga add index (countycode), add index 
(ResidenceStreetName), add index (LastName, FirstName), add column 
County varchar(50) first;

