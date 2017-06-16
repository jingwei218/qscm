$(document).ready(function () {
    // ajax csrf
    var csrftoken = Cookies.get('csrftoken');
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
    $('#save_n_create_scheme').click(function(e){
        e.preventDefault();
        var scheme_settings = new Array(),
            scheme_name = $('.scheme_name').text();
        $('.scheme_setting').each(function(i, element) {
            var setting_pid = $(element).find('.setting_name').attr('id'),
                scheme_setting_value = $(element).find('.scheme_setting_value').text();
            scheme_settings[scheme_settings.length] = {
                "setting_pid": setting_pid,
                "scheme_setting_value": scheme_setting_value
            }
        });
        scheme_meta = {
            "scheme_name": scheme_name,
            "scheme_settings": scheme_settings
        }
        pjson = JSON.stringify(scheme_meta);
        $.ajax({
            url: ajax_url,
            dataType: "json",
            method: "POST",
            data: pjson,
        }).done(function(json) {
            var scheme_pid = json['scheme_pid'],
                msg = "Scheme " + scheme_pid + " was created.";
            $('#scheme_caption').html(msg);
        })
    });

    $('#edit_box').css({
        width: 0,
        height: 0,
        position: "absolute"
    }).blur(function(e){
        if ($('.edited').data("type") == "checkbox") {
            var checked = $(this).prop('checked');
            $('.edited').text(checked);
        } else {
            $('.edited').text($('#edit_box').val());
        }
        $(this).val('').hide();
    });

    $('.editable').click(function(e) {
        e.preventDefault();
        var box_width = $(this).outerWidth(),
            box_height = $(this).outerHeight(),
            box_left = $(this).offset().left,
            box_top = $(this).offset().top,
            edited_value = $(this).text();
            edit_type = $(this).data("type");
        $('.edited').removeClass("edited");
        $(this).addClass("edited");

        $('#edit_box').show()
        .attr("type", edit_type)
        .offset({
            left: box_left,
            top: box_top
        });
        if (edit_type == "checkbox") {
            $('#edit_box').css({
                width: box_height,
                height: box_height,
                borderRadius: "1 1 1 1"
            });
            $('.edited').text('');
        } else {
            $('#edit_box').css({
                width: box_width,
                height: box_height,
                borderRadius: "1 1 1 1"
            });
        }
        $('#edit_box').focus().val(edited_value).select();
    });
});