function QSA(x) {
    return document.querySelectorAll(x);
}
var LINUX = /Linux/.test(navigator.userAgent),
    MACOS = /[^a-z]mac ?os/i.test(navigator.userAgent),
    WINDOWS = /Windows/.test(navigator.userAgent);


var oa = QSA('pre');
for (var a = 0; a < oa.length; a++) {
    var html = oa[a].innerHTML,
        nd = /^ +/.exec(html)[0].length,
        rd = new RegExp('(^|\r?\n) {' + nd + '}', 'g');

    oa[a].innerHTML = html.replace(rd, '$1').replace(/[ \r\n]+$/, '').replace(/\r?\n/g, '<br />');
}

function add_dls() {
    oa = QSA('pre.dl');
    for (var a = 0; a < oa.length; a++) {
        var an = 'ta' + a,
            o = ebi(an) || mknod('a', an, 'download');

        oa[a].setAttribute('id', 'tx' + a);
        oa[a].parentNode.insertBefore(o, oa[a]);
        o.setAttribute('download', oa[a].getAttribute('name'));
        o.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(oa[a].textContent));
        clmod(o, 'txa', 1);
    }
}
add_dls();


oa = QSA('.ossel a');
for (var a = 0; a < oa.length; a++)
    oa[a].onclick = esetos;

function esetos(e) {
    ev(e);
    setos(((e && e.target) || (window.event && window.event.srcElement)).id.slice(1));
}

function setos(os) {
    var oa = QSA('.os');
    for (var a = 0; a < oa.length; a++)
        oa[a].style.display = 'none';

    var oa = QSA('.' + os);
    for (var a = 0; a < oa.length; a++)
        oa[a].style.display = '';

    oa = QSA('.ossel a');
    for (var a = 0; a < oa.length; a++)
        clmod(oa[a], 'g', oa[a].id.slice(1) == os);
}

setos(WINDOWS ? 'win' : LINUX ? 'lin' : MACOS ? 'mac' : 'idk');


ebi('setpw').onclick = function (e) {
    ev(e);
    modal.prompt('password:', '', function (v) {
        if (!v)
            return;

        var pw0 = ebi('pw0').innerHTML,
            oa = QSA('b');
        
        for (var a = 0; a < oa.length; a++)
            if (oa[a].innerHTML == pw0)
                oa[a].textContent = v;

        add_dls();
    });
}
