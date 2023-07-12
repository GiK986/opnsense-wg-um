window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    const datatablesSimple2 = document.getElementById('datatablesSimple2');


    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple, {
            paging: true,
//            scrollY: "50vh",
            firstLast: true,
            rowNavigation: true,
            tabIndex: 1,
//            hiddenHeader: true,
        });
    }

    if (datatablesSimple2) {
        new simpleDatatables.DataTable(datatablesSimple2);
    }
});
