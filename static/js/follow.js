$(function(){
    $('#follow').click(function() {
    	name = $(this).text();
        $.ajax({
        	type: "POST",
			url: "/followPlayer",
			data: {
            	'player' : String(window.location)
            },
            dataType: "json",
            success: function(data){
        		$("#followSuccess").append('<div class="alert alert-success">' + "Successfully following " + name + "</div>");
	        },
	        error: function(error){
	            console.log(error);
        	}
        });
    });
});