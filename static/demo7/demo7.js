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
    socket = new WebSocket('ws://127.0.0.1:8000/socket/');
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

$(document).ready(function () {

    var $table1 = $('#t-1'),
        $headers = $table1.find('thead th');
    $headers
        .each(function () {
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
        var json_data = { 'url': window.location.protocol + '//10.0.0.2/demo7/wspush/' }, //test use only
            //json_data = { 'url': window.location.protocol + '//' + window.location.host + '/demo7/ws/' },
            data = JSON.stringify(json_data);
        $.ajax({
            url: '/demo7/qrcode/',
            dataType: "json",
            method: "POST",
            data: data
        }).done(function (rec_json) {
            img_path = rec_json['img_path'];
            $('#qrcode_img').append('<img src="' + img_path + '" alt="QR CODE"/>');
        });
    });

    $('.draggable').draggable({
        drag: function (e, ui) {

        }
    });

    $('.resizable').resizable();

    $('#print').click(function(e) {
        $.print(".printarea");
    })
    
    $('#save').click(function(e) {
        var json_data = {'printableElements': new Array()}
        $('.printable').each(function(i, e) {
            var ele_data = {
                'name': $(this).data('name'),
                'positionX': $(this).position().left,
                'positionY': $(this).position().top,
                'width': $(this).outerWidth(),
                'height': $(this).outerHeight()
            }
            json_data['printableElements'].push(ele_data);
        });
        data = JSON.stringify(json_data);
        console.log(data);
        $.ajax({
            url: '/demo7/savetemplate/',
            dataType: "json",
            method: "POST",
            data: data
        }).done(function(rec_json) {
            
        });
    });

});


