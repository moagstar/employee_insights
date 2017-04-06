/**
 * Show the initial data in the database and set the upload success handler
 * on the dropzone.
 */
$(document).ready(function () {
    loadResultTable();
    Dropzone.options.importEmployeesCsv = { success: loadResultTable };
});