function refreshJobDataTable() {
	var jobName = getCurrentJobNameFromTable();
	if(!jobName){
		alert('There is no job selected');
		return;
	}

	var ajaxUrl = '/data/' + jobName;
	console.log('Loading job data from ' + ajaxUrl);
	$.ajax({
        type: "GET",
        url: ajaxUrl,
        dataType: "json",
        success: function (data) {
        	var DATA_ID = "_id";
        	var BINARY_KEYS = "keys";

        	var attrSet = {};
        	var attrList = [];
        	var columns = [];
        	for(i=0; i<data.data.length; ++i){
        		$.each(data.data[i], function(key) {
        			if(!attrSet.hasOwnProperty(key)){
        				attrSet[key] = true;
        				attrList.push(key);
        				columns.push({"title" : key, "data" : key});
        			}
        		});

        		var metadata = data.metadata[i];
        		if(metadata.hasOwnProperty(BINARY_KEYS) && metadata.hasOwnProperty(DATA_ID)){
        			var dataId = metadata[DATA_ID];
        			var binaryKeys = metadata[BINARY_KEYS];
        			for(j=0; j<binaryKeys.length; ++j){
        				var url = "/data/" + encodeURIComponent(jobName) + "/" + encodeURIComponent(dataId) + "/" + encodeURIComponent(binaryKeys[j]);
						data.data[i][binaryKeys[j]] = "<a href='" + url + "'>Download</a>";
        			}
        		}
        	}

        	var $table = $('#jobDataTable');
        	if ( $.fn.dataTable.isDataTable($table) ) {
			    $table.DataTable().destroy();
			}

        	$table.dataTable({
        		"data" : data.data,
        		"columns" : columns,
        		"dom": 'RC<"clear">lfrtip'
        	});

        },
        error: function (jqXHR, textStatus, errorThrown) {
        	alert("Unable to get job data. Status: " + textStatus);
        }
    })
}

function setupJobDataTable() {
    var $refreshBtn = $('#refreshJobDataTableBtn');

    $refreshBtn.on("click", refreshJobDataTable);
}
