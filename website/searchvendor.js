function searchTransactions() {
    const vendorId = document.getElementById('vendor-id-input').value.trim();
    if (!vendorId) {
        alert('Please enter a vendor ID.');
        return;
    }

    fetchTransactionDetails(vendorId);
}

function displayTransactionDetails(transactionDetails) {
    const transactionTable = document.getElementById('transaction-table');
    if (!transactionDetails || transactionDetails.length === 0) {
        transactionTable.innerHTML = '<p>No transactions found for this vendor ID.</p>';
        return;
    }

    // Construct table HTML
    let tableHTML = '<table>';
    tableHTML += '<tr><th>Transaction ID</th><th>Catch Weight</th><th>Date & Time</th><th>Location</th></tr>';
    transactionDetails.forEach(transaction => {
        tableHTML += `<tr><td>${transaction.transaction_id}</td><td>${transaction.weight}</td><td>${transaction.datetime}</td><td>${transaction.location}</td></tr>`;
    });
    tableHTML += '</table>';

    // Display table
    transactionTable.innerHTML = tableHTML;
}
