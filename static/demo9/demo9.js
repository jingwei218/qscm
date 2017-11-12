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

function connectSocket() {
    socket = new WebSocket('ws://' + window.location.host.split(':')[0] + ':8080/socket/');
    if (socket.readyState == WebSocket.OPEN) {
        socket.onopen();
    }
    socket.onmessage = function (message) {
        var data = JSON.parse(message.data)
        if (data['action'] == 'push_qrcode') {
            $('#qrcode_img').html('');
        }
        $('#ws_message').text(data['msg']);
    };
}

function appendTable(json, cols, tpl, tplmsg) {
    var error_message = json['error_message'];
    if (error_message) {
        $(tplmsg).text(error_message);
        return;
    }
    var table = json['context'],
        eid = json['node_eid'],
        col_array = cols.split(','),
        msg = json['message'];
    $(tplmsg).text(msg);
    $(tpl).append('<table id="' + eid + '" class="te"><thead><tr></tr></thead><tbody></tbody></table>');
    var html = '';
    for (ci in col_array) {
        html += '<th>' + col_array[ci] + '</th>';
    }
    $(tpl).find('table:last').find('thead>tr').append(html);
    html = '';
    for (ri in table) {
        html += '<tr>';
        for (fi in col_array) {
            col = col_array[fi]
            html += '<td>' + table[ri][col] + '</td>';
        }
        html += '</tr>';
    }
    $(tpl).find('table:last').find('tbody').append(html);
    $(tpl).find('table:last').draggable().resizable();
}

function appendField(json, tpl, tplmsg) {
    var error_message = json['error_message'];
    if (error_message) {
        $(tplmsg).text(error_message);
        return;
    }
    var field = json['context'],
        eid = json['node_eid'],
        msg = json['message'];
    $(tplmsg).text(msg);
    $(tpl).append('<span id="' + eid + '" class="te">' + field + '</span>');
    $(tpl).find('span:last').draggable().resizable();
}

function appendLabel(json, tpl, tplmsg, labeltxt) {
    var error_message = json['error_message'];
    if (error_message) {
        $(tplmsg).text(error_message);
        return;
    }
    var eid = json['node_eid'],
        msg = json['message'],
        label = labeltxt;
    $(tplmsg).text(msg);
    html = '<span id="' + eid + '" class="te">' + label + '</span>';
    $(tpl).append(html);
    $(tpl).find('span:last').draggable().resizable();
}

