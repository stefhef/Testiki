var ip = location.host;
let input = document.querySelector("#message");
let el = document.querySelectorAll("div.d-flex.flex-row");
el[el.length - 1].scrollIntoView(false);


function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

var socket = new WebSocket(`ws://${ip}/messenger/ws?client_id=${getCookie("user_id")}`);

function form_message(text, id, color) {
    let n_m = document.querySelector("#n_msg");
    if (n_m) {
        n_m.remove();
    }
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/messenger/data/?id=" + id, false);
    xmlHttp.send(null);
    let resp = xmlHttp.responseText.split(',');
    let dv1 = `<div style="color: ${color}" class="d-flex flex-row flex-fill">`;
    let photo = '<div class="photo msg" style="width: 60px; height: 60px; margin: 10px"><img\n' +
        '                                src="data:image/jpeg;base64,' + resp[1].slice(1, -1) + '"\n' +
        '                                alt="Фото профиля"\n' +
        '                                class="personphoto"></div>'
    let p1 = `<div class="d-flex flex-column flex-fill"><p class=\"info\">${resp[0].slice(2, -1)} ${moment().format("YYYY-MM-DD HH:mm:ss")}</p>`;
    let p2 = `<p class="text-break message">${text}</p></div></div>`;
    document.querySelectorAll("#container")[0].insertAdjacentHTML("beforeend", dv1 + photo + p1 + p2);
    input.value = "";
    let el = document.querySelectorAll("div.d-flex.flex-row");
    el[el.length - 1].scrollIntoView(false);
}


function send_message() {
    let input = document.getElementById("message");
    if (!input.value) {
        return
    }
    const to_id = document.getElementById("user").href.split("/");
    socket.send(`${input.value};${to_id[to_id.length - 1]}`)
    // let xmlHttp = new XMLHttpRequest();
    // xmlHttp.open("POST", `/messenger/send_message/?msg=${input.value}&from_id=${getCookie("user_id")}&to_id=${to_id[to_id.length - 1]}`, true);
    // xmlHttp.send(null);
    form_message(input.value, getCookie("user_id"), "gray")
}

function sm(e) {
    if (e.code === 'Enter') {
        send_message();
    }
}

input.addEventListener('keyup', sm);


function processMessage(event) {
    console.log("Сообщение пришло")
    form_message(event.data, getCookie("user_id"), "blue")
}

socket.onmessage = processMessage;

