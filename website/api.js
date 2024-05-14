function signupUser() {
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    $.ajax({
        type: "POST",
        url: "/signup",
        contentType: "application/json",
        data: JSON.stringify({ name: name, email: email, password: password }),
        success: function(response) {
            alert(response.message);
            // window.location.href = "/login";
        },
        error: function(xhr, status, error) {
            alert("Error: " + xhr.responseText);
        }
    });
}

// Function to handle login
function loginUser() {
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    $.ajax({
        type: "POST",
        url: "/login",
        contentType: "application/json",
        data: JSON.stringify({ email: email, password: password }),
        success: function(response) {
            alert(response.message);
            if (response.ok) {
                sessionStorage.setItem('username', email);
                sessionStorage.setItem('password', password);
                // window.location.href = "/dashboard";
            }
        },
        error: function(xhr, status, error) {
            alert("Error: " + xhr.responseText);
        }
    });
}
function makeTransaction() {
    const shipmentWeight = document.getElementById('shipment-weight').value;
    const catchTime = document.getElementById('catch-time').value;
    const vendorId = sessionStorage.getItem('vendorId'); 
    const requestData = {
        function: "pushData",
        args: [vendorId, shipmentWeight, "ipAddress", catchTime]
    };

    fetch('/invoke', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        sessionStorage.setItem('qrCodeURL', data.qrCodeURL);
        window.location.href = 'qrcode.html';
    })
    .catch(error => console.error('Error:', error));
}

function submitQRCode() {
    const qrCodeInput = document.getElementById('qr-code-input');
    if (qrCodeInput.files.length === 0) {
        alert('Please select a file.');
        return;
    }
    const formData = new FormData();
    formData.append('qr_image', qrCodeInput.files[0]);
    fetch('/decode_qr_code', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        sessionStorage.setItem('decodedData', JSON.stringify(data));
        window.location.href = 'show.html';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing the QR code.');
    });
}

function fetchTransactionDetails(vendorId) {
    const url = '/query';
    const data = {
        function: 'queryData',
        args: [vendorId]
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayTransactionDetails(data.result);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while fetching transaction details.');
    });
}

function fetchTransactionDetails(vendorId) {
    const url = '/query';
    const data = {
        function: 'queryDataByVendorID',
        args: [vendorId]
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayTransactionDetails(data.result);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while fetching transaction details.');
    });
}
