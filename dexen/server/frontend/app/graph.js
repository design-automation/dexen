function setupGraph(){
	var $graphPane = $("#graphPane");
    var $eddexFrame = $("<iframe>/")
                                .attr("src", "eddex/index.html")
                                .attr("id", "eddexFrame")
                                .attr("width", "100%")
                                .attr("scrolling", "no")
                                .attr("frameBorder", "0");
    $graphPane.empty();
    $graphPane.append($eddexFrame);
    $eddexFrame.iFrameResize({
        "initCallback" : function(){
        }
    });
}

function refreshGraph(){
	var jobName = getCurrentJobNameFromTable();
	if(!jobName){
		alert('There is no job selected');
		return;
	}

	var eddexFrame = $("#eddexFrame").get(0);
	if(eddexFrame == null || eddexFrame.contentWindow == null){
		alert("Unable to get the graph iframe");
		return;
	}

	eddexFrame.contentWindow.postMessage("[DexenJob]" + jobName, "*");	
}