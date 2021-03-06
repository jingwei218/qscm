var scheme_hash_pid_glb, datasheet_hash_pid_glb;
var option_list;
var number_of_datasheets, number_of_vendors;
var number_of_options, mix_options, min_in_options, number_of_rows, number_of_columns, quantity_allocated;
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

function displayDataSheetNameList(datasheets, number_of_datasheets) {
    $('#datasheet_namelist>li').remove(); //移除所有数据表名称
    for (var i = 0; i < number_of_datasheets; i++) {
        $('#datasheet_namelist').append('<li role="presentation"><a href=""></a></li>');
        if (i <= datasheets.length - 1) { //生成数据表名称列表
            $('#datasheet_namelist>li').last().find('a')
                .text(datasheets[i]['datasheet_name'])
                .attr('id', datasheets[i]['datasheet_hash_pid']);
        } else { //当数据表数量大于已生成数据表数量时，表示生成数据表未达上限，可以继续添加
            $('#datasheet_namelist>li').last().find('a')
                .addClass("glyphicon glyphicon-plus").attr("aria-hidden", "true");
        }
    }
    $('#datasheet_namelist>li:first').addClass('active'); //默认选中第一个数据表
    $('#scheme_settings_operation').hide(); //不显示编辑按钮
    $('#scheme_settings_lock').hide(); //不显示创建数据表按钮
    $('#datasheet_settings_container').show(); //显示数据表设置
    $('#datasheet_settings_container .editable').text(''); //清空表单
    $('#datasheet_settings_operation').text('Create').show(); //显示新建按钮
    $('#datasheet_settings_lock').hide(); //不显示创建模板按钮
    $('#datasheet_template').hide(); //不显示数据表模板
    editOn('#datasheet_settings_container'); //挂载编辑事件
}

function displaySettingLists(lists) {
    //遍历带type-list类的td，从td的data-optionkey获取键，再得到键对应的列表，放入选项列表中
    $('#datasheet_settings_container .type-list').each(function(i, element) {
        var optionkey = $(element).data('optionkey'),
            options = option_list[optionkey],
            box_width = $(element).outerWidth(),
            box_height = $(element).outerHeight();
        $(element).append('<select></select>');
        $(options).each(function(i, option) {
            $(element).find('select').append('<option value="' + option + '">' + option + '</option>');
        });
    });
    if (lists) {
        $(lists).each(function(i, element) {
            var find_target = 'option[value="' + element + '"]';
            $('#datasheet_settings_container .type-list select').eq(i)
                .find(find_target).attr('selected', 'selected');
        });
    }
}

function displayDataSheetTemplate(datasheet_field_list, datasheet_fields, datasheet_element_exists, uoms, quantity_roles, number_of_columns) {

    $('#datasheet_template_caption').text($('.datasheet_name').text()); //提示数据表名称

    //每行除第一列外全部删除
    $('#datasheet_template tr').each(function(i, element) {
        $(element).find('td').not(':first').remove();
    });

    //生成计量单位数据表
    var uom_datalist = '<datalist id="uom_list">';
    $(uoms).each(function(i, element) {
        uom_datalist += '<option value=' + element['name'] +
            ' label=' + element['name'] + ' id=' + element['uom_hash_pid'] +
            ' />';
    });
    uom_datalist += '</datalist>';

    for (var i = 0; i < number_of_columns; i++) {

        $('#column_name').append('<td class="editable" data-type="text"></td>');
        $('#column_type').append('<td><select></select></td>'); //列类型为下拉列表
        $('#quantity_uom, #quantity_role').append('<td></td>'); //添加数量单位列表
        $('#column_name td:last, #column_type td:last, #quantity_uom td:last, #quantity_role td:last').data('sequence', i); //列添加次序

        //添加列类型选项
        for (var j = 0; j < datasheet_field_list.length; j++) {
            $('#column_type select:last').append('<option></option>');
            $('#column_type select:last').find('option:last')
                .text(datasheet_field_list[j])
                .attr('value', datasheet_field_list[j])
                .attr('id', j);
        }

        //前两列必须为序列号和产品类型，最后一列必须为供应商，不可更改
        var field_type, find_target;
        if (i <= 1) {
            if (i == 0) {
                field_type = 'Serial';
            } else if (i == 1) {
                field_type = 'Vendor';
            }
            find_target = 'option[value="' + field_type + '"]';
            $('#column_type select').eq(i).attr('disabled', 'disabled')
                .find(find_target).attr('selected', 'selected');
        }

        //当找到可用字段信息时
        if (datasheet_fields.length > 0) {
            $('#column_name td:last')
                .attr('id', datasheet_fields[i]['sequence'])
                .text(datasheet_fields[i]['display_name']);

            //匹配字段类型
            var field_type = datasheet_fields[i]['field_type'],
                find_target = 'option[value="' + field_type + '"]';
            $('#column_type select:last')
                .find(find_target).attr('selected', 'selected');

            //数量字段时，显示单位输入框和数量类型
            if (field_type == 'Quantity') {
                $('#quantity_uom td:last').append('<input list="uom_list"/>')
                    .append(uom_datalist);
                $('#quantity_uom input:last').val(datasheet_fields[i]['quantity_uom']);
                $('#quantity_role td:last').append('<select></select>');
                $(quantity_roles).each(function(i, element) {
                    $('#quantity_role select:last').append('<option value="' + element[0] + '">' + element[1] + '</option>');
                });
                var quantity_role = datasheet_fields[i]['quantity_role'];
                find_target = 'option[value="' + quantity_role + '"]';
                $('#quantity_role select:last').find(find_target).attr('selected', 'selected');
            }
        }
    }

    $('#column_type select').change(function(e) {
        var column_type = $(e.target).find('option:selected').val(),
            seq = $(e.target).parent('td').data('sequence');
        //若为数量，显示列表；若非数量，移除列表
        if (column_type == 'Quantity') {
            $('#quantity_uom').find('td').not(':first').eq(seq).append('<input list="uom_list"/>').append(uom_datalist);
            $('#quantity_role').find('td').not(':first').eq(seq).append('<select></select>');
            $(quantity_roles).each(function(i, element) {
                $('#quantity_role').find('td').not(':first').eq(seq).find('select').append('<option value="' + element[0] + '">' + element[1] + '</option>');
            });
        } else {
            $('#quantity_uom').find('td').not(':first').eq(seq).find('input').remove();
            $('#quantity_role').find('td').not(':first').eq(seq).find('select').remove();
        }
    });

    if (datasheet_element_exists) {
        $('#column_type select, #quantity_uom input, #quantity_role select').attr('disabled', 'disabled');
        $('#datasheet_template_create').hide();
        $('#datasheet_template_download').hide();
        $('#datasheet_file').hide();
    } else {
        $('#datasheet_template_create').show();
    }

    $('#datasheet_template').show(); //显示数据表模板
    $('#datasheet_settings_operation').hide(); //不显示编辑按钮
    $('#datasheet_settings_lock').hide(); //不显示创建数据表模板按钮
    editOn('#datasheet_template'); //使模板可编辑
}

function saveSchemeSettings(mode) {

    var scheme_settings = new Array(),
        scheme_users = new Array(),
        scheme_name = $('.scheme_name').text();

    $('.scheme_setting').each(function(i, element) {
        var setting_hash_pid = $(element).find('.setting_name').attr('id'), //设置项的pid号
            scheme_setting_value = $(element).find('.scheme_setting_value').text(); //设置项的值

        scheme_settings[scheme_settings.length] = { //在设置列表的最后添加设置项
            "setting_hash_pid": setting_hash_pid,
            "scheme_setting_value": scheme_setting_value
        }
    });

    //保存选中状态
    $('#scheme_user_list>option').each(function(i, element) {
        var user_status, selected;
        //确定实际选中状态
        if ($(element).is(':selected')) {
            selected = 1;
        } else {
            selected = 0;
        }
        //数据库中保存的选中状态
        if (mode == "create") {
            user_status = selected;
            $(element).data('status', user_status);
        } else if (mode == "update") {
            user_status = $(element).data('status');
        }
        scheme_users[scheme_users.length] = {
            "user_username": $(element).text(),
            "user_hash_pid": $(element).attr('value'),
            "user_selected": selected,
            "user_status": user_status
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
        url: ajax_save_scheme_settings_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function(rec_json) { //ajax发送成功后获得后台发送的反馈信息
        var err = rec_json['error_message'],
            scheme_name = rec_json['scheme_name'],
            msg_create = "Scheme &lt;" + scheme_name + "&gt; was created.",
            msg_update = "Scheme &lt;" + scheme_name + "&gt; was updated.";
        //scheme_meta['scheme_hash_pid'] = scheme_hash_pid_glb;
        if (err) { //若有收到后台错误信息，显示错误信息；否则显示生成信息
            $('#scheme_caption').html(err);
        } else {
            if (mode == 'create') {
                $('#scheme_caption').html(msg_create);
            } else if (mode == 'update') {
                $('#scheme_caption').html(msg_update);
            }
            scheme_hash_pid_glb = rec_json['scheme_hash_pid']; //用于在更新设置时向后台传输项目的pid
            $('.scheme_name').text(scheme_name); //更新项目名称
            $('#scheme_settings_operation').text('Edit'); //保存后显示编辑按钮
            $('#scheme_settings_lock').show(); //保存后显示锁定按钮
            $('#scheme_settings_container .editable').off('click'); //保存后不可修改
            $('#scheme_user_list').attr("disabled", "disabled");
        }

        number_of_datasheets = parseInt(scheme_settings[0]['scheme_setting_value']);
        number_of_vendors = parseInt(scheme_settings[1]['scheme_setting_value']);

    });
}

function getSchemeSettings(scheme_hash_pid) {

    //项目的元数据
    var scheme_meta = {
        "scheme_hash_pid": scheme_hash_pid
    }

    //将元数据转换为json
    scheme_meta_json = JSON.stringify(scheme_meta);

    //发送异步数据到后台
    $.ajax({
        url: ajax_get_scheme_settings_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function(rec_json) {
        var scheme_name = rec_json['scheme_name'],
            scheme_settings = rec_json['scheme_settings'],
            scheme_users = rec_json['scheme_users'],
            datasheets = rec_json['datasheets'],
            scheme_setting_locked = rec_json['setting_locked'];

        option_list = rec_json['option_list'];

        //(1)项目设置部分
        $('.scheme_name').text(scheme_name); //在项目名称栏中显示名称
        //在项目设置栏中显示设置值
        $(scheme_settings).each(function(i, element) {
            $('.scheme_setting_value').eq(i).text(element['scheme_setting_value']);
        });

        $('#scheme_user_list>option').remove(); //移除所有用户名
        //重新添加用户名，关联id号，并选定项目拥有者
        $(scheme_users).each(function(i, element) {
            $('#scheme_user_list').append('<option></option>');
            $('#scheme_user_list>option').last()
                .text(element['user_username'])
                .attr('value', element['user_hash_pid']);
            if (element['selected_owner']) {
                $('#scheme_user_list>option').last()
                    .attr('selected', 'selected') //显示选中
                    .data('status', 1); //系统存储的选中状态
            } else {
                $('#scheme_user_list>option').last()
                    .data('status', 0); //系统存储的未选中状态
            }
        });
        $('#scheme_user_list').attr('disabled', 'disabled');
        //(1)项目设置部分

        //(2)项目设置赋值到全局变量
        number_of_datasheets = parseInt(scheme_settings[0]['scheme_setting_value']);
        number_of_vendors = parseInt(scheme_settings[1]['scheme_setting_value']);

        //(3)数据表设置的显示

        if (scheme_setting_locked) {
            //锁住设置时，自动显示所有数据表设置
            displayDataSheetNameList(datasheets, number_of_datasheets);
            if (datasheets.length > 0) {
                getDataSheetSettings(datasheets[0]['datasheet_hash_pid']); //获得第一个数据表的设置信息
            } else {
                displaySettingLists();
            }

        } else {
            //未锁住设置时，可以选择编辑设置项
            $('#scheme_settings_operation').text('Edit').show();
            $('#scheme_settings_lock').show();
            $('#datasheet_settings_container').hide();
            $('#datasheet_settings_container .editable').off('click');
        }
        //(3)数据表设置的显示
    });
}

function lockSchemeSettings(scheme_hash_pid) {

    //项目的元数据
    var scheme_meta = {
        "scheme_hash_pid": scheme_hash_pid,
        "scheme_setting_locked": true
    }

    //将元数据转换为json
    scheme_meta_json = JSON.stringify(scheme_meta);

    $.ajax({
        url: ajax_lock_scheme_settings_url,
        dataType: "json",
        method: "POST",
        data: scheme_meta_json,
    }).done(function(rec_json) {
        option_list = rec_json['option_list'];
        var datasheets = rec_json['datasheets'];
        displayDataSheetNameList(datasheets, number_of_datasheets);
        displaySettingLists();
    });
}

function saveDataSheetSettings(mode) {

    var datasheet_settings = new Array(),
        datasheet_name = $('.datasheet_name').text(),
        datasheet_category = $('.datasheet_category option:selected').val();
    $('.datasheet_setting').each(function(i, element) {
        var setting_hash_pid = $(element).find('.setting_name').attr('id'); //设置项的hash_pid号
        if ($(element).find('.datasheet_setting_value').data('type') == 'list') {
            datasheet_setting_value = $(element).find('option:selected').val();
        } else {
            datasheet_setting_value = $(element).find('.datasheet_setting_value').text(); //设置项的值
        }
        datasheet_settings[datasheet_settings.length] = { //在设置列表的最后添加设置项
            "setting_hash_pid": setting_hash_pid,
            "datasheet_setting_value": datasheet_setting_value
        }
    });

    //数据表的元数据
    var datasheet_meta = {
        "scheme_hash_pid": scheme_hash_pid_glb,
        "datasheet_hash_pid": datasheet_hash_pid_glb,
        "datasheet_name": datasheet_name,
        "datasheet_category": datasheet_category,
        "datasheet_settings": datasheet_settings,
        "mode": mode
    }

    //将元数据转换为json
    datasheet_meta_json = JSON.stringify(datasheet_meta);
    //发送异步数据到后台
    $.ajax({
        url: ajax_save_datasheet_settings_url,
        dataType: "json",
        method: "POST",
        data: datasheet_meta_json,
    }).done(function(rec_json) { //ajax发送成功后获得后台发送的反馈信息

        datasheet_hash_pid_glb = rec_json['datasheet_hash_pid']; //用于在更新设置时向后台传输项目的pid
        var err = rec_json['error_message'],
            datasheet_name = rec_json['datasheet_name'],
            msg_create = "Datasheet &lt;" + datasheet_name + "&gt; was created.",
            msg_update = "Datasheet &lt;" + datasheet_name + "&gt; was updated.";

        if (err) { //若有收到后台错误信息，显示错误信息；否则显示生成信息
            $('#datasheet_caption').html(err);
        } else {
            if (mode == 'create') {
                $('#datasheet_caption').html(msg_create);
            } else if (mode == 'update') {
                $('#datasheet_caption').html(msg_update);
            }
            $('.datasheet_name').text(datasheet_name);
            $('#datasheet_settings_operation').text('Edit'); //保存后显示编辑按钮
            $('#datasheet_settings_lock').show(); //保存后显示锁定按钮
            $('#datasheet_settings_container .editable').off('click'); //保存后不可修改
            $('#datasheet_settings_container .type-list').each(function(i, element) {
                $(element).text($(element).find('select').val());
            });
            $('#datasheet_namelist>li.active').find('a')
                .text(datasheet_name).attr('id', datasheet_hash_pid_glb)
                .removeClass('glyphicon glyphicon-plus').removeAttr('aria-hidden');
        }
    });

    number_of_options = parseInt(datasheet_settings[0]['datasheet_setting_value']);
    mix_options = datasheet_settings[1]['datasheet_setting_value'] == 'true';
    min_in_options = datasheet_settings[2]['datasheet_setting_value'] == 'true';
    number_of_rows = parseInt(datasheet_settings[3]['datasheet_setting_value']);
    number_of_columns = parseInt(datasheet_settings[4]['datasheet_setting_value']);
    //quantity_allocated = datasheet_settings[5]['datasheet_setting_value'] == 'true';
}

function getDataSheetSettings(datasheet_hash_pid) {

    datasheet_hash_pid_glb = datasheet_hash_pid; //传值到全局变量，在更新设置时引用

    //数据表的元数据
    var datasheet_meta = {
        "datasheet_hash_pid": datasheet_hash_pid
    }

    //将元数据转换为json
    datasheet_meta_json = JSON.stringify(datasheet_meta);

    $.ajax({
        url: ajax_get_datasheet_settings_url,
        dataType: "json",
        method: "POST",
        data: datasheet_meta_json,
    }).done(function(rec_json) {
        var datasheet_category = rec_json['datasheet_category'],
            datasheet_settings = rec_json['datasheet_settings'],
            datasheet_setting_locked = rec_json['setting_locked'];

        //(1)数据表设置部分
        $('.datasheet_name').text($('#datasheet_namelist>li.active').find('a').text()); //在数据表名称栏中显示名称
        $('.datasheet_category').text(datasheet_category); //显示数据表分类
        //在项目设置栏中显示设置值
        $(datasheet_settings).each(function(i, element) {
            $('.datasheet_setting_value').eq(i).text(element['datasheet_setting_value']);
        });
        //(1)数据表设置部分

        //(2)数据表设置赋值到全局变量
        number_of_options = parseInt(datasheet_settings[0]['datasheet_setting_value']);
        mix_options = datasheet_settings[1]['datasheet_setting_value'] == 'true';
        min_in_options = datasheet_settings[2]['datasheet_setting_value'] == 'true';
        number_of_columns = parseInt(datasheet_settings[4]['datasheet_setting_value']);
        //(2)数据表设置赋值到全局变量

        //(3)数据表设置部分
        $('#datasheet_settings_container .editable').off('click');
        if (datasheet_setting_locked) {
            //锁住设置时，自动显示所有数据表设置
            $('#datasheet_settings_operation').hide(); //不显示编辑按钮
            $('#datasheet_settings_lock').hide(); //不显示创建数据表按钮
            lockDataSheetSettings(datasheet_hash_pid);
        } else {
            //未锁住设置时，可以选择编辑设置项
            $('#datasheet_settings_operation').text('Edit').show();
            $('#datasheet_settings_lock').show();
            $('#datasheet_template').hide();
        }
        //(3)数据表设置部分
    });

}

function lockDataSheetSettings(datasheet_hash_pid) {

    //项目的元数据
    var datasheet_meta = {
        "datasheet_hash_pid": datasheet_hash_pid,
        "datasheet_setting_locked": true
    }

    //将元数据转换为json
    datasheet_meta_json = JSON.stringify(datasheet_meta);

    $.ajax({
        url: ajax_lock_datasheet_settings_url,
        dataType: "json",
        method: "POST",
        data: datasheet_meta_json,
    }).done(function(rec_json) {
        var datasheet_field_list = rec_json['datasheet_field_list'],
            datasheet_fields = rec_json['datasheet_fields'],
            datasheet_element_exists = rec_json['datasheet_element_exists'],
            uoms = rec_json['uoms'],
            quantity_roles = rec_json['quantity_roles'],
            xltemplate_file_name = rec_json['xltemplate_file_name'];

        displayDataSheetTemplate(datasheet_field_list, datasheet_fields, datasheet_element_exists, uoms, quantity_roles, number_of_columns);
        if (xltemplate_file_name) {
            displayTemplateDownload(xltemplate_file_name, datasheet_hash_pid);
        } else {
            $('#datasheet_template_download').hide();
            $('#datasheet_file').hide();
        }
    });
}

function saveDataSheetTemplate() {

    var datasheet_template_fields = new Array();
    $('#column_name .editable').each(function(i, element) {
        var sequence = $(element).data('sequence'), //获取字段的次序
            display_name = $(element).text(),
            field_type = $('#column_type select').eq(i).find('option:selected').val(),
            quantity_role = $('#quantity_role td').not(':first').eq(i).find('select').find('option:selected').val(),
            quantity_uom = $('#quantity_uom td').not(':first').eq(i).find('input').val();

        datasheet_template_fields[datasheet_template_fields.length] = { //在设置列表的最后添加设置项
            "sequence": sequence,
            "display_name": display_name,
            "field_type": field_type,
            "quantity_role": quantity_role,
            "quantity_uom": quantity_uom
        }
    });

    //数据表的元数据
    var datasheet_field_meta = {
        "datasheet_hash_pid": datasheet_hash_pid_glb,
        "datasheet_template_fields": datasheet_template_fields
    }

    //将元数据转换为json
    datasheet_field_meta_json = JSON.stringify(datasheet_field_meta);
    //发送异步数据到后台
    $.ajax({
        url: ajax_save_datasheet_fields_url,
        dataType: "json",
        method: "POST",
        data: datasheet_field_meta_json,
    }).done(function(rec_json) { //ajax发送成功后获得后台发送的反馈信息

        var err = rec_json['error_message'],
            msg_save = "Template was saved.";

        if (err) { //若有收到后台错误信息，显示错误信息；否则显示生成信息
            $('#datasheet_template_caption').html(err);
        } else {
            $('#datasheet_template_caption').html(msg_save);
            displayTemplateDownload(rec_json['xltemplate_file_name'], datasheet_hash_pid_glb);
            //$('#datasheet_namelist').find('a#' + datasheet_hash_pid_glb).click();
        }
    });
}

function displayTemplateDownload(filename, datasheet_hash_pid) {
    $('#datasheet_template_download')
        .html('<span class="glyphicon glyphicon-cloud-download" aria-hidden="true"></span>' + ' ' + filename)
        .attr('href', download_datasheet_template_url + datasheet_hash_pid + '/')
        .show();
    $('#datasheet_file').show();
}

function editOn(target) {
    //可编辑字段点击事件
    $(target).find('.editable').click(function(e) {
        e.preventDefault();
        var box_width = $(this).outerWidth(),
            box_height = $(this).outerHeight(),
            box_left = $(this).offset().left,
            box_top = $(this).offset().top,
            edited_value = $(this).text(),
            edit_type = $(this).data("type");

        $('.edited').removeClass("edited");
        $(this).addClass("edited");

        if (edit_type != "list") {
            $('#edit_box').show()
                .attr("type", edit_type)
                .offset({
                    left: box_left,
                    top: box_top
                }).css({
                    width: box_width,
                    height: box_height,
                }).focus().val(edited_value).select();
        }
    });
}

$(document).ready(function() {

    //编辑框初始化及事件挂载
    $('#edit_box').css({
        width: 0,
        height: 0,
        position: "absolute"
    }).blur(function(e) { //编辑框失焦后
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
        $('.edited').removeClass('edited');
        $(this).val('').hide();
    });

    //打开设置栏
    $('#new_scheme, .setting').click(function(e) {
        e.preventDefault();
        $('#scheme_settings_container').show();

        if ($(this).is('#new_scheme')) { //新建项目的情况
            $('#scheme_settings_operation').text('Create').show(); //显示新建按钮
            $('#scheme_settings_lock').hide(); //隐藏锁定按钮
            $('#scheme_settings_container .editable').text(''); //清空表单
            $('#datasheet_settings_container').hide(); //隐藏数据表设置
            $('#scheme_user_list').removeAttr('disabled'); //使用户列表可选
            editOn('#scheme_settings_container'); //挂载单击事件，使字段可编辑
        } else { //显示项目设置的情况
            scheme_hash_pid_glb = $(this).attr('id');
            getSchemeSettings(scheme_hash_pid_glb);
        }
    });

    //点击新建或更新项目设置链接
    $('#scheme_settings_operation').click(function(e) {
        e.preventDefault();
        if ($(this).text() == "Create") {
            saveSchemeSettings('create');
        } else if ($(this).text() == "Update") { //Update
            saveSchemeSettings('update');
        } else if ($(this).text() == "Edit") {
            $(this).text("Update"); //点击编辑后变为更新按钮
            $('#scheme_settings_lock').hide(); //隐藏锁定设置按钮，编辑状态下不可锁定
            $('#scheme_user_list').removeAttr('disabled'); //使用户列表可编辑
            editOn('#scheme_settings_container'); //挂载单击事件，使字段可编辑
        }

    });

    $('#scheme_settings_lock').click(function(e) {
        e.preventDefault();
        lockSchemeSettings(scheme_hash_pid_glb);
    });

    $('#datasheet_namelist').click(function(e) {
        e.preventDefault();
        if ($(e.target).is('a')) {
            $('#datasheet_template').hide();
            datasheet_hash_pid = $(e.target).attr('id');
            if (datasheet_hash_pid) {
                getDataSheetSettings(datasheet_hash_pid);
            } else {
                $('#datasheet_settings_container .editable').text(''); //清空表单
                $('#datasheet_settings_operation').text('Create').show(); //显示新建按钮
                $('#datasheet_settings_lock').hide(); //不显示创建模板按钮
                editOn('#datasheet_settings_container'); //使设置可编辑
                displaySettingLists();
            }
            $('.active').removeClass('active');
            $(e.target).parent('li').addClass('active');
        }
    });

    //点击新建或更新数据表设置链接
    $('#datasheet_settings_operation').click(function(e) {
        e.preventDefault();
        if ($(this).text() == "Create") {
            saveDataSheetSettings('create');
        } else if ($(this).text() == "Update") { //Update
            saveDataSheetSettings('update');
        } else if ($(this).text() == "Edit") {
            $(this).text("Update"); //点击编辑后变为更新按钮
            $('#datasheet_settings_lock').hide(); //隐藏锁定设置按钮，编辑状态下不可锁定
            $('#datasheet_template').hide(); //隐藏数据表模板
            editOn('#datasheet_settings_container'); //挂载单击事件，使字段可编辑
            var lists = new Array();
            $('#datasheet_settings_container .type-list').each(function(i, element) {
                lists[i] = $(element).text();
                $(element).text('');
            });
            displaySettingLists(lists);

        }
    });

    $('#datasheet_settings_lock').click(function(e) {
        e.preventDefault();
        lockDataSheetSettings(datasheet_hash_pid_glb);
    });

    $('#datasheet_template_operation').click(function(e) {
        e.preventDefault();
        saveDataSheetTemplate();
    });

    $('#datasheet_template').scroll(function(e) {
        $('#edit_box').blur();
    });

    $('#datasheet_file_operation').click(function(e) {
        e.preventDefault();
        $('#datasheet_upload_form').submit();
    });

    $('#datasheet_upload_form').submit(function() {
        var formData = new FormData(this);
        formData.append('datasheet_hash_pid', datasheet_hash_pid_glb);

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
            $('#datasheet_file').val('');
            if (err) {
                $('#datasheet_file_upload_message').text(err);
            } else {
                $('#datasheet_file_upload_message').text(datasheet_file_name + ' was uploaded.');
            }
        });
        return false;
    });

});