$.function({
var $orders = $('#orders');
var	$name = $('#name');
var	$drink = $('#drink');

	var ordertemplate = "<li><strong>{{name}}</strong></li>"+"<button data-id={{id}}></button>"
	function addorder(order){
		$orders.append(Mustache.render(ordertemplate,order ));
	}

	$.ajax({
		url : '/posts',
		type: 'GET',
		success : function(orders){
			$.each(orders,function(i,order))
			{
				 addorder(order)
			}
		error: function(){
			alert('Error loading oredes')
		}
		}

	});
$('#addorder').on('click',function(){
var order={
	name=$name.val();
	drink=$drink.val();
};

$.ajax({
	type:'POST',
	usl:'addorder',
	data: order
	success: function(neworders){
			$.each(neworders,function(i,neworder))
			{
				$orders.append('<li>'+ neworder.name+'</li>'); 
			}}
	error:


});

$orders.delegate('.remove ','click',function(){
var $li=$(this).closes('li');
$.ajax({
type:'DELETE',
url:'api/orders/'+$(this).attr('data-id'),
success:function(){
$li.remove();
}

});

});

});






});