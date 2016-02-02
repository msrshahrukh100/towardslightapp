$(function(){
	$('.modal-trigger').leanModal();
  $('.materialboxed').materialbox();
      

 $('select').material_select();

$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 80 // Creates a dropdown of 15 years to control year
  });


	var $com = $('#comments');

	$('#btnSignUp').click(function(){
		
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});

$('#btnaddpost').click(function(){
	$messageadded = $('.messageadded');
		
		$.ajax({
			url: '/addpost',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				if(response.message)
				{


				$messageadded.append(response.message+'<br>');
				}
				else
				{
					$messageadded.append('Please fill all entries'+'<br>');
				}

				},
			error: function(error){
				console.log(error);
			}
		});
	});








	 $('#textarea1').val('New Text');
  $('#textarea1').trigger('autoresize');
});
