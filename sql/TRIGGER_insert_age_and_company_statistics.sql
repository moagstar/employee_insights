CREATE TRIGGER insert_age_and_company_statistics AFTER INSERT ON employee
BEGIN
  UPDATE  employee
  SET     age = julianday('NOW') - julianday(new.date_of_birth)
  WHERE   employee_id = new.employee_id;

  REPLACE INTO company_statistic
  SELECT company.company_id AS company_company_id, avg(employee.age) AS average_age
  FROM company JOIN employee ON company.company_id = employee.company_id;

END;