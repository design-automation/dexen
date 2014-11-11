function exportJobs(){
	window.location.href = "/export"
}

function importJobs(){

}

function setupExportImport(){
	$('#exportJobBtn').on('click', exportJobs);
	$('#importJobBtn').on('click', importJobs);
}