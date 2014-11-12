function exportJobs(){
	window.location.href = "/export/" + getCurrentJobNameFromTable();
}

function importJobs(){

}

function setupExportImport(){
	$('#exportJobBtn').on('click', exportJobs);
	$('#importJobBtn').on('click', importJobs);
}