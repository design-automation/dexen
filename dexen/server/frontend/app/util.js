/**
 * Created by kafkef on 6/4/14.
 */


function timestampToDateString(secondsSinceEpoch) {
    if (secondsSinceEpoch === null) {
        return '';
    }
    return new Date(secondsSinceEpoch*1000).toLocaleString();
}

var entityMap = {
	"&": "&amp;",
	"<": "&lt;",
	">": "&gt;",
	'"': '&quot;',
	"'": '&#39;',
	"/": '&#x2F;'
};

function escapeHtml(string) {
	return String(string).replace(/[&<>"'\/]/g, function (s) {
		return entityMap[s];
	});
}