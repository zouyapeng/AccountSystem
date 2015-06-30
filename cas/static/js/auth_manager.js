/**
 * Created by root on 2/5/15.
 */
$(function () {

    var ManagerModal = function(modal, appid, appname){
        this.appid = appid;
        this.appname = appname;
        this.modal = modal;
        this.content = this.modal.find('.modal-body .auth-content');
        this.updateBtn = this.modal.find('.updateAuth');
        this.removeAllBtn = this.modal.find('.removeAllAuth');
        var self = this;

        var getObject = function(appid){
            return $.get("/oauth2/api/v1/access-token/"+appid+"/")
        };
        this.show = function(){
            this.content.html("");
            getObject(this.appid).then(function(data){
                self.content.append(_.template($("#managerModal-template").html())(data));
                self.modal.find('.modal-body .loading').hide();
                self.removeAllBtn.unbind("click").click(function(){
                    self.removeAllAuth();
                });
                self.updateBtn.unbind("click").click(function(){
                    self.updateAuth();
                });
            }, function(){

            })
        };

        this.updateAuth = function(){
            self.updateBtn.button('loading');
            var scope = [];
            $.each(modal.find('.modal-body .scopes input[name="scope"]:checked'), function(){
                var s = $(this).val();
                if(s){
                    scope.push($(this).val());
                }
            })
            $.ajax({
                type: "PUT",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                url: "/oauth2/api/v1/access-token/"+self.appid+"/",
                data: $.toJSON({"scope":scope.join(" ")}),
                success: function(){
                    self.updateBtn.button('reset');
                },
                error: function(){
                    self.updateBtn.button('reset');
                    alert("服务器错误");
                }
            });
        };

        self.removeAllAuth = function(){
            if(confirm("您确定要取消对 "+self.appname+" 的所有授权？")){
                this.removeAllBtn.button('loading');
                $.ajax({
                    type: "DELETE",
                    dataType: 'json',
                    contentType: 'application/json;charset=UTF-8',
                    url: "/oauth2/api/v1/access-token/"+self.appid+"/",
                    success: function(){
                        location.reload();
                        self.removeAllBtn.button('reset');
                    },
                    error: function(){
                        self.removeAllBtn.button('reset');
                        alert("服务器错误");
                    }
                });
            }
        };

        return this;
    };

    $('#managerModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var appname = button.data('appname');
        var appid = button.data('appid');
        var modal = $(this);
        modal.find('.modal-title span').text(appname);
        modal.find('.modal-body .loading').show();
        new ManagerModal(modal, appid, appname).show();
    });
})