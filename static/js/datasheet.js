var csrftoken = Cookies.get('csrftoken');

// ajax csrf
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
    var target_form;
    $('.datasheet_file_operation').click(function(e) {
        e.preventDefault();
        target_form = '#' + $(e.target).attr('id');
        $('.datasheet_upload_form').filter(target_form).submit();
    });

    $('.datasheet_upload_form').submit(function() {
        var formData = new FormData(this);
        formData.append('datasheet_hash_pid', $(this).attr('id'));
        $.ajax({
            url: upload_datasheet_file_url,
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,
            processData: false
        }).done(function(rec_json) {
            var err = rec_json['error_message'],
                datasheet_file_name = rec_json['xldatasheet_file_name'];
            $('.datasheet_file').filter(target_form).val('');
            if (err) {
                $('.datasheet_file_upload_message').filter(target_form).text(err);
            } else {
                $('.datasheet_file_upload_message').filter(target_form).text(datasheet_file_name + ' was uploaded.');
            }
        });
        return false;
    });

});