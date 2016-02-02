$(document).ready(function(){
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal-trigger').leanModal();

      $(".button-collapse").sideNav();




      $(function(){
			    $('#fileupload').fileupload({
        			url: 'upload',
        			dataType: 'json',
        			add: function (e, data) {
        				data.submit();
        			},
			        success:function(response,status) {
					console.log(response.filename);
					var filePath = 'static/Uploads/' + response.filename;
					$('#imgUpload').attr('src',filePath);
					$('#filePath').val(filePath);
			        	console.log('success');
			        },
			        error:function(error){
			        	console.log(error);
			        }
    			});
		})

      
  });


