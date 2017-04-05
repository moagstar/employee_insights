Assumptions:

- Records with empty names SHOULD be imported

- Only support for csv dialect as given (utf-8, always headers, comma separated)

- The data should be imported as is, without any cleaning to remove whitespace etc.

- The database is only the current situation, no historical records are built.

- The age (assumed to be in years) that is supplied is only valid at a certain moment in time. This
  timestamp is not supplied in the dataset, so should be supplied with the csv
  file, for example using the upload interface the date to which the csv relates
  should also be supplied.

- Where the city field is empty the state can be used instead.