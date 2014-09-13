

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
        refreshJobs();
    });
}

function runJob(jobName) {
    var url = '/run_job/' + jobName;
    var xhr = $.post(url);

    xhr.done(function() {
        console.log("Running job: " + jobName + "is successful.");
        refreshJobs();
    });
}

function stopJob(jobName) {
    var url = '/stop_job/' + jobName;
    var xhr = $.post(url);

    xhr.done(function() {
        console.log("Stopping job: " + jobName + "is successful.");
        refreshJobs();
    });
}

function refreshJobs() {
    var xhr = $.getJSON('/jobs');

    xhr.done(function(data) {
        console.log('Downloading jobs successful, jobs data: ' + data['jobs']);
        updateJobsTable(data.jobs);
    });
}

function refreshJobFiles() {
    var url = "/files_metadata/" + getCurrentJobNameFromTable();
    var xhr = $.getJSON(url);

    xhr.done(function(data) {
        console.log('Job files metadata has been received jobs files metadata: ' + data.files_metadata);
        updateJobFilesTable(data.files_metadata);
    });
}

function setupJobActions() {
    var $createJobBtn = $('#createJobBtn');
    var $runJobBtn = $('#runJobBtn');
    var $stopJobBtn = $('#stopJobBtn');
    var $refreshAllJobsBtn = $('#refreshAllJobsBtn');
    var $refreshJobFilesBtn = $('#refreshJobFilesBtn');
    var $refreshEventTasksBtn = $('#refreshEventTasksBtn');
    var $refreshDataflowTasksBtn = $('#refreshDataflowTasksBtn');

    $createJobBtn.click(function() {
        var jobName = $('#jobNameTextBox').val();
        createJob(jobName);
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


$(document).ready(function() {
    console.log('The document is ready');
    setupJobsTable();
    setupTasksTable();
    setupFilesTable();
    setupJobActions();
    setupTasksRegistration();
    setupExecutionsTable();
    setupJobDataTable();
});
