var gid = 0;

$(document).ready(function() {

    $('.add_element').click(function(e) {
        var html,
            eid = $(e.target).attr('id'),
            inputVal = $(e.target).next().val();
        switch(eid) {
            case "add_table":
                html = '<table id="t-' + gid.toString() + '" '
                    + 'class="draggable resizable">'
                    + '<thead><tr>';
                for (var i=0; i<inputVal; i++) {
                    html += '<th></th>'
                }
                html += '</tr></thead><tbody><tr>'
                for (var i=0; i<inputVal; i++) {
                    html += '<td></td>'
                }
                html += '</tr></tbody></table>';
                break;
            case "add_header":
                html = '<h5 class="draggable">'
                    + inputVal
                    +'</h5>';
                break;
            case "add_label":
                html = '<span class="draggable">'
                    + inputVal
                    +'</span>';
        }
        gid += 1;
        $('#c01').append(html);
        $('.draggable').draggable();
        $('.resizable').resizable();
    });
});

