/*!
    * Start Bootstrap - SB Admin v7.0.5 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2022 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});

function share(uuid, event) {
    // Send a POST request to the /share endpoint
    fetch('/share', { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({uuid: uuid}) })
      .then(response => response.json())
      .then(data => {
        // Copy the URL to the user's clipboard

        copyToClipboard(data.share_url);
    });

    event.currentTarget.innerText = 'copy to Clipboard '
    event.currentTarget.innerHTML += '<i class="fas fa-circle-check"></i>'
}

async function copyToClipboard(text) {
    try {
      // Try to use navigator.clipboard (if available)
      await navigator.clipboard.writeText(text);
    } catch (err) {
      // Fall back to document.execCommand('copy')
      const input = document.createElement('input');
      input.value = text;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    }
}
const modal = document.getElementById("search-results-modal");
const resultsList = document.getElementById("search-results");
const form = document.getElementById("search-form");
const input = document.getElementById("search-input");
const close = document.getElementsByClassName("btn-close")[0];
const modalTitle = document.getElementsByClassName("modal-title")[0]

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = input.value;
  fetch(`/search?q=${encodeURIComponent(query)}`)
    .then((response) => response.json())
    .then((data) => {
      resultsList.innerHTML = "";
      data.forEach((result) => {
        const li = document.createElement("li");
        li.className = "list-group-item"
        li.innerHTML = `<a class="nav-link" href="${result.url}">${result.title}</a>`;
        resultsList.appendChild(li);
      });
      modalTitle.innerText = `Search for "${query}"`
      modal.style.display = "block";
    });
});

close.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (event) => {
  if (event.target == modal) {
    modal.style.display = "none";
  }
});

const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
if (confirmDeleteBtn) {
    confirmDeleteBtn.onclick = (event) => {
          url = event.currentTarget.baseURI;
          fetch(url, { method: "DELETE" })
            .then((response) => response.json())
            .then((data) => {
              // Handle the response from the server
              // ...
              if (data) {
                window.location.replace("/");
              }

            });
          $("#confirmDeleteModal").modal("hide");
        };
}

const confirmReconfigurationBtn = document.getElementById("confirmReconfigurationBtn");
if (confirmReconfigurationBtn) {
    confirmReconfigurationBtn.onclick = (event) => {
          url = event.currentTarget.baseURI + '/reconfiguration';
          const interface_uuid = document.querySelector('#interface').value
          const add_qr_code = Boolean(document.querySelector('#add_qr_code').value)
          const allowed_ips_group = Number(document.querySelector('#allowed_ips_group').value)

          fetch(url, { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({interface_uuid: interface_uuid,
                                            allowed_ips_group: allowed_ips_group,
                                            add_qr_code: add_qr_code
                                            }) })
            .then((response) => response.json())
            .then((data) => {
              // Handle the response from the server
              // ...
              if (data) {
                window.location.replace("/");
              }

            });
          $("#confirmReconfigurationModal").modal("hide");
        };
}


function calculate_allowed_ips(event) {
    const allowed_ips = document.getElementById('id_allowed_ips').value;
    const disallowed_ips = document.getElementById('id_disallowed_ips').value;
    const button = document.querySelector("button.btn.btn-primary.btn-block");
    const allowed_ips_calculated = document.getElementById('id_allowed_ips_calculated')
    button.disabled = true;

    allowed_ips_calculated.value = '';

    fetch('/wg_users/calculate_allowed_ips/', { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({allowed_ips: allowed_ips, disallowed_ips: disallowed_ips}) })
      .then(response => response.json())
      .then(data => {
        allowed_ips_calculated.value = data.allowed_ips_calculated
        button.disabled = false;
    });

}