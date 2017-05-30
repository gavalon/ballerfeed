$(document).ready(function(){
	$('#search').keyup(function(){
		value = $(this).val();
		$.ajax({
			type: "POST",
			url: "/getPlayers",
			data: {
            	'search_keyword' : value
            },
            dataType: "json",
            success: function(data){
            	$("#results").empty();
            	for (var key in data) {
					if (data.hasOwnProperty(key)) {
						player_name = data[key];
						$("#results").append('<p><a href="/player/' + key   + '">' + player_name + "</a></p>");
				  	}
				}
            },
            error: function(error){
            	console.log(error);
            }
		});
	});

});