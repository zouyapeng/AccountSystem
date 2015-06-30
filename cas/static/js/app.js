/**
 * Created by root on 2/6/15.
 */

$.fn.button_add_disabled = function(){
    this.attr('disabled', true).addClass('btn-u-default');
    return this;
}

$.fn.button_remove_disabled = function(){
    this.attr('disabled', false).removeClass('btn-u-default');
    return this;
}
$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [ o[this.name] ];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});



$(function(){
  $('[data-toggle="popover"]').popover();

    $(document).on('click', 'img.captcha-img', function() {
        var src = $(this).attr('src');
        $(this).attr('src', src.split('?')[0]+'?v='+Math.random());
    });

    $(".input-group-filter .show-filter-more").click(function(){
        var gf = $(this).parents(".input-group-filter");
        if(gf.hasClass("open")){
            gf.removeClass("open");
        }else{
            gf.addClass("open");
        }

    });
})
