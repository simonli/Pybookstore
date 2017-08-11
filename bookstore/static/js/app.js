function get_dept_list() {
    var division_id = $("#division_id").val();
    if (division_id > 0) {
        $("#department_id").empty();
        $.ajax({
            url: '/admin/_get_departments',
            type: 'POST',
            data: {'division_id': division_id},
            success: function (data) {
                var depts = data.result;
                $("#department_id").append("<option value='0'>请选择所属修学点</option>");
                for (var i = 0; i < depts.length; i++) {
                    $("#department_id").append("<option value='" + depts[i]['id'] + "'>" + depts[i]['name'] + "</option>");
                }
            }
        });
    }
}

function get_class_list() {
    var department_id = $("#department_id").val();
    if (department_id > 0) {
        $("#class_id").empty();
        $.ajax({
            url: '/admin/_get_classes',
            type: 'POST',
            data: {'department_id': department_id},
            success: function (data) {
                var classes = data.result;
                $("#class_id").append("<option value='0'>请选择所属班级</option>");
                for (var i = 0; i < classes.length; i++) {
                    $("#class_id").append("<option value='" + classes[i]['id'] + "'>" + classes[i]['name'] + "</option>");
                }
            }
        });
    }
}

function confirm_delete(url) {
    $.confirm({
        title: '⚠️ 警告',
        content: '此操作不可恢复，确认删除吗？',
        type: 'red',
        typeAnimated: true,
        buttons: {
            confirm: {
                text: '删除',
                btnClass: 'btn-danger',
                action: function () {
                    location.href = url;
                }
            },
            cancel: {
                text: '取消',
                btnClass: 'btn-default',
                action: function () {
                }
            }
        }
    });
}

$('#form').submit(function (e) {
    var keyword = $('#keyword')
    if(keyword.val()==undefined){
        $('msg').text('关键词不能为空').show().fadeOut(2000);
        event.preventDefault()

    }

})
