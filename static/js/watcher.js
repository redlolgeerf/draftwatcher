$(document).ready(function() {
    $('#addbtn').click(function(){
        $("#addbtn").html('Пожалуйста, подождите')
});
    $('#addbtn2').click(function(){
        $("#addbtn2").html('Пожалуйста, подождите')
});
    $('#editcomment').click(function(){
        $('#id_comment').prop("disabled", false);
        var r= $('<button id="add_comment" class="btn btn-xs btn-primary" type="submit" name="submit">Сохранить</button>');
        $("#add_comment_form").append(r);
        $('#editcomment').hide();
        
});
});
