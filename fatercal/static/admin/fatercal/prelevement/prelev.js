var $ = django.jQuery;

$(document).ready(function(){
    $('input[id=id_date').on('input',function(e){
        date_check()
    });
});

function Date_update(date) {
    if (date=='unique'){
        var date = document.getElementById("date_1");
        document.getElementById("id_date").value = date.value;
    }else if (date=='periode'){
        var date_periode_1 = document.getElementById("date_periode_1");
        var date_periode_2 = document.getElementById("date_periode_2");
        if (date_periode_1 != null && date_periode_2 != null){
            if (new Date(date_periode_1.value).getTime() < new Date(date_periode_2.value).getTime()){
                document.getElementById("id_date").value = date_periode_1.value + '/' + date_periode_2.value;
            } else if(new Date(date_periode_1.value).getTime() > new Date(date_periode_2.value).getTime()){
                document.getElementById("id_date").value = date_periode_2.value + '/' + date_periode_1.value;
            }
        }
    }
    date_check()
}

function date_check(){
    var regex_1 = new RegExp(/(^\d{4}$)|(^\d{4}-(0[1-9]|1[0-2])$)|(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|(^$)/g)
    var regex_2 = new RegExp(/(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)/g)
    elem = document.getElementById("id_date").value
    if (regex_1.test(elem) || regex_2.test(elem)){
        var str = 'Le date est de la bonne forme';
        var good = true;
    } else{
        var str = "La date n'est pas sous la bonne forme. Ex : 1850, 1850-12, 1850-12-01, 1850-12-01/1850-12-01";
        var good = false;
    }
    var element =  document.getElementById('date_note');
    if (typeof(element) != 'undefined' && element != null){
        if (good){
            element.className = 'success';
            element.innerHTML = str;
        }else{
            element.className = 'errornote';
            element.innerHTML = str;
        }
    } else {
        var messageEl = document.createElement('LI');
        if (good){
            messageEl.className = "success";
        } else {
            messageEl.className = "errornote";
        }
        messageEl.id = 'date_note';
        messageEl.innerHTML = str;
        var br = document.createElement('BR');
        document.getElementsByClassName('form-row field-date').item(0).appendChild(br);
        document.getElementsByClassName('form-row field-date').item(0).appendChild(messageEl);
    }
}