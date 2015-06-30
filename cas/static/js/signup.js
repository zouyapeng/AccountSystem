/**
 * Created by root on 2/5/15.
 */
$(function(){
    $("#forgetForm").validate({
        submitHandler: function (form) {
            var $this = this;
            var $form = $(form);
            $form.find('button[type=submit]').button('loading');
            $.ajax({
                type: "POST",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/account/api/v1/user/forget/",
                data: $.toJSON($form.serializeObject()),
                success: function (data) {
                    $form.find('button[type=submit]').button('reset');
                    if (!data.status) {
                        $this.showLabel($form.find('*[name=' + data.f + ']'), data.msg);
                        $form.find('input[name=captcha]').val("");
                        $form.find('.captcha-img').click();
                    }else{
                        $form.find(".step1").addClass("hide");
                        $form.find(".step2").removeClass("hide");
                    }
                },
                error: function(){
                    $form.find('button[type=submit]').button('reset');
                    alert("服务器错误");
                }
            });
        },
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parent().append(error);
        },
        rules: {
            email: {
                required: true,
                email: true
            },
            captcha: {
                required: true
            }
        }
    });
    $("#resetPasswordForm1").validate({
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parent().append(error);
        },
        rules: {
            newpassword: {
                required: true,
                minlength: 5,
                maxlength: 30
            },
            newpassword1: {
                required: true,
                minlength: 5,
                maxlength: 30,
                equalTo: "#id_newpassword"
            }
        }
    });
    $("#signupForm").validate({
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parents('.col-xs-9').append(error);
        },
        rules: {
            username: {
                required: true,
                minlength: 2
            },
            password: {
                required: true,
                maxlength: 30,
                minlength: 5
            },
            password1: {
                required: true,
                minlength: 5,
                maxlength: 30,
                equalTo: "#id_password"
            },
            email: {
                required: true,
                email: true
            },
            security_question: "required",
            security_answer: "required",
            human_name: "required"
        }
    });

})