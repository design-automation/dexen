



String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};


function createJob(jobName) {
    $.post("/create_job/" + jobName, function() {
        console.log("/create_job post request is successful.");
        downloadJobs();
    });
}


function runJob(jobName) {
    var url = '/run_job/' + jobName; 
    $.post(url, function() {
        console.log("Running job: " + jobName + "is successful.");
        downloadJobs();
    });    
}


function stopJob(jobName) {
    var url = '/stop_job/' + jobName; 
    $.post(url, function() {
        console.log("Stopping job: " + jobName + "is successful.");
        downloadJobs();
    });        
}


function downloadJobs() {
    $.getJSON('/jobs', function(data) {
        console.log("Downloading jobs successful, jobs data: " + data["jobs"]);
        refreshJobs(data["jobs"]);
    });
}


function registerTask(jobName, task) {
    console.log('Registering task: {0} for job: {1}'.f(jobName, task.task_name));
    console.log(JSON.stringify(task));
    
    $.ajax({
        type: 'POST',
        url: ('/register_task/{0}'.f(jobName)),
        data: JSON.stringify(task),
        contentType: 'application/json',
        dataType: 'json'
    }).done(function(data) {
        console.log('Posting register task is successful.');
        downloadJobs();
    }).fail(function(data, textStatus, jqXHR) {
        console.log("posing register task failed");
        console.log(textStatus);
        console.log(jqXHR.responseText);     
        console.log(jqXHR.statusCode());     
    });
}

function uploadCode() {
    
}


function showLightBox($content, title) {
    $lightbox.children(':not(img):not(#lightboxHeader)').hide();    
    $lightboxHeader.text(title);
    $content.show(); 
    $lightbox.show();
    $lightboxOverlay.show();
}


function closeLightBox()
{
    $lightbox.hide();
    $lightboxOverlay.hide();
}


function setupCreateJobDiv() {
    $createJobDiv = $('#createJobDiv');
    $createJobDiv.children('button').click(function() {
        var jobName = $createJobDiv.find('#jobName').val();
        console.log("Captured job name: " + jobName);
        createJob(jobName);
        closeLightBox();
    });
    
}


function setupRegisterTaskDiv() {
    $registerTaskDiv = $('#registerTaskDiv');

    // Setting up events
    $('#taskType').change(function() {
        var $eventDetailsDiv = $('#eventDetailsDiv');
        var taskType = $('#taskType option:selected').val();
        console.log("task type is " + taskType);
        if (taskType === "event") {
            console.log("showing event details div");
            $eventDetailsDiv.show();    
        }
        else {
            $eventDetailsDiv.hide();            
        }
    });


    $('#eventType').change(function() {
        var eventType = $('#eventType option:selected').val();
        if (eventType === 'PeriodicTimeEvent') {
            $('.eventDivs').hide();
            $('#periodEventDiv').show();
        }
        else if (eventType === 'OneShotTimeEvent') {
            $('.eventDivs').hide();
            $('#oneshotEventDiv').show();
        }
        else {
            $('.eventDivs').hide();
        }
    });
    
    $registerTaskDiv.find('.registerTaskBtn').click(function() {
        var task = {};
        task.task_name = $('#taskName').val();
        task.cmd_args =  $('#cmdLine').val().split(" ");
        var taskType = $('#taskType option:selected').val();
        
        if (taskType === 'event') {
            task['event'] = {};
            var eventType = $('#eventType option:selected').val();
            if (eventType === 'PeriodicTimeEvent') {
                task['event'].name = 'PeriodicTimeEvent';
                task['event'].period = $('#periodTime').val();
            }
            else if (eventType === 'OneShotTimeEvent') {
                task['event'].name = 'OneShotTimeEvent';
                task['event'].after = $('#oneshotTime').val();
            }
            else {
                task['event'].name = eventType;
            }
        }
       
        registerTask($registerTaskDiv.data('job-name'), task);
        closeLightBox();
    });
}


function setupContents() {
    setupCreateJobDiv();
    setupRegisterTaskDiv();    
}


function setupLightBox() {
    $('#lightbox > img').click(function() {
        closeLightBox();
    });
}


function updateTaskInfoDiv($taskInfoDiv, taskInfo) {
    $taskInfoDiv.find('span[data-field]').each(function() {
        var field = $(this).data("field");
        console.log("field is " + field);
        if (field === 'registration_time') {
            var date = new Date(taskInfo[field] * 1000);
            $(this).text(date.toUTCString());
        }
        else {
            $(this).text(taskInfo[field]);
        } 
    });    
}


function attachTaskInfoDiv($taskInfoDiv, $jobInfoDiv) {
    var $tasks = $jobInfoDiv.find('.tasks');
    $('<li></li>').append($taskInfoDiv).appendTo($tasks);
}


function createTaskInfoDiv(taskInfo) {
    var html = '';
    html += '<div class="taskInfo" data-task-name="">'
    html += '    <div> <span>Task Name:</span> <span data-field="task_name"></span> </div>'
    html += '    <div> <span>Registration Time:</span> <span data-field="registration_time"></span> </div>'
    html += '    <div> <span>Num Executions:</span> <span data-field="num_executions"></span> </div>'
    html += '    <div> <span>Avg Execution Time:</span> <span data-field="avg_execution_time"></span> </div>'
    html += '    <div> <span>Num Pending:</span> <span data-field="num_pending"></span> </div>'
    html += '    <div> <span>Num Scheduled:</span> <span data-field="num_scheduled"></span> </div>'
    html += '    <button class="deregisterBtn">Deregister</button>'
    html += '</div>'
    
    var $taskInfoDiv = $(html);
    $taskInfoDiv.attr("data-task-name", taskInfo.task_name);
    
    updateTaskInfoDiv($taskInfoDiv, taskInfo);
    
    return $taskInfoDiv;
}


function updateJobInfoDiv($jobInfoDiv, jobInfo) {

    // Update job header
    $jobInfoDiv.find('span[data-field]').each(function() {
       var field = $(this).data("field");
       console.log("field is " + field);
       $(this).text(jobInfo[field]); 
    });     
    
    $runStopBtn = $jobInfoDiv.find('.runStopBtn');
    if (jobInfo.status === "RUNNING") {
        $runStopBtn.val('stop');
        $runStopBtn.html('Stop');
    }
    else {
        $runStopBtn.val('run');
        $runStopBtn.html('Run');
    }
    
    $.each(jobInfo.event_tasks, function(index, taskInfo) {
        var sel = 'div[data-task-name="{0}"]'.f(taskInfo.task_name);
        var $taskInfoDiv = $jobInfoDiv.find(sel);
        if ($taskInfoDiv.size() === 0) {
            $taskInfoDiv = createTaskInfoDiv(taskInfo);
            attachTaskInfoDiv($taskInfoDiv, $jobInfoDiv);
        }
        else {
            updateTaskInfoDiv($taskInfoDiv, taskInfo);
        }
    });
}


function attachJobInfoDiv($jobInfoDiv) {
    $('<li></li>').append($jobInfoDiv).appendTo($('#jobsDiv #jobs'));    
}


function createJobInfoDiv(jobInfo) {
    console.log("Creating job for {0}".f(jobInfo.job_name));
    
    var html = '';
    html += '<div class="jobInfo" data-job-name="">';
    html += '    <div class="jobHeader">';
    html += '        <span data-field="job_name"></span>';
    html += '        <span data-field="status"></span>';
    html += '        <button class="runStopBtn">Run</button>';
    html += '        <button class="uploadBtn">Upload</button>';    
    html += '        <button class="registerTaskBtn">Register Task</button>';
    html += '        <button class="expandCollapseBtn" value="collapse">Collapse</button>';
    html += '    </div>';
    html += '    <div class="tasksDiv">';
    html += '        <ul class="tasks">';
    html += '        </ul>';
    html += '    </div>';
    html += '</div>';
    
    var $jobInfoDiv = $(html);
    $jobInfoDiv.attr('data-job-name', jobInfo.job_name);

    var $runStopBtn = $jobInfoDiv.find('.runStopBtn'); 
    $runStopBtn.click(function() {
        if ($(this).val() === 'run') {
            runJob(jobInfo.job_name);        
        }
        else {
            stopJob(jobInfo.job_name);
        }
    });

    
    var $uploadBtn = $jobInfoDiv.find('.uploadBtn');
    var $uploadCodeDiv = $('#uploadCodeDiv');
    $uploadBtn.click(function() {
        $uploadCodeDiv.find('form').attr('action', 'upload_file/{0}'.f(jobInfo.job_name));
        showLightBox($uploadCodeDiv, 'Upload Code File');
    });
    
    var $registerTaskBtn = $jobInfoDiv.find('.registerTaskBtn'); 
    $registerTaskBtn.click(function() {
        $registerTaskDiv.data('job-name', jobInfo.job_name);  
        showLightBox($registerTaskDiv, 'REGISTER TASK');
    });

    var $expandCollapseBtn = $jobInfoDiv.find('.expandCollapseBtn'); 
    $expandCollapseBtn.click(function() {
        var $tasksDiv = $jobInfoDiv.find('.tasksDiv');
        if ($expandCollapseBtn.val() === 'expand') {
            $expandCollapseBtn.val('collapse');
            $expandCollapseBtn.html('Collapse');
        }
        else {
            $expandCollapseBtn.val('expand');
            $expandCollapseBtn.html('Expand');
        }
        $tasksDiv.toggle();
    });

    updateJobInfoDiv($jobInfoDiv, jobInfo);

    return $jobInfoDiv;
}


