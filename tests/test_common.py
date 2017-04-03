def get_company_employees(employee_data):
    """
    Returns a generator that when yielded groups employees by company.

    :param employee_data: Hypothesis generated employee database source data.

    :return: Generator which when iterated yields a tuple of
             (company, list of employees).
    """
    for company in employee_data.companies:
        is_employee = lambda x: x.company_id == company.company_id
        company_employees = list(filter(is_employee, employee_data.employees))
        if company_employees:
            yield company, company_employees
