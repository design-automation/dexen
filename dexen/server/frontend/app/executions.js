var curExecutions = null;

function showMoreExecutions(rowNo, key){
	if(curExecutions == null || curExecutions.length <= rowNo){
		console.log("Current execution records do not have row " + rowNo);
        return;
    }
    $("#showMoreModal .modal-header h4").html(escapeHtml(key));
    $("#showMoreModal #showMoreModalContent").html(escapeHtml(curExecutions[rowNo][key]));
    $("#showMoreModal").modal();
}

function executionsTableRenderFunction(localKey){
	var MAX_CHARS = 160;
	return function(data, type, row, meta){
		if(!row.hasOwnProperty(localKey))
			return "";

		var cellData = row[localKey];

		if(type == "display"){
			cellData = String(cellData);
			if(cellData.length > MAX_CHARS){
				cellData = cellData.substring(0, MAX_CHARS);
				return escapeHtml(cellData) + "&hellip;" +
						" <a href='javascript:void(0)' onclick='showMoreExecutions(" + meta.row + ", \"" + localKey + "\");'>More</a>";
			}
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

	var ajaxUrl = '/executions/' + jobName;
	console.log('Loading executions table from ' + ajaxUrl);

	var table = $('#executionsTable').DataTable();
	table
		.clear()
		.draw();

	$.ajax({
        type: "GET",
        url: ajaxUrl,
        dataType: "json",
        success: function (data) {
        	curExecutions = data.executions;
			table
				.rows.add(data.executions)
				.draw();
		},
		error: function (jqXHR, textStatus, errorThrown) {
        	alert("Unable to get executions. Status: " + textStatus);
        }
	});
}

function setupExecutionsTable() {
	var $table = $('#executionsTable');
	$table.dataTable({
    	"data": [],
    	"columns": [
			{ "title" : "ID"			,	"data": null   ,   "render" : executionsTableRenderFunction("execution_id") },
			{ "title" : "Task" 	        ,	"data": null   ,   "render" : executionsTableRenderFunction("task_name") },
			{ "title" : "Worker"	    ,	"data": null   ,   "render" : executionsTableRenderFunction("worker_name") },
			{ "title" : "Creation Time"	,	"data": null   ,   "render" : executionsTableRenderFunction("creation_time") },
			{ "title" : "Begin Time"	,	"data": null   ,   "render" : executionsTableRenderFunction("begin_time") },
			{ "title" : "End Time"		,	"data": null   ,   "render" : executionsTableRenderFunction("end_time") },
			{ "title" : "Status"		,	"data": null   ,   "render" : executionsTableRenderFunction("status") },
			{ "title" : "Stdout"		,	"data": null   ,   "render" : executionsTableRenderFunction("stdout") },
			{ "title" : "Stderr"		,	"data": null   ,   "render" : executionsTableRenderFunction("stderr") }
		]
    });	   

    var $refreshBtn = $('#refreshExecutionsTableBtn');
    $refreshBtn.on("click", refreshExecutionsTable);
}
