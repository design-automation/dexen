/**
 * Created by kafkef on 6/4/14.
 */


function getSelectedRow($table) {
    return $table.find('tr.row-selected');
}

function selectRow($tr){
    $tr.addClass('row-selected');
}

function getDataFromSelectedRow($table, colIndex) {
    var $tr = getSelectedRow($table);
    var $td = $tr.children().eq(colIndex);
    console.log("Selected data at column %d is %s", colIndex, $td.text());
    return $td.text();
}

function setupTable($table, fnSelectedCallback) {
    $table.find('tbody').click(function(event) {
        if($.fn.dataTable.isDataTable($table)){
            if($table.DataTable().rows().data().length > 0){
                console.log('Event target %s', event.target);
                var $td = $(event.target);
                $table.find('tr.row-selected').removeClass('row-selected');
                var $tr = $td.parent('tr');
                $tr.addClass('row-selected');
                fnSelectedCallback($tr);
            }
        }
    });
}