 $("#preloader").hide();
 $("#preloader1").hide();
 $("#preloader4").hide();
 $("#preloader5").hide();


$(function(){   
    var $uploadedimage = $('.uploadedimage'); 
    var $messageln=$('.messageln');

    var $iderror=$('.iderror');
    var $perror=$('.perror');

    var $success=$('.success');
  

    $('.btnSignIn').click(function(){
            

        $.ajax({
            url: '/validateLogin',
            data: $('form').serialize(),
            type: 'POST',
            success: function(data){

            $messageln.empty();

              if(data.msg)
              {$messageln.append('<li>'+data.msg+'</li>');}
          else
                {window.location="/userhome";}


                          }
        });
    });






$('#frontSignUp').click(function(){

     $("#preloader").show();
        $.ajax({
            url: '/fsignup',
            data: $('form').serialize(),
            type: 'POST',
            success: function(data){
                 $("#preloader").fadeOut(300).hide();
                $iderror.empty();
                $perror.empty();
                $success.empty();

                 if(data.perror)
                 {
                    $perror.append('<li>'+data.perror+'</li>');
                 }
                if(data.ierror)
                {
                    $iderror.append('<li>'+data.ierror+'</li>');
                }
                    if (data.success)
                    {
                        $success.append('<li>'+data.success+'</li>');
                    }
                   
            }
        });
    });


$('#btnfp').click(function(){
         $("#preloader1").show();
        $.ajax({
            url: '/forgotpw',
            data: $('form').serialize(),
            type: 'POST',
            success: function(data){
                    $("#preloader1").fadeOut(300).hide();
                   $messageln.empty();
           $messageln.append('<li>'+data.msg+'</li>');
                
                   
            }
        });
    });





$('#getconfirmationcode').click(function(){
         $("#preloader4").show();
        $.ajax({
            url: '/getconfirmationcode',
            data: $('form').serialize(),
            type: 'POST',
            success: function(data){
                    $("#preloader4").fadeOut(300).hide();
                   $messageln.empty();
           $messageln.append('<li>'+data.msg+'</li>');
                
                   
            }
        });
    });




//for the uploading pic


$('#upload').submit( function(e) {
    e.preventDefault();
         $("#preloader5").show();

    var data = new FormData(this); // <-- 'this' is your form element

    $.ajax({
            url: '/upload',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST',     
            success: function(data){
             $("#preloader5").fadeOut(300).hide();

            //console.log(path);
            //$uploadedimage.append(' ');

           $('#imgUpload').attr('src','static/Uploads/'+data.imagepath);

        }
    });
    });












});