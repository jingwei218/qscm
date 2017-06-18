function editOn() {
    //可编辑字段点击事件
    $('.editable').click(function (e) {
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
            });
            $('.edited').css({'visibility': 'hidden'});
        } else {
            $('#edit_box').css({
                width: box_width,
                height: box_height,
            });
        }
        $('#edit_box').focus().val(edited_value).select();
    });
}

function schemeJson(mode) {
    var scheme_settings = new Array(),
        scheme_name = $('.scheme_name').text(),
        scheme_pid = 0;
    $('.scheme_setting').each(function (i, element) {
        var setting_pid = $(element).find('.setting_name').attr('id'), //设置项的pid号
            scheme_setting_value = $(element).find('.scheme_setting_value').text(); //设置项的值

        scheme_settings[scheme_settings.length] = { //在设置列表的最后添加设置项
            "setting_pid": setting_pid,
            "scheme_setting_value": scheme_setting_value
        }
    });
    //项目的元数据
    scheme_meta = {
        "scheme_pid": scheme_pid,
        "scheme_name": scheme_name,
        "scheme_settings": scheme_settings,
        "mode": mode
    }

    //将元数据转换为json
    scheme_meta_json = JSON.stringify(scheme_meta);
    //发送异步数据到后台
    $.ajax({
        url: ajax_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function (rec_json) { //ajax发送成功后获得后台发送的反馈信息
        var scheme_pid = rec_json['scheme_pid'],
            err = rec_json['error_message'],
            msg_create = "Scheme " + scheme_pid + " was created.",
            msg_update = "Scheme " + scheme_pid + " was updated."
        if (err) { //若有收到后台错误信息，显示错误信息；否则显示生成信息
            $('#scheme_caption').html(err);
        } else {
            if (mode == 'create') {
                $('#scheme_caption').html(msg_create);
                $('#edit_scheme_settings').show();
                $('#create_scheme').hide();
            } else if (mode == 'update') {
                $('#scheme_caption').html(msg_update);
                $('#cancel_scheme_edit').hide();
            }
            $('.editable').off('click');  //保存后不可修改
            
        }
    });
}

var saved_scheme_meta;

$(document).ready(function () {
    // ajax csrf
    var csrftoken = Cookies.get('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#new_scheme').click(function (e) {
        e.preventDefault();
        $('#new_scheme_settings').show();
        editOn(); //挂载单击事件，使字段可编辑
    });

    //编辑框初始化及事件挂载
    $('#edit_box').css({
        width: 0,
        height: 0,
        position: "absolute"
    }).blur(function (e) {
        var txt_val,
            data_type = $('.edited').data("type");
        if (data_type == "checkbox") {
            txt_val = $(this).prop('checked');
            $('.edited').css({'visibility': 'visible'});
        } else if (data_type == "text") {
            txt_val = $('#edit_box').val();
        } else if (data_type == "number") {
            txt_val = $('#edit_box').val();
        }
        $('.edited').text(txt_val);
        $(this).val('').hide();
    });

    $('#create_scheme').click(function (e) {
        e.preventDefault();
        schemeJson('create');
    });

    $('#edit_scheme_settings').click(function (e) {
        e.preventDefault();
        if ($(this).text() == "Edit") {
            $(this).text("Update");
            editOn(); //挂载单击事件，使字段可编辑
        } else {
            $(this).text("Edit");
            $('.editable').off('click');
            schemeJson('update');
        }

    });
});