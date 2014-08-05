/**
 * Created by kafkef on 5/4/14.
 */



var JobFilesTableColIndex = {
    FileName: 0,
    UploadTime: 1,
    Size: 2
};

function getCurrentFileNameFromTable() {
    var $jobFilesTable = $('#jobFilesTable');
    return getDataFromSelectedRow($jobFilesTable, JobFilesTableColIndex.FileName);
}

function uploadFile() {
    var $filePathInput = $('#filePathInput');
    var uploadURL = '/upload_file/' + getCurrentJobNameFromTable();
    var $uploadsArea = $('#uploadsArea');
    var $uploadEntry = $('.upload-entry');

    $filePathInput.fileupload({
        url: uploadURL,
        dataType: 'json',
        //singleFileUploads: true,
        autoUpload: false,
        done: function (e, data) {
            console.log('file upload done.');
            $.each(data.result.files, function (index, file) {
                console.log("file %s has been uploaded", file);
            });
        },
        fail: function(e, data) {
            console.log(e);
            console.log(data);
        },
        add: function(e, data) {
            var fileName = data.files[0].name;
            var $entry = $uploadEntry.clone().appendTo($uploadsArea);
            data.context = $entry;
            $entry.find('label').text(fileName);
            $entry.find('button').click(function() {
                console.log('Upload button is clicked submitting data...');
                data.submit();
            });
            $entry.show();
        },
        progress: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var $entry = data.context;
            $entry.find('.progress-bar').css('width', progress + '%');
        }
    });
}


function updateJobFilesTable(files) {
    var $jobFilesTable = $('#jobFilesTable');
    console.log('Updating jobs', files);
    $jobFilesTable.dataTable().fnClearTable();
    $.each(files, function(index, file) {
        file['upload_time'] = timestampToDateString(file['upload_time']);
    });
    $jobFilesTable.dataTable().fnAddData(files);
}

function setupFilesTable() {
    var $jobFilesTable = $('#jobFilesTable');
    var $downloadJobFileBtn = $('#downloadJobFileBtn');
    var $uploadJobFileBtn = $('#uploadJobFileBtn');
    var $fileUploadModal = $('#fileUploadModal');
    var $uploadsArea = $('#uploadsArea');
    var $refreshJobFilesBtn = $('#refreshJobFilesBtn');

    $jobFilesTable.dataTable( {
        bPaginate: false,
        bInfo: false,
        bSearchable: false,
        bFilter: false,
        aoColumns: [
            {sTitle: 'Name', mData: 'file_name'},
            {sTitle: 'Upload Time', mData: 'upload_time'},
            {sTitle: 'Size', mData: 'size'},
        ]
    });

    setupTable($jobFilesTable, function($tr) {
        console.log('job files table row selected callback.');
    });

    $downloadJobFileBtn.click(function() {
        var jobName = getCurrentJobNameFromTable();
        var fileName = getCurrentFileNameFromTable();
        window.location = "/download_file/" + jobName + "/" + fileName;
    });

    $uploadJobFileBtn.click(function() {
        $uploadsArea.children().not(':first').remove();
        uploadFile();
        $fileUploadModal.modal();
    });

    $refreshJobFilesBtn.click(function() {
        var url = '/files_metadata/' + getCurrentJobNameFromTable();
        var xhr = $.getJSON(url);
        xhr.done(function(data) {
            console.log('refresh files are done: ', data.files_metadata);
        });
    });
}
