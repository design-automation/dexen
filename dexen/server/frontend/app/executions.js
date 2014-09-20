function executionsTableRenderFunction(key){
	var localKey = key;
	return function(data, type, row, meta){
		if(!row.hasOwnProperty(localKey))
			return "";

		var cellData = row[localKey];

		if(type == "display" && typeof(cellData) == "string"){
			return escapeHtml(cellData);
		}

		return cellData;
	};
}

function refreshExecutionsTable() {
	var jobName = getCurrentJobNameFromTable();
	if(!jobName){
		alert('There is no job selected');
		return;
	}

	var $table = $('#executionsTable');
	var ajaxUrl = '/executions/' + jobName;
	console.log('Loading executions table from ' + ajaxUrl);

	$.ajax({
        type: "GET",
        url: ajaxUrl,
        dataType: "json",
        success: function (data) {
			if($.fn.dataTable.isDataTable($table) ) 		
				$table.DataTable().destroy();

			$table.dataTable({
		    	"data": data.executions,
		    	"columns": [
					{ "title" : "ID"			,	"data": null   ,   "render" : executionsTableRenderFunction("execution_id") },
					{ "title" : "Task Name" 	,	"data": null   ,   "render" : executionsTableRenderFunction("task_name") },
					{ "title" : "WorkerName"	,	"data": null   ,   "render" : executionsTableRenderFunction("worker_name") },
					{ "title" : "Creation Time"	,	"data": null   ,   "render" : executionsTableRenderFunction("creation_time") },
					{ "title" : "Begin Time"	,	"data": null   ,   "render" : executionsTableRenderFunction("begin_time") },
					{ "title" : "End Time"		,	"data": null   ,   "render" : executionsTableRenderFunction("end_time") },
					{ "title" : "Status"		,	"data": null   ,   "render" : executionsTableRenderFunction("status") },
					{ "title" : "Stdout"		,	"data": null   ,   "render" : executionsTableRenderFunction("stdout") },
					{ "title" : "Stderr"		,	"data": null   ,   "render" : executionsTableRenderFunction("stderr") }
				]
		    });	    
		
		}
	});
}

function setupExecutionsTable() {
    var $refreshBtn = $('#refreshExecutionsTableBtn');

    $refreshBtn.on("click", refreshExecutionsTable);
}
