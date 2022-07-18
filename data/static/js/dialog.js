let input = document.querySelector("#message");
let el = document.querySelectorAll("div.d-flex.flex-row");
el[el.length - 1].scrollIntoView(false);

function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function form_message(text, id) {

    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/messenger/data/?id=" + id, false);
    xmlHttp.send(null);
    let resp = xmlHttp.responseText.split(',');
    let dv1 = '<div style="color: gray" class="d-flex flex-row flex-fill">';
    let photo = '<div class="photo msg" style="width: 60px; height: 60px; margin: 10px"><img\n' +
        '                                src="data:image/jpeg;base64,' + resp[1].slice(1, -1) + '"\n' +
        '                                alt="Фото профиля"\n' +
        '                                class="personphoto"></div>'
    let p1 = '<div class="d-flex flex-column flex-fill"><p class=\"info\">' + resp[0].slice(2, -1) + ' ' + moment().format("YYYY-MM-DD HH:mm:ss") + '</p>';
    let p2 = '<p class="text-break message">' + text + '</p></div>';
    let dv2 = '</div>';
    return dv1 + photo + p1 + p2 + dv2;
}


function send_message() {
    let input = document.getElementById("message");
    const to_id = document.getElementById("user").href.split("/");
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "/messenger/send_message/?msg=" + input.value + "&from_id=" + getCookie("user_id") + "&to_id=" + to_id[to_id.length - 1], true);
    xmlHttp.send(null);
    let cont = document.querySelectorAll("#container")[0];
    cont.insertAdjacentHTML("beforeend", form_message(input.value, getCookie("user_id")));
    input.value = "";
    let el = document.querySelectorAll("div.d-flex.flex-row");
    el[el.length - 1].scrollIntoView(false);
}

function sm(e) {
    if (e.code === 'Enter') {
        send_message();
    }
}

input.addEventListener('keyup', sm);




