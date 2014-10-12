function createDefaultJobDataTableDefinition() {
    return {    
                "data" : [],
                "columns" : [{"title" : "_id", "data" : "_id"}],
                "dom": 'RC<"clear">lfrtip'
            };
}

function createJobDataTable(definition) {
    var $table = $('#jobDataTable');
    if ( $.fn.dataTable.isDataTable($table) ) {
        $table.DataTable().destroy();
        $table.empty();
    }
    $table.dataTable(definition);
}

var curDataObjects = null;
var columnKeys = null;

function showMore(rowNo, colNo){
    if(curDataObjects == null || curDataObjects.data.length <= rowNo 
        || columnKeys == null || columnKeys.length <= colNo){
        console.log("Current data objects do not have row " + rowNo + " and col " + colNo);
        return;
    }
    var key = columnKeys[colNo];
    $("#showMoreModal .modal-header h4").html(escapeHtml(key));
    $("#showMoreModal #showMoreModalContent").html(escapeHtml(curDataObjects.data[rowNo][key]));
    $("#showMoreModal").modal();
}

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
            curDataObjects = data;
        	var DATA_ID = "_id";
        	var BINARY_KEYS = "keys";

        	var attrSet = {};
        	var columns = [];
            columnKeys = [];
        	for(i=0; i<data.data.length; ++i){
        		$.each(data.data[i], function(key, item) {
        			if(!attrSet.hasOwnProperty(key)){
        				attrSet[key] = true;
                        columnKeys.push(key);
        				columns.push(
        					{	"title" : escapeHtml(key), 
        						"data" : null, 
        						"render" : (function(localKey){
                                                var MAX_CHARS = 160;
        										return function(allData, type, row, meta){
                                                    var cellData = row[localKey];
                                                    if(cellData == null)
                                                        return "";
                                                    
        											if(type == "display"){
                                                        if(typeof(cellData) == "string"){									
            												var metadata = data.metadata[meta.row];
    										        		if(metadata.hasOwnProperty(BINARY_KEYS) && metadata.hasOwnProperty(DATA_ID)){
    										        			if(metadata[BINARY_KEYS].indexOf(localKey) != -1){
    										        				var dataId = metadata[DATA_ID];										        			
    										        				var url = "/data/" + encodeURIComponent(jobName) + "/" + encodeURIComponent(dataId) + "/" + encodeURIComponent(localKey);
    																return "<a href='" + url + "'>Download</a>";
    										        			}										        			
    										        		}
                                                        }else{
                                                            cellData = String(cellData);
                                                        }
                                                        if(cellData.length > MAX_CHARS){
                                                            return escapeHtml(cellData.substring(0, MAX_CHARS)) + "&hellip;" + 
                                                                    " <a href='javascript:void(0)' onclick='showMore(" + meta.row + ", " + meta.col + ");'>More</a>";
                                                        }
										        		return escapeHtml(cellData);
        											}

        											return cellData;
        										};
        									})(key)
        				});
        			}
        		});
        	}

            var definition = null;

        	if(columns.length > 0){
            	definition =   {
                        		  "data" : data.data,
                        		  "columns" : columns,
                        		  "dom": 'RC<"clear">lfrtip'
                        	   };
            } else{
                definition = createDefaultJobDataTableDefinition();
            }

            createJobDataTable(definition);

        },
        error: function (jqXHR, textStatus, errorThrown) {
        	alert("Unable to get job data. Status: " + textStatus);
            createJobDataTable(createDefaultJobDataTableDefinition());
        }
    })
}

function setupJobDataTable() {
    var $refreshBtn = $('#refreshJobDataTableBtn');

    $refreshBtn.on("click", refreshJobDataTable);
}
