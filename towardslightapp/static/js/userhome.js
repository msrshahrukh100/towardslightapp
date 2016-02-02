
 $("#preloader").hide();
  $("#preloader1").hide();


$(function(){

    
    
    var $username=$('.username');
        var $useremail=$('.useremail');
		 var $workinfo = $('.workinfo');
			 var $areaofinterest = $('.areaofinterest');
		 var $hobbies = $('.hobbies');
		 var $skills = $('.skills');
        var $post = $('#postbyyou');

        $.ajax({
            url: '/getallinfo',
            type: 'GET',
            success: function(data){
            
              $('.profilepic').attr('src','static/Uploads/'+data.ppic); 
              if(data.lname){
              $username.append(data.fname +' '+data.lname);
                  }
                  else
                    {$username.append(data.fname );}
              $useremail.append(data.email);
              $('.profilepic').attr('src','static/Uploads/'+data.ppic); 
              if(data.atype)
              {
              	if(data.institute)
              	{
              		$workinfo.append(" <i class='material-icons left'>class</i>"
+data.atype+" at "+data.institute);  

              	}
              }

              if(data.areaoint)
              	{$areaofinterest.append(" <i class='material-icons left'>subtitles</i>My areas of interest are "+data.areaoint);}
              if(data.hobby)
              	{$hobbies.append(" <i class='material-icons left'>perm_camera_mic</i> My hobbies are "+data.hobby);}

				if(data.skills)
              	{$skills.append(" <i class='material-icons left'>stars</i>My Skills are "+data.skills);}
                          }
        });
  





////////////////////////////////////////////////for the posts

        $.ajax({
            url: '/getallposts',
            type: 'GET',
            success: function(data){
              var obj = JSON.parse(data);
      $("#preloader").fadeOut(300).hide();
      $("#preloader1").fadeOut(300).hide();

$.each(obj, function(index, value) {

if(value.posttype === 'Sprituality'){
  $post.append('<li class="collection-item avatar"><i class="material-icons circle green ">grade</i><span class="title">'+value.mtitle+'</span><p>'+value.posttype+'<br>Published on '+value.date+'</p><a href="/editdpost/'+value.mid+'" class="secondary-content"><i class="material-icons" style="padding-right:35px">mode_edit</i></a><a href="/showpost/'+value.mid+'" class="secondary-content"><i class="material-icons">library_books</i></a></li>');
       }


if(value.posttype === "Political"){
  $post.append('<li class="collection-item avatar"><i class="material-icons circle pink">language</i><span class="title">'+value.mtitle+'</span><p>'+value.posttype+'<br>Published on '+value.date+'</p><a href="/editdpost/'+value.mid+'" class="secondary-content"><i class="material-icons" style="padding-right:35px">mode_edit</i></a><a href="/showpost/'+value.mid+'" class="secondary-content"><i class="material-icons">library_books</i></a></li>');
       }


if(value.posttype === "Socio-economic"){
  $post.append('<li class="collection-item avatar"><i class="material-icons circle red">person_pin</i><span class="title">'+value.mtitle+'</span><p>'+value.posttype+'<br>Published on '+value.date+'</p><a href="/editdpost/'+value.mid+'" class="secondary-content"><i class="material-icons" style="padding-right:35px">mode_edit</i></a><a href="/showpost/'+value.mid+'" class="secondary-content"><i class="material-icons">library_books</i></a></li>');
       }


if(value.posttype === "Life Style"){
  $post.append('<li class="collection-item avatar"><i class="material-icons circle blue">loyalty</i><span class="title">'+value.mtitle+'</span><p>'+value.posttype+'<br>Published on '+value.date+'</p><a href="/editdpost/'+value.mid+'" class="secondary-content"><i class="material-icons" style="padding-right:35px">mode_edit</i></a><a href="/showpost/'+value.mid+'" class="secondary-content"><i class="material-icons">library_books</i></a></li>');
       }


        
   });

                          }
        });
  



$nomessages=$('#nomessages');
$nomessagesmob=$('#nomessagesmob');

$.ajax({

  url:'/getunseenmsg',
  type:'GET',
  success:function(data){
    $nomessages.append(data.msg);
    $nomessagesmob.append(data.msg);

  }

});


});