$(document).ready(function () {

    var $table1 = $('#t-1'),
        $headers = $table1.find('thead th');
    $headers.each(function () {
        var keyType = this.className.replace(/^sort-/, '');
        $(this).data('keyType', keyType);
    })
        .wrapInner('<a href="#"></a>')
        .addClass('sort');

    var sortKeys = {
        alpha: function ($cell) {
            var key = $.trim($cell.text()).toUpperCase();
            return key;
        },
        numeric: function ($cell) {
            var num = $cell.text().replace(/^[^\d.]*/, '');
            var key = parseFloat(num);
            if (isNaN(key)) {
                key = 0;
            }
            return key;
        },
        date: function ($cell) {
            var key = Date.parse($cell.text());
            return key;
        }
    };

    $headers.click(function (e) {
        e.preventDefault();
        var $header = $(this),
            column = $header.index(),
            keyType = $header.data('keyType'),
            sortDirection = 1;

        if (!$.isFunction(sortKeys[keyType])) {
            return;
        }

        if ($header.hasClass('sorted-asc')) {
            sortDirection = -1;
        }

        var rows = $table1.find('tbody > tr').each(function () {
            var $cell = $(this).children('td').eq(column);
            $(this).data('sortKey', sortKeys[keyType]($cell));
        }).get();

        rows.sort(function (a, b) {
            var keyA = $(a).data('sortKey');
            var keyB = $(b).data('sortKey');
            if (keyA < keyB) return -sortDirection;
            if (keyA > keyB) return sortDirection;
            return 0;
        });

        $headers.removeClass('sorted-asc sorted-desc');
        $header.addClass(sortDirection == 1 ? 'sorted-asc' : 'sorted-desc');

        $.each(rows, function (index, row) {
            $table1.children('tbody').append(row);
        });
    });

    $('#edit_box').css({
        width: 0,
        height: 0,
        position: "absolute"
    }).blur(function (e) { //编辑框失焦后
        var txt_val = $('#edit_box').val();
        $('.edited').text(txt_val);
        $('.edited').removeClass('edited');
        $(this).val('').hide();
    });

    $('.editable').click(function (e) {
        e.preventDefault();
        var box_width = $(this).outerWidth(),
            box_height = $(this).outerHeight(),
            box_left = $(this).offset().left,
            box_top = $(this).offset().top,
            edited_value = $(this).text();
        $('.edited').removeClass("edited");
        $(this).addClass("edited");


        $('#edit_box').show()
            .offset({
                left: box_left,
                top: box_top
            }).css({
                width: box_width,
                height: box_height,
            }).focus().val(edited_value).select();
    });

    $('a#wsqr').click(function (e) {
        e.preventDefault();
        connectSocket();
        $('#qrcode_img').html('');
        var json_data = { 'url': window.location.protocol + '//' + window.location.host + '/demo9/wspush/' },
            data = JSON.stringify(json_data);
        $.ajax({
            url: '/demo9/qrcode/',
            dataType: "json",
            method: "POST",
            data: data
        }).done(function (rec_json) {
            var img_path = rec_json['img_path'];
            $('#qrcode_img').append('<img src="' + img_path + '" alt="QR CODE"/>');
        });
    });

    $('.draggable').draggable();

    $('.resizable').resizable();

    $('#print').click(function (e) {
        $.print(".printarea");
    });

    $('.add_element').click(function (e) {
        e.preventDefault();
        var html,
            eid = $(e.target).attr('id');
        switch (eid) {
            case "add_table":
                var tblMod = $('#tblMod').val(),
                    tblCol = $('#tblCol').val(),
                    json_data = {
                        'node': 'table',
                        'model_name': tblMod,
                        'filter_condition_string': $('#tblFltCon').val(),
                        'col_string': tblCol,
                        'template_name': $('#tplNam').val()
                    },
                    data = JSON.stringify(json_data);
                $.ajax({
                    url: '/demo9/addelement/',
                    dataType: "json",
                    method: "POST",
                    data: data
                }).done(function (rec_json) {
                    appendTable(rec_json, tblCol, '#template', '#template_msg');
                });
                break;
            case "add_field":
                var fldMod = $('#fldMod').val(),
                    fldCol = $('#fldCol').val(),
                    json_data = {
                        'node': 'field',
                        'model_name': fldMod,
                        'filter_condition_string': $('#fldFltCon').val(),
                        'col_string': fldCol,
                        'template_name': $('#tplNam').val()
                    },
                    data = JSON.stringify(json_data);
                $.ajax({
                    url: '/demo9/addelement/',
                    dataType: "json",
                    method: "POST",
                    data: data
                }).done(function (rec_json) {
                    appendField(rec_json, '#template', '#template_msg');
                });
                break;
            case "add_label":
                var lblTxt = $('#lblTxt').val(),
                    json_data = {
                        'node': 'label',
                        'label_text': $('#lblTxt').val(),
                        'template_name': $('#tplNam').val()
                    },
                    data = JSON.stringify(json_data);
                $.ajax({
                    url: '/demo9/addelement/',
                    dataType: "json",
                    method: "POST",
                    data: data
                }).done(function (rec_json) {
                    appendLabel(rec_json, '#template', '#template_msg', lblTxt);
                });
        }
    });

    $('#save').click(function (e) {
        var json_data = { 'templateElements': new Array() }
        $('.te').each(function (i, e) {
            var eid_arr = $(e).attr('id').split('-'),
                ele_data = {
                    'node': eid_arr[0],
                    'node_id': eid_arr[1],
                    'positionX': $(e).offset().left - $('#template').offset().left,
                    'positionY': $(e).offset().top - $('#template').offset().top,
                    'width': $(e).outerWidth(),
                    'height': $(e).outerHeight()
                }
            json_data['templateElements'].push(ele_data);
        });
        data = JSON.stringify(json_data);
        $.ajax({
            url: '/demo9/savetemplate/',
            dataType: "json",
            method: "POST",
            data: data
        }).done(function (rec_json) {
            var error_message = rec_json['error_message'];
            if (error_message) {
                $('#template_msg').text(error_message);
                return;
            }
            var msg = rec_json['message'];
            $('#template_msg').text(msg);
        });
    });

    $('#load').click(function (e) {
        e.preventDefault();
        $('#template .te').remove();
        var tplNam = $('#tplNam').val(),
            json_data = {
                'template_name': tplNam
            },
            data = JSON.stringify(json_data);
        $.ajax({
            url: '/demo9/loadtemplate/',
            dataType: "json",
            method: "POST",
            data: data
        }).done(function (rec_json) {
            var error_message = rec_json['error_message'];
            if (error_message) {
                $('#template_msg').text(error_message);
                return;
            }
            var templateElements = rec_json['templateElements'];
            for (key in templateElements) {
                var json = templateElements[key],
                    node = json['node'],
                    cols = json['columns'],
                    positionX = json['positionX'],
                    positionY = json['positionY'],
                    width = json['width'],
                    height = json['height'];
                switch (node) {
                    case "table":
                        appendTable(json, cols, '#template', '#template_msg');
                        break;
                    case "field":
                        appendField(json, '#template', '#template_msg');
                        break;
                    case "label":
                        appendLabel(json, '#template', '#template_msg', json['context']);
                }
                $('#template .te:last').offset({
                    left: positionX + $('#template').offset().left,
                    top: positionY + $('#template').offset().top
                }).outerWidth(width).outerHeight(height);
            }
        });
    });

    $('#reset').click(function(e) {
        e.preventDefault();
        $('#template .te').remove();
    });

    $('#tplNam').change(function() {
        $('#load').click();
    });

});


