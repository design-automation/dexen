/**
 * Created by kafkef on 6/4/14.
 */



function setupEventTasksTable() {
    var $table = $('#eventTasksTable');
    var $registerBtn = $('#registerEventTaskBtn');
    var $registrationDialog = $('#eventTaskRegistrationModal');
    var $refreshBtn = $('#refreshEventTasksBtn');

    $table.dataTable( {
        bPaginate: false,
        bInfo: false,
        bSearchable: false,
        bFilter: false,
        aoColumns: [
            {sTitle: 'Name', mData: 'task_name'},
            {sTitle: 'Registration Time', mData: 'registration_time'},
            {sTitle: 'Num Pending', mData: 'num_pending'},
            {sTitle: 'Num Scheduled', mData: 'num_scheduled'},
            {sTitle: 'Total Executions', mData: 'num_executions'},
            {sTitle: 'Avg. Execution Time', mData: 'avg_execution_time'},
        ]
    });

    setupTable($table, function() {
        console.log('Row is selected call back in event tasks table.');
    });

    $registerBtn.click(function() {
        $registrationDialog.modal();
    });

    $refreshBtn.click(function() {
        refreshEventTasksTable();
    });
}

function setupDataflowTasksTable() {
    var $table = $('#dataflowTasksTable');
    var $registerBtn = $('#registerDataflowTaskBtn');
    var $registrationDialog = $('#dataflowTaskRegistrationModal');
    var $refreshBtn = $('#refreshDataflowTasksBtn');

    $table.dataTable({
        bPaginate: false,
        bInfo: false,
        bSearchable: false,
        bFilter: false,
        aoColumns: [
            {sTitle: 'Name', mData: 'task_name'},
            {sTitle: 'Registration Time', mData: 'registration_time'},
            {sTitle: 'Num Pending Data', mData: 'num_pending_data'},
            {sTitle: 'Num Scheduled Data', mData: 'num_scheduled_data'},
            {sTitle: 'Scheduled Executions', mData: 'num_scheduled_executions'},
            {sTitle: 'Failed Executions', mData: 'num_failed_executions'},
            {sTitle: 'Total Executions', mData: 'num_executions'},
            {sTitle: 'Avg. Execution Time', mData: 'avg_execution_time'},
        ]
    });

    setupTable($table, function() {
        console.log('Row is selected call back in data flow tasks table.');
    });

    $registerBtn.click(function() {
        $registrationDialog.modal();
    });

    $refreshBtn.click(function() {
        refreshDataflowTasksTable();
    });
}

function setupTasksTable() {
    setupEventTasksTable();
    setupDataflowTasksTable();
}
