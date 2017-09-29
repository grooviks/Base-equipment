$( '.input' ).on('blur keyup',  function(event){


            var id = $(this).attr("id");
            var name = $(this).attr("name");
            var val = $(this).val();

            if(event.keyCode==13){
                $(event.target).parents('td').next().find('.input').first().focus();
                event.preventDefault();
            }
            
            if (id.indexOf("numb") + 1) { //если id поле ввода номера то проверяем на ввод числа
                if (this.value.match(/[^0-9]/g)) {
                        //this.value = this.value.replace(/[^0-9]/g, '');
                        this.value = '';
                        return ;
                }
            }


            $.ajax({
                type: "POST",
                url: "/edit_device",
                data: { 'id' :  id , 'name' : name, 'value' : val},
                type: 'POST',
                success: function(response) {
                    //var json = jQuery.parseJSON(response)
                    //$(id).html(json.resp)
                    console.log(response);
                },
                error: function(error) {
                    console.log(error);
            }
        });
});