function refreshJobs(jobInfos) {
    $.each(jobInfos, function(index, jobInfo) {
        console.log("Refreshing job {0} at index {1}}".f(jobInfo.job_name, index));
        var sel = 'div[data-job-name="{0}"]'.f(jobInfo.job_name);
        var $jobInfoDiv = $(sel); 
        if ($jobInfoDiv.size() === 0) {
            $jobInfoDiv = createJobInfoDiv(jobInfo);
            attachJobInfoDiv($jobInfoDiv);
        }
        else {
            updateJobInfoDiv($jobInfoDiv, jobInfo);
        }
    });
}

function cacheJqueryObjects() {
    $lightboxOverlay = $('#lightboxOverlay');
    $lightbox = $('#lightbox');
    $lightboxHeader = $('#lightboxHeader');    
}


var execution_fields = {
    'execution_id' : 0,
    'task_name' : 1,
    'worker_name' : 2,
    'creation_time' : 3,
    'begin_time' : 4,
    'end_time' : 5,
    'status' : 6,
    'stdout' : 7,
    'stderr' : 8
};


var execution_data = {};

function updateExecutionTableRow($row, execution) {
    for (var prop in execution) {
        var col = execution_fields[prop];
        $row.children().eq(col).html(execution[prop]);
        //console.log("updateing col {2} with prop {0}: {1}".f(prop, execution[prop], col));
    }    
}

function refreshExecutions(executions) {
     var content = "";  
     content +=  '<tr>';
     content +=     '<td data-field="execution_id"></td>';
     content +=     '<td data-field="task_name"></td>';
     content +=     '<td data-field="worker_name"></td>';
     content +=     '<td data-field="creation_time"></td>';
     content +=     '<td data-field="begin_time"></td>';
     content +=     '<td data-field="end_time"></td>';
     content +=     '<td data-field="status"></td>';
     content +=     '<td data-field="stdout"></td>';
     content +=     '<td data-field="stderr"></td>';
     content +=  '</tr>';

    var $tempDiv = $('<div></div>');

    console.log("execution length is", executions.length);
    $.each(executions, function(index, execution) {
        var exec_id = execution.execution_id.toString();
        if (execution_data.hasOwnProperty(exec_id)) {
            var $row = execution_data[exec_id];
            updateExecutionTableRow($row, execution);
            if (index % 1000 === 0) {
                console.log("updatating index: {0}".f(index));
            }
        }
        else {
            var $r = $(content);
            $tempDiv.append($r);
            updateExecutionTableRow($r, execution);
            execution_data[exec_id] = $r;
        }
    });
    
    $('#executionsTable > tbody').append($tempDiv.children());
    
}

var lastRefresh = 0;

function downloadExecutions() {
    console.log("Downloading Executions");
    var url = 'executions/job55?last_update={0}'.f(lastRefresh);
    lastRefresh = (new Date()).getTime() / 1000.0;
    $.getJSON(url, function(data) {
        console.log("Downloading executions successful");
        refreshExecutions(data.executions);
    });
}

$(document).ready(function() {
    cacheJqueryObjects();
    setupLightBox();
    setupContents();

    //downloadJobs();
    
    /*
    var execs = [];
    for (var i = 0; i < 30000; i++) {
        var t = {};
        t.execution_id = i;
        t.task_name = "task1";
        t.worker_name = "worker";
        t.creation_time = "jan 12";
        t.begin_time = "may 13";
        t.end_time = "22:00";
        t.status = "";
        t.stdout = "";
        t.stderr = "";
        execs.push(t);
    }
    */

    var execs2 = [];
    for (var i = 0; i < 100000; i++) {
        var t = [i, 'task2', 'worker1', '12:00', '14:00', '22:00', 'fdas', 'fad', 'daf'];
        execs2.push(t);
    }
    
    
    $('#executionsHeader .refreshBtn').click(function() {
        //downloadExecutions();
        console.log("Begin refresh executions table");    
        var start = new Date().getTime();
        //refreshExecutions(execs);
        $('#executionsTable').dataTable({
            "bStateSave" : false,
            "aaData" : execs2,
            "aoColumns" : [
                {"sTitle" : "ID"},
                {"sTitle" : "Task Name"},
                {"sTitle" : "Worker Name"},
                {"sTitle" : "Creation Time"},
                {"sTitle" : "Begin Time"},
                {"sTitle" : "End Time"},
                {"sTitle" : "Status"},
                {"sTitle" : "Stdout"},
                {"sTitle" : "Stderr"}
            ]
        });
        
        var end = new Date().getTime();
        console.log("End refresh executions table took {0} seconds".f((end-start)/1000.0));
        
    });
    

    $('#refreshJobBtn').click(function() {
        downloadJobs();    
    });
   
    $('#createJobBtn').click(function() {
        showLightBox($createJobDiv, 'CREATE JOB');
    });
    
    
});



