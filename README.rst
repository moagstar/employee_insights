Assumptions:

- Some records have empty first, last name which implies that these fields
  should be optional, perhaps these employees prefer to remain anon? These
  records should be imported.

- The upload function only needs to work with a csv file as given, for example
  I don't need to support a csv file which is supplied in the form FullName and
  split this into first_name and last_name. No need to support different dialects etc.

- The data should be imported as is, without any cleaning to remove whitespace etc.

- The database is only the current situation, no historical records are built.

- The age that is supplied is only valid at a certain moment in time. This
  timestamp is not supplied in the dataset, so should be supplied with the csv
  file, for example using the upload interface the date to which the csv relates
  should also be supplied.

- The age that is supplied is assumed to in years.

- Header field is always present in csv.

- Csv is supplied in UTF-8 encoding