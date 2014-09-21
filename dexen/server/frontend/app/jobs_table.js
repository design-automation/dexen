/**
 * Created by kafkef on 6/4/14.
 */



function getCurrentJobNameFromTable() {
    var $jobsTable = $('#jobsTable');
    return getDataFromSelectedRow($jobsTable, jobsTableColsIndex.JOB_NAME);
}

function getCurrentJobStatusFromTable() {
    var $jobsTable = $('#jobsTable');
    return getDataFromSelectedRow($jobsTable, jobsTableColsIndex.STATUS);
}

var jobsTableColsIndex = {
    JOB_NAME: 0,
    STATUS: 1,
    CREATION_TIME: 2,
    START_TIME: 3,
    STOP_TIME: 4
};

function updateJobBtns($tr) {
    var status = getCurrentJobStatusFromTable();
    $('#runJobBtn').disable(status !== 'STOPPED');
    $('#stopJobBtn').disable(status === 'STOPPED');
}

function setupJobsTable() {
    var $jobsTable = $('#jobsTable');
    $jobsTable.dataTable( {
        bPaginate: false,
        bInfo: false,
        bSearchable: false,
        bFilter: false,
        aoColumns: [
            {sTitle: 'Job Name', mData: 'job_name'},
            {sTitle: 'Status', mData: 'status'},
            {sTitle: 'Created', mData: 'creation_time'},
            {sTitle: 'Started', mData: 'start_time'},
            {sTitle: 'Stopped', mData: 'stop_time'}
        ]
    });

    setupTable($jobsTable, updateJobBtns);
}

function ReselectJobRow($table){
    this.$table = $table;
    this.jobName = null;
    if(getSelectedRow($table).length > 0)
        this.jobName = getDataFromSelectedRow($table, jobsTableColsIndex.JOB_NAME);

    this.reselect = function(){
        if(this.jobName != null){
            var jobName = this.jobName;
            var $td = $table.find("tr td:nth-child(" + (jobsTableColsIndex.JOB_NAME+1) + ")").filter(function() {
                return $(this).text() == jobName;
            });
            if($td.length > 0){
                $tr = $td.parent();
                selectRow($tr);
                updateJobBtns($tr);
            }
        }
    }
}

function updateJobsTable(jobs) {
    var $jobsTable = $('#jobsTable');
    console.log('Updating jobs %s', jobs);

    var reselectJobRow = new ReselectJobRow($jobsTable);

    $jobsTable.dataTable().fnClearTable();
    $.each(jobs, function(index, job) {
        job['creation_time'] = timestampToDateString(job['creation_time']);
        job['start_time'] = timestampToDateString(job['start_time']);
        job['stop_time'] = timestampToDateString(job['stop_time']);
    });
    $jobsTable.dataTable().fnAddData(jobs);

    reselectJobRow.reselect();
}
