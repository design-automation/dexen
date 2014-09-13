function refreshExecutionsTable() {
	var jobName = getCurrentJobNameFromTable();
	if(!jobName){
		alert('There is no job selected');
		return;
	}

	var $table = $('#executionsTable');
	var ajaxUrl = '/executions/' + jobName;
	console.log('Loading executions table from ' + ajaxUrl);
	if($.fn.dataTable.isDataTable($table) ) {		
		$table.DataTable().ajax.url(ajaxUrl).load();
	} else{
		$table.dataTable({
	    	"ajax": {		    
			    "dataSrc": "executions",
			    "url": ajaxUrl
			},
	        "columns": [
				{ "title" : "ID"			,	"data": "execution_id" },
				{ "title" : "Task Name" 	,	"data": "task_name" },
				{ "title" : "WorkerName"	,	"data": "worker_name" },
				{ "title" : "Creation Time"	,	"data": "creation_time" },
				{ "title" : "Begin Time"	,	"data": "begin_time" },
				{ "title" : "End Time"		,	"data": "end_time" },
				{ "title" : "Status"		,	"data": "status" },
				{ "title" : "Stdout"		,	"data": "stdout" },
				{ "title" : "Stderr"		,	"data": "stderr" }
			]
	    });	    
	}
}

function setupExecutionsTable() {
    var $refreshBtn = $('#refreshExecutionsTableBtn');

    $refreshBtn.on("click", refreshExecutionsTable);
}
