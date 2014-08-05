


var EventType = {
    JobStoppedEvent: 'JobStoppedEvent',
    JobStartedEvent: 'JobStartedEvent',
    PeriodicTimeEvent: 'PeriodicTimeEvent',
    OneShotTimeEvent: 'OneShotTimeEvent'
};

var TaskType = {
    EventTask: 'EventTask',
    DataflowTask: 'DataflowTask'
};

function updateTasksTable($table, tasks) {
    console.log('Updating event task tables', tasks);
    $table.dataTable().fnClearTable();
    $.each(tasks, function(index, task) {
        task['registration_time'] = timestampToDateString(task['registration_time']);
    });
    $table.dataTable().fnAddData(tasks);
}

function refreshEventTasksTable() {
    var jobName = getCurrentJobNameFromTable();
    var xhr = $.get('/tasks/' + jobName);
    xhr.done(function(data) {
        console.log('refresh event tasks done', data);
        updateTasksTable($('#eventTasksTable'), data.tasks.event_tasks);
    });
}

function refreshDataflowTasksTable() {
    var jobName = getCurrentJobNameFromTable();
    var xhr = $.get('/tasks/' + jobName);
    xhr.done(function(data) {
        console.log('refresh dataflow tasks done', data);
        updateTasksTable($('#dataflowTasksTable'), data.tasks.dataflow_tasks);
    });
}

function registerTask(jobName, task, taskType) {
    console.log('Issuing /register_task post request.');
    var xhr = $.postJSON("/register_task/" + jobName, task);
    xhr.done(function(data) {
        console.log('post /register_task is done.');
        if (taskType === TaskType.EventTask) {
            refreshEventTasksTable();
        } else {
            refreshDataflowTasksTable();
        }
    });
    return xhr
}

function setupEventTaskRegistration() {
    var $form = $('#eventTaskRegistrationForm');
    var $eventTypeInput = $('#eventTypeInput');
    var $submitBtn = $('#eventTaskRegistrationSubmitBtn');
    var $modalDialog = $('#eventTaskRegistrationModal');

    $form.submit(function(event) {
        console.log("Event task registration form is submitted.");
        event.preventDefault();
    });

    $submitBtn.click(function() {
        var task = {};
        console.log('task registration submit button is clicked.');
        task.task_name = $('#taskNameInput').val();
        task.cmd_args = $('#cmdArgsInput').val();
        task.event = {};
        task.event.name = $eventTypeInput.find('option:selected').val();
        if (task.event.name === EventType.PeriodicTimeEvent) {
            task.event.period = parseInt($('#periodicTimeInput').val());
        }
        if (task.event.name === EventType.OneShotTimeEvent) {
            task.event.after = parseInt($('#oneShotTimeInput').val());
        }

        var jobName = getCurrentJobNameFromTable();
        console.log('Task is ', task);
        console.log('Current job name: %s', jobName);
        var xhr = registerTask(jobName, task, TaskType.EventTask);
        xhr.always(function(data) {
            console.log('I am hiding modal dialog');
            $modalDialog.modal('hide');
        });
    });

    var $oneShotTimeFormGroup = $('#oneShotTimeFormGroup');
    var $periodicTimeFormGroup = $('#periodicTimeFormGroup');
    $eventTypeInput.change(function() {
        var eventType = $eventTypeInput.find('option:selected').val();
        console.log('Selected Event Type: %s', eventType);
        switch (eventType) {
            case EventType.OneShotTimeEvent:
                $oneShotTimeFormGroup.show();
                $periodicTimeFormGroup.hide();
                break;
            case EventType.PeriodicTimeEvent:
                $periodicTimeFormGroup.show();
                $oneShotTimeFormGroup.hide();
                break;
            default:
                $periodicTimeFormGroup.hide();
                $oneShotTimeFormGroup.hide();
        }
    });
}

function setupDataflowTaskRegistration() {
    var $form = $('#dataflowTaskRegistrationForm');
    var $submitBtn = $('#dataflowTaskRegistrationSubmitBtn');
    var $modalDialog = $('#dataflowTaskRegistrationModal');

    $submitBtn.click(function() {
        console.log('Submit button is clicked for dataflow task registration.');
        var task = {};
        task.task_name = $('#dataflowTaskNameInput').val();
        task.cmd_args = $('#dataflowCmdArgsInput').val();
        task.input_size = parseInt($('#dataflowTaskInputSizeInput').val());
        task.condition = $.parseJSON($('#dataflowTaskConditionTextArea').val());

        var jobName = getCurrentJobNameFromTable();
        console.log('Task is ', task);
        console.log('Current job name: %s', jobName);
        var xhr = registerTask(jobName, task, TaskType.DataflowTask);
        xhr.always(function(data) {
            console.log('I am hiding modal dialog');
            $modalDialog.modal('hide');
        });
    });
}


function setupTasksRegistration() {
    setupEventTaskRegistration();
    setupDataflowTaskRegistration();
}
