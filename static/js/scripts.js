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
    fetch('/wg_users/get_qrcode_link/', { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({wg_user_uuid: uuid}) })
      .then(response => response.json())
      .then(data => {
        // Copy the URL to the user's clipboard

        copyToClipboard(data.link);

    });

    event.currentTarget.innerText = 'copied to Clipboard ';
    event.currentTarget.innerHTML += '<i class="fas fa-circle-check"></i>';
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
  fetch(`/wg_users/search/${encodeURIComponent(query)}/`)
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

function deleteWgUser(uuid, event) {
    // Send a DELETE request to the /wg_users/<uuid> endpoint
    fetch(`/wg_users/delete/${uuid}/`, { method: 'DELETE' })
      .then(response => response.json())
      .then(data => {
        // Refresh the page
        window.location.replace(document.referrer);
    });
    $("#confirmDeleteModal").modal("hide");
}

const confirmReconfigurationBtn = document.getElementById("confirmReconfigurationBtn");
if (confirmReconfigurationBtn) {
    confirmReconfigurationBtn.onclick = (event) => {
          url = event.currentTarget.baseURI + 'reconfiguration/';
          const interface_uuid = document.querySelector('#interface').value
          const allowed_ips_group = document.querySelector('#allowed_ips_group').value

          fetch(url, { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({interface_uuid: interface_uuid,
                                            allowed_ips_group: allowed_ips_group
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

function test_connection(event) {
    event.preventDefault();

    const alert = document.querySelector("#message");
    alert.classList.add("alert-danger");
    alert.classList.remove("alert-success");
    alert.innerHTML = '';

    const card_footer = document.querySelector(".card-footer");
    card_footer.classList.add("d-none");

    const add_api_client = document.querySelector("#add-api-client");
    add_api_client.className = "btn btn-outline-primary"
    add_api_client.disabled = true;

    const btn_test_connection = document.querySelector("#btn-test-connection");
    btn_test_connection.innerHTML = 'Test Connection <i class="fa-solid fa-spinner fa-spin"></i>'

    const url = event.currentTarget.baseURI + '/test_connection/';
    const base_url = document.querySelector('#id_base_url').value;
    const api_key = document.querySelector('#id_api_key').value;
    const api_secret = document.querySelector('#id_api_secret').value;

    const re = new RegExp("^(http|https)://[\\w+\\.-]+/api$", "gmi");
    if (!re.test(base_url)) {
        add_api_client.className = "btn btn-outline-danger"

        alert.innerHTML = 'The base URL must start with http:// or https:// and end with /api';
        card_footer.classList.remove("d-none");
        btn_test_connection.innerHTML = 'Test Connection';
        return;
    }

    fetch('/opnsense_api_clients/test_connection', { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ base_url: base_url, api_key: api_key, api_secret: api_secret }) })
      .then(response => response.json())
      .then(data => {
        // Handle the response from the server
        btn_test_connection.innerHTML = 'Test Connection';

        if (data.status == 'success') {
            add_api_client.className = "btn btn-outline-success"
            add_api_client.disabled = false;

            alert.classList.remove("alert-danger");
            alert.classList.add("alert-success");
            alert.innerHTML = data.message;
            card_footer.classList.remove("d-none");
        }
        else {
            add_api_client.className = "btn btn-outline-danger"
            add_api_client.disabled = true;

            alert.innerHTML = data.message;
            card_footer.classList.remove("d-none");
        }
    });
}

function parseIniFile(event) {
    event.preventDefault();
    const alert = document.querySelector("#message");
    alert.innerHTML = '';

    const card_footer = document.querySelector(".card-footer");
    card_footer.classList.add("d-none");
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
      const contents = e.target.result;
      let lines = contents.split('\n');
      let isAddedKey = false;
      let isAddedSecret = false;
      for (var i = 0; i < lines.length; i++) {
        let parts = lines[i].split('=');
        if (parts[0] == 'key') {
          document.getElementById('id_api_key').value = parts[1];
          isAddedKey = true;
        } else if (parts[0] == 'secret') {
          document.getElementById('id_api_secret').value = parts[1];
          isAddedSecret = true;
        }
      }

      if (isAddedKey && isAddedSecret) {
        alert.innerHTML = 'The file was successfully parsed. Please click on the "Test Connection" button to verify the connection.';
        alert.classList.remove("alert-danger");
        alert.classList.add("alert-success");
        card_footer.classList.remove("d-none");
        fileInput.value = '';
      } else {
        alert.innerHTML = 'The file is not a valid OPNsense API client configuration file.';
        card_footer.classList.remove("d-none");
      }

    };

  reader.readAsText(file);
}

function sendEmail(event, wg_user_uuid) {
    const url = '/wg_users/send_email/' + wg_user_uuid + '/';
    const email = document.querySelector('#email').value

    fetch(url, { method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({email: email}) })
        .then(response => response.json())
        .then(data => {
            window.location.replace(document.referrer);
        });

    const sendEmailModal = new bootstrap.Modal(document.getElementById('sendEmailModal'), {});
    sendEmailModal.hide();
}