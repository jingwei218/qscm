var scheme_hash_pid_glb;
var number_of_datasheets, number_of_vendors;
var csrftoken = Cookies.get('csrftoken');

// ajax csrf
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
            $('.edited').css({ 'visibility': 'hidden' });
        } else {
            $('#edit_box').css({
                width: box_width,
                height: box_height,
            });
        }
        $('#edit_box').focus().val(edited_value).select();
    });
    $('#scheme_user_list').removeAttr('disabled');
}

function saveSchemeJson(mode) {
    var scheme_settings = new Array(),
        scheme_users = new Array(),
        scheme_name = $('.scheme_name').text();
    $('.scheme_setting').each(function (i, element) {
        var setting_hash_pid = $(element).find('.setting_name').attr('id'), //设置项的pid号
            scheme_setting_value = $(element).find('.scheme_setting_value').text(); //设置项的值

        scheme_settings[scheme_settings.length] = { //在设置列表的最后添加设置项
            "setting_hash_pid": setting_hash_pid,
            "scheme_setting_value": scheme_setting_value
        }
    });

    //保存选中状态
    $('#scheme_user_list>option:selected').each(function(i, element) {
        scheme_users[scheme_users.length] = {
            "user_username": $(element).text(),
            "user_hash_pid": $(element).attr('value'),
            "user_selected": 1,
            "user_status": $(element).data('status')
        }
    });

    //保存未选中状态
    $('#scheme_user_list>option').not(':selected').each(function(i, element) {
        scheme_users[scheme_users.length] = {
            "user_username": $(element).text(),
            "user_hash_pid": $(element).attr('value'),
            "user_selected": 0,
            "user_status": $(element).data('status')
        }
    });
    
    //项目的元数据
    var scheme_meta = {
        "scheme_hash_pid": scheme_hash_pid_glb,
        "scheme_name": scheme_name,
        "scheme_settings": scheme_settings,
        "scheme_users": scheme_users,
        "mode": mode
    }

    //将元数据转换为json
    scheme_meta_json = JSON.stringify(scheme_meta);
    //发送异步数据到后台
    $.ajax({
        url: ajax_save_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function (rec_json) { //ajax发送成功后获得后台发送的反馈信息
        scheme_hash_pid_glb = rec_json['scheme_hash_pid']; //用于在更新设置时向后台传输Scheme的pid
        var err = rec_json['error_message'],
            msg_create = "Scheme &lt;" + scheme_name + "&gt; was created.",
            msg_update = "Scheme &lt;" + scheme_name + "&gt; was updated."
        scheme_meta['scheme_hash_pid'] = scheme_hash_pid_glb;
        //console.log(rec_json);
        if (err) { //若有收到后台错误信息，显示错误信息；否则显示生成信息
            $('#scheme_caption').html(err);
        } else {
            if (mode == 'create') {
                $('#scheme_caption').html(msg_create);
            } else if (mode == 'update') {
                $('#scheme_caption').html(msg_update);
                $('#cancel_scheme_edit').hide();
            }
            $('#scheme_settings_operation').text('Edit');
            $('.editable').off('click');  //保存后不可修改
            $('#scheme_user_list').attr("disabled", "disabled");
        }
    });
}

function getSchemeJson(scheme_hash_pid) {

    //项目的元数据
    var scheme_meta = {
        "scheme_hash_pid": scheme_hash_pid
    }

    //将元数据转换为json
    scheme_meta_json = JSON.stringify(scheme_meta);

    //发送异步数据到后台
    $.ajax({
        url: ajax_get_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function(rec_json) {
        var scheme_name = rec_json['scheme_name'],
            scheme_settings = rec_json['scheme_settings'],
            scheme_users = rec_json['scheme_users'],
            data_sheets = rec_json['data_sheets'],
            scheme_setting_locked = rec_json['setting_locked'];

        $('.scheme_name').text(scheme_name);
        $(scheme_settings).each(function(i, element) {
            $('.scheme_setting_value').eq(i).text(element['scheme_setting_value']);
        });

        $('#scheme_user_list>option').remove();
        $(scheme_users).each(function(i, element) {
            $('#scheme_user_list').append('<option></option>');
            $('#scheme_user_list>option').last()
                .text(element['user_username'])
                .attr('value', element['user_hash_pid']);
            if (element['selected_owner']) {
                $('#scheme_user_list>option').last()
                    .attr('selected', 'selected')
                    .data('status', 1);
            } else {
                $('#scheme_user_list>option').last()
                    .data('status', 0)
            }
        });

        //scheme_hash_pid_glb = scheme_hash_pid;
        number_of_datasheets = parseInt($('.scheme_setting_value').eq(0).text()),
        number_of_vendors = parseInt($('.scheme_setting_value').eq(1).text());

        $('#datasheet_namelist>li').remove(); //移除所有数据表名称
        if (scheme_setting_locked) {
            //锁住设置时，自动显示所有数据表设置
            $('#scheme_settings_operation').hide(); //不显示编辑按钮
            $('#datasheet_settings_container').show();

            for (var i=0; i<number_of_datasheets; i++) {
                $('#datasheet_namelist').append('<li role="presentation"><a href=""></a></li>');
                if (i <= data_sheets.length-1) {
                    $('#datasheet_namelist>li').last().find('a').text(data_sheets[i]['datasheet_name']);
                } else {
                    $('#datasheet_namelist>li').last().find('a').html('<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>');
                }
            }

            
             $('#datasheet_namelist>li:first').addClass('active');

        } else {
            //未锁住设置时，可以选择编辑设置项
            $('#scheme_settings_operation').text('Edit').show();
            $('#datasheet_settings_container').hide();
            $('.editable').off('click');
        }
        
    });
}

$(document).ready(function () {

    //编辑框初始化及事件挂载
    $('#edit_box').css({
        width: 0,
        height: 0,
        position: "absolute"
    }).blur(function (e) { //编辑框失焦后
        var txt_val,
            data_type = $('.edited').data("type");
        if (data_type == "checkbox") {
            txt_val = $(this).prop('checked');
            $('.edited').css({ 'visibility': 'visible' });
        } else if (data_type == "text") {
            txt_val = $('#edit_box').val();
        } else if (data_type == "number") {
            txt_val = $('#edit_box').val();
        }
        $('.edited').text(txt_val);
        $(this).val('').hide();
    });

    //设置，打开设置栏
    $('#new_scheme, .setting').click(function (e) {
        e.preventDefault();
        $('#scheme_settings_container').show();

        if ($(this).is('#new_scheme')) { //新建项目的情况
            $('#scheme_settings_operation').text('Create').show();
            $('.editable').text('');  //清空表单
            $('#datasheet_settings_container').hide(); //隐藏数据表设置
            editOn(); //挂载单击事件，使字段可编辑  
        } else { //更新项目设置的情况
            scheme_hash_pid_glb = $(this).attr('id');
            getSchemeJson(scheme_hash_pid_glb);
            $('#scheme_user_list').attr('disabled', 'disabled');
        }
    });

    //点击新建或更新链接
    $('#scheme_settings_operation').click(function (e) {
        e.preventDefault();
        if ($(this).text() == "Create") {
            saveSchemeJson('create');
        } else if ($(this).text() == "Edit") {
            $(this).text("Update");
            editOn(); //挂载单击事件，使字段可编辑
        } else {  //Update
            saveSchemeJson('update');
        }

    });
});