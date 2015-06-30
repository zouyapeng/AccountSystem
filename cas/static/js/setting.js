/**
 * Created by root on 2/6/15.
 */
$(function () {
//    ============修改安全邮箱 start=================
    var verifiedEmailForm = function(){
        var $form = $("#verifiedEmailForm")
        this.interval;
        var self = this;
        var step2 = $form.find('.step2');

        this.resendRequest=function(data){
            return $.ajax({
                type: "PUT",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/account/api/v1/user/verified-email/",
                data: $.toJSON(data)
            });
        };
        this.resendInterval = function(seconds){
            clearInterval(self.interval);
            var $a = step2.find('.resend');
            $a.html(seconds+"秒后可重发");
            $a.unbind("click");
            $a.attr("disabled", "disabled");
            self.interval = window.setInterval(function(){
                seconds--;
                $a.html(seconds+"秒后可重发");
                if(seconds<=1){
                    clearInterval(self.interval);
                    $a.removeAttr("disabled", "disabled");
                    $a.html("重新发送").click(function(){
                        self.resend($a);
                    });
                }
            }, 1000);
        }

        this.resend = function($btn){
            $btn.button('loading');
            self.resendRequest({}).then(function(data){
                $btn.button('reset');
                if(data.status){
                    if(step2.hasClass("hide")){
                        $form.find('.step1').removeClass("show").addClass("hide");
                        step2.removeClass("hide").addClass("show");
                    }
                    var seconds = data.seconds||120;
                    self.resendInterval(seconds);
                }else{
                    alert(data.msg);
                }
            }, function(){
                $btn.button('reset');
            })
        }

        this.init = function(){
            $form.validate({
                errorPlacement: function (error, element) {
                    error.addClass('help-block');
                    element.parents('.form-group').addClass('has-error');
                    element.parent('div').append(error);
                },
                submitHandler: function (form) {
                    var $self = $(form);
                    var $fs = this;
                    var $submitBtn = $self.find('button[type=submit]');
                    $submitBtn.button('loading');
                    self.resendRequest($self.serializeObject()).then(function(data){
                        $submitBtn.button('reset');
                        if(data.status){
                            $self.find('.step1').removeClass("show").addClass("hide");
                            $self.find('.step2').removeClass("hide").addClass("show");
                            var seconds = data.seconds||120;
                            self.resendInterval(seconds);
                        }else{
                            $fs.showLabel($self.find('*[name=' + data.f + ']'), data.msg);
                        }
                    }, function(){
                        $submitBtn.button('reset');
                        alert("服务器错误");
                    })
                },
                rules: {
                    email: {
                        required: true,
                        email: true
                    },
                    security_answer: {
                        required: true
                    },
                    new_email: {
                        required: true,
                        email: true
                    }
                }
            });

            if($form.find("button.resend-a").length){
//                重发激活邮件
                $form.find("button.resend-a").click(function(){
                    self.resend($(this));
                })
            }

        };

        return this;
    };
    new verifiedEmailForm().init();

//    ============修改安全邮箱 end=================


//    ============修改基本信息 start=================
    $("#profileForm").validate({
        submitHandler: function (form) {
            var $self = $(form);
            $self.find('button[type=submit]').button('loading');
            $.ajax({
                type: "PUT",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/account/api/v1/user-profile/",
                data: $.toJSON($self.serializeObject()),
                success: function (data) {
                    $self.find('button[type=submit]').button('reset');
                    alert("修改成功");
                }
            });
        },
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parent().append(error);
        },
        rules: {
            telephone: {
                isMobile: true
            }
        }
    });
//    ============修改基本信息 end=================

    var $iframe = $("#certificateDownloadIframe");

    $("#certificateForm").validate({
        submitHandler: function (form) {
            var $self = $(form);
            $self.find('button[type=submit]').button('loading');
            $.ajax({
                type: "POST",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/account/api/v1/user/certificate/download/",
                data: $.toJSON($self.serializeObject()),
                success: function (data) {
                    $self.find('button[type=submit]').button('reset');
                    $iframe.attr("src", $iframe.attr("data-src")+"?v="+String(Math.random()));
                },
                error:function(){
                    $self.find('button[type=submit]').button('reset');
                    alert("下载错误");
                }
            });
        },
        rules: {
            password: {
                required: true,
                minlength: 5,
                maxlength: 20
            }
        }
    });



    $("#securityForm").validate({
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parent('div').append(error);
        },
        submitHandler: function (form) {
            var $form = $(form);
            var $this = this;
            $form.find('button[type=submit]').button('loading');
            $.ajax({
                type: "PUT",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/account/api/v1/user/change-password/",
                data: $.toJSON($form.serializeObject()),
                success: function (data) {
                    $form.find('button[type=submit]').button('reset');
                    if (!data.status) {
                        $this.showLabel($form.find('*[name=' + data.f + ']'), data.msg);
                    }else{
                        alert("修改成功");
                        location.reload()
                    }
                },
                error:function(){
                    $form.find('button[type=submit]').button('reset');
                    alert("服务器错误");
                }
            });
        },
        rules: {
            old_password: {
                required: true,
                minlength: 5,
                maxlength: 100
            },
            new_password: {
                required: true,
                minlength: 5,
                maxlength: 100
            },
            new_password1: {
                required: true,
                minlength: 5,
                maxlength: 100,
                equalTo: "#id_new_password"
            }
        }
    });

    $("#securityQaForm").validate({
        submitHandler: function (form) {
            var $form = $(form);
            var step1 = $form.children(".step1");
            var step2 = $form.children(".step2");

            var $this = this;
            if(!step1.hasClass("hide")){
                step1.find('button[type=submit]').button('loading');
                $.ajax({
                    type: "POST",
                    dataType: 'json',
                    contentType: 'application/json;charset=UTF-8',
                    url: "/account/api/v1/user/change-security-qa/",
                    data: $.toJSON($form.serializeObject()),
                    success: function (data) {
                        $form.find('button[type=submit]').button('reset');
                        if (!data.status) {
                            $this.showLabel($form.find('*[name=' + data.f + ']'), data.msg);
                        }else{
                            step1.addClass("hide");
                            step2.removeClass("hide");
                        }
                    },
                    error:function(){
                        $form.find('button[type=submit]').button('reset');
                        alert("服务器错误");
                    }
                });
            }else{
                step2.find('button[type=submit]').button('loading');
                $.ajax({
                    type: "PUT",
                    dataType: 'json',
                    contentType: 'application/json;charset=UTF-8',
                    url: "/account/api/v1/user/change-security-qa/",
                    data: $.toJSON($form.serializeObject()),
                    success: function (data) {
                        $form.find('button[type=submit]').button('reset');
                        if (!data.status) {
                            $this.showLabel($form.find('*[name=' + data.f + ']'), data.msg);
                        }else{
                            alert("修改成功");
                            location.reload();
                        }
                    },
                    error:function(){
                        $form.find('button[type=submit]').button('reset');
                        alert("服务器错误");
                    }
                });

            }

        },
        errorPlacement: function (error, element) {
            error.addClass('help-block');
            element.parents('.form-group').addClass('has-error');
            element.parent('div').append(error);
        },
        rules: {
            security_answer: "required",
            new_security_answer: "required",
            new_security_question: "required"
        }
    });

//    ============用户组 start=================
    $(".group-list .applications").click(function(){
        var $this = $(this);
        if(!$this.attr("data-group-id")){
            return;
        }
        $this.button("loading");
        $.ajax({
            type: "POST",
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            url: "/account/api/v1/group/"+$this.data("group-id")+"/applications/",
            success: function (data) {
                $this.parent("td").html("等待验证");
            },
            error:function(){
                $this.button('reset');
                alert("服务器错误");
            }
        });
    })

    $(".group_users .edit").click(function(){
        var $this = $(this);
        if(!$this.attr("data-ug-id") || !$this.attr("data-method")){
            return;
        }
        $this.button("loading");
        $.ajax({
            type: $this.attr("data-method"),
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            url: "/account/api/v1/group/audit/"+$this.data("ug-id")+"/",
            success: function (data) {
                $this.button('reset');
                location.reload();
            },
            error:function(){
                $this.button('reset');
                alert("服务器错误");
            }
        });
    });

//    ============用户组 end=================
});