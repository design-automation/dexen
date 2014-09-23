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

function updateActivePane(){
    var $li = $("ul.nav-tabs li.active");
    if($li.length > 0){
        var $a = $($li.find("a:first"));        
        var href = $a.attr("href");
        tabContents[href].onChange(getCurrentJobNameFromTable());
    }
}

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

    setupTable($jobsTable, function($tr){
        updateJobBtns($tr);
        updateActivePane();
    });
}

function ReselectJobRow($table, curJobName){
    this.$table = $table;
    this.jobName = curJobName;
    if(curJobName == null && getSelectedRow($table).length > 0)
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

                return jobName;
            }
        }
        return null;
    }
}

function updateJobsTable(jobs, curJobName) {
    var $jobsTable = $('#jobsTable');
    console.log('Updating jobs %s', jobs);

    var reselectJobRow = new ReselectJobRow($jobsTable, curJobName);

    $jobsTable.dataTable().fnClearTable();
    $.each(jobs, function(index, job) {
        job['creation_time'] = timestampToDateString(job['creation_time']);
        job['start_time'] = timestampToDateString(job['start_time']);
        job['stop_time'] = timestampToDateString(job['stop_time']);
    });
    if(jobs.length > 0)
        $jobsTable.dataTable().fnAddData(jobs);

    var jobName = reselectJobRow.reselect();

    if(jobName == null){
        if(jobs.length == 0){
            $("ul.nav-tabs li").removeClass("active");
            $("ul.nav-tabs li").addClass("disabled");
            $("div.tab-content div.tab-pane").removeClass("active");
            return;
        } else{
            jobName = jobs[0]['job_name'];
            $tr = $jobsTable.find("tr:first");
            selectRow($tr);
            updateJobBtns($tr);
        }
    }

    var $li = $("ul.nav-tabs li");
    $li.removeClass("disabled");

    updateActivePane();    
        
    if($("div.tab-content div.tab-pane.active").length == 0){
        $li.first().find("a:first").tab("show");
    }
}
