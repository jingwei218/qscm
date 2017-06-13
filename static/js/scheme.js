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
    var p_data = {};
    $('#save_n_create_scheme').click(function(e){
        e.preventDefault();
        p_data['scheme_name'] = $('.scheme_name').text();
        $('.scheme_setting').each(function(i, element) {
            var scheme_setting_id = $(element).find('.scheme_setting_name').attr('id'),
                scheme_setting_value = $(element).find('.scheme_setting_value').text();
            p_data[scheme_setting_id] = scheme_setting_value;
        });
        $.ajax({
            url: "/{{ platform|lower }}/{{ service|lower }}/scheme/save_n_create_scheme/",
            dataType: "json",
            method: "POST",
            data: p_data,
        }).done(function(json) {
            var scheme_id = json['scheme_id'],
                msg = "Scheme " + scheme_id + " was created.";
            $('#scheme_caption').html(msg);
        })
    });
});