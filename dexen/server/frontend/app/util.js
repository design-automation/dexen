/**
 * Created by kafkef on 6/4/14.
 */


function timestampToDateString(secondsSinceEpoch) {
    if (secondsSinceEpoch === null) {
        return '';
    }
    return new Date(secondsSinceEpoch*1000).toLocaleString();
}

