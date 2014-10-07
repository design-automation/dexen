

// Disable function
jQuery.fn.extend({
    disable: function(state) {
        return this.each(function() {
            this.disabled = state;
        });
    }
});

jQuery.postJSON = function(url, data, callback) {
    return jQuery.ajax({
        'type': 'POST',
        'url': url,
        'contentType': 'application/json',
        'data': JSON.stringify(data),
        'dataType': 'json',
        'success': callback
    });
};

var dexen = dexen || {};

function createJob(jobName) {
    console.log('Creating job %s', jobName);
    var xhr = $.post("/create_job/" + jobName);

    xhr.done(function() {
        console.log("/create_job post request is successful.");
        refreshJobs(jobName);
    });
}

function runJob(jobName) {
    var url = '/run_job/' + jobName;
    var xhr = $.post(url);

    xhr.done(function() {
        console.log("Running job: " + jobName + "is successful.");
        refreshJobs(jobName);
    });
}

function stopJob(jobName) {
    var url = '/stop_job/' + jobName;
    var xhr = $.post(url);

    xhr.done(function() {
        console.log("Stopping job: " + jobName + "is successful.");
        refreshJobs(jobName);
    });
}

function refreshJobs(jobName) {
    var xhr = $.getJSON('/jobs');

    xhr.done(function(data) {
        console.log('Downloading jobs successful, jobs data: ' + data['jobs']);
        updateJobsTable(data.jobs, jobName);
    });
}

function setupJobActions() {
    var $jobNameTextBox = $('#jobNameTextBox');
    var $createJobBtn = $('#createJobBtn');
    var $runJobBtn = $('#runJobBtn');
    var $stopJobBtn = $('#stopJobBtn');
    var $refreshAllJobsBtn = $('#refreshAllJobsBtn');
    var $refreshJobFilesBtn = $('#refreshJobFilesBtn');
    var $refreshEventTasksBtn = $('#refreshEventTasksBtn');
    var $refreshDataflowTasksBtn = $('#refreshDataflowTasksBtn');

    $jobNameTextBox.keypress(function(event) {
        if ( event.which == 13 ) {
            $createJobBtn.trigger('click');
        }
    });

    $createJobBtn.click(function() {
        var jobName = prompt("Please enter a job name", "");

        if (jobName != null && jobName.length > 0) {
            createJob(jobName);
        }
    });

    $runJobBtn.click(function() {
        var jobName = getCurrentJobNameFromTable();
        runJob(jobName);
    });

    $stopJobBtn.click(function() {
        var jobName = getCurrentJobNameFromTable();
        stopJob(jobName);
    });

    $refreshAllJobsBtn.click(function() {
        refreshJobs();
    });

    $refreshJobFilesBtn.click(function() {
        refreshJobFiles();
    })
}

function TabContent(fnRefreshTable){
    this.curJobName = null;
    this.refreshTable = fnRefreshTable;
    this.onChange = function(jobName){
        if(this.curJobName != jobName){
            this.curJobName = jobName;
            this.refreshTable();
        }
    };
}


var tabContents = {
    "#filesPane" : new TabContent(refreshJobFiles),
    "#eventTasksPane" : new TabContent(refreshEventTasksTable),
    "#dataflowTasksPane" : new TabContent(refreshDataflowTasksTable),
    "#executionsPane" : new TabContent(refreshExecutionsTable),
    "#dataPane" : new TabContent(refreshJobDataTable),
    "#graphPane" : new TabContent(refreshGraph)
};

function setupTabs(){
    var $tabs = $(".nav-tabs a[data-toggle=tab]");
    $tabs.on("click", function(e) {
        $li = $(this).parent();
        if ($li.hasClass("disabled")) {
            e.preventDefault();
            return false;
        }
    });

    $tabs.on('shown.bs.tab', function (e) {
        var $a = $(e.target);        
        var href = $a.attr("href");
        tabContents[href].onChange(getCurrentJobNameFromTable());
    })
}

$(document).ready(function() {
    console.log('The document is ready');
    setupJobsTable();
    setupTasksTable();
    setupFilesTable();
    setupJobActions();
    setupTasksRegistration();
    setupExecutionsTable();
    setupJobDataTable();
    setupTabs();
    setupGraph();

    refreshJobs();
});
