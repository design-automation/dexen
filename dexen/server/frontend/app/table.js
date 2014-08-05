/**
 * Created by kafkef on 6/4/14.
 */




function getDataFromSelectedRow($table, colIndex) {
    var $tr = $table.find('tr.row-selected');
    var $td = $tr.children().eq(colIndex);
    console.log("Selected data at column %d is %s", colIndex, $td.text());
    return $td.text();
}

function setupTable($table, fnSelectedCallback) {
    $table.find('tbody').click(function(event) {
        console.log('Event target %s', event.target);
        var $td = $(event.target);
        $table.find('tr.row-selected').removeClass('row-selected');
        var $tr = $td.parent('tr');
        $tr.addClass('row-selected');
        fnSelectedCallback($tr);
    });
}