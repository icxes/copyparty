(function() {
    var tab = ebi('tab').tBodies[0],
        tr = Array.prototype.slice.call(tab.rows, 0),
        rows = [];

    for (var a = 0; a < tr.length; a++) {
        var td = tr[a].cells,
            an = td[5].children[0];

        rows.push([
            td[0].textContent,
            td[2].textContent,
            td[3].textContent,
            an.textContent,
            an.getAttribute('href'),
        ]);
    }

    for (var a = 0; a < rows.length; a++) {
        var t = rows[a],
            sz = t[0],
            at = parseInt(t[1]),
            nam = vsplit(t[3]),
            dh = vsplit(t[4])[0];

        tr[a].cells[0].innerHTML = sz.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        tr[a].cells[2].innerHTML = at ? unix2iso(at) : '(?)';
        tr[a].cells[3].innerHTML = at ? shumantime(t[2]) : '(?)';
        tr[a].cells[4].innerHTML = '<a href="' + dh + '">' + nam[0] + '</a>';
        tr[a].cells[5].children[0].innerHTML = nam[1].split('?')[0];
    }

    ebi('hits').innerHTML = '-- showing ' + rows.length + ' files';
})();
