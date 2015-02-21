function exportJobs(){
	window.location.href = "/export/" + getCurrentJobNameFromTable();
}

function setupExportImport(){
	$('#exportJobBtn').on('click', exportJobs);
	$('#importJobBtn').fileupload({
		url: '/import',
        dataType: 'json',
        submit: function (e, data) {
        	var filename = data.files[0].name;
		    $.blockUI({ message: '<h1>Importing ' + filename + ' ...</h1>' });
		},
        done: function (e, data, textStatus) {
        	$.unblockUI();
        	refreshJobs();
        	var err = data.result["error"];
            alert(err == null? "Import succeeded." : err);
        },
        fail: function(e, data, textStatus) {
        	$.unblockUI();
        	alert("Upload failed: " + data.textStatus)	
        }
    });
}