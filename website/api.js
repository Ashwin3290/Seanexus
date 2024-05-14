var base_url = "http://127.0.0.1:5000";

function signupUser() {
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    const requestData = {
        name: name,
        email: email,
        password: password
    };

    fetch(base_url+"/signup", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.user_id) {
            sessionStorage.setItem('user_id', data.user_id);
            window.location.replace("user.html");
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error: " + error);
    });
}


function loginUser() {
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    const requestData = {
        email: email,
        password: password
    };
    fetch(base_url+"/login", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.ok) {
            sessionStorage.setItem('vendor_id', data.vendor_id);
            window.location.replace("user.html");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error: " + error);
    });
}

function makeTransaction() {
    const shipmentWeight = document.getElementById('shipment-weight').value;
    const catchTime = document.getElementById('catch-time').value;
    // const vendorId = sessionStorage.getItem('vendor_id');
    const vendorId = 683503;
    const ipAddress = window.location.hostname;
    const requestData = {
        function: "pushData",
        args: [vendorId, shipmentWeight, ipAddress, catchTime]
    };
    console.log(requestData);

    fetch(base_url+'/invoke', {
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
    fetch(base_url+'/decode_qr_code', {
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
    const data = {
        function: 'queryDataByVendorID',
        args: [vendorId]
    };

    fetch(base_url+'/query', {
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
