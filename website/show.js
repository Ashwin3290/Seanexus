document.addEventListener('DOMContentLoaded', function() {
    const decodedData = sessionStorage.getItem('decodedData');
    if (!decodedData) {
        console.error('No decoded data found.');
        return;
    }
    const data = JSON.parse(decodedData);
    const dataTable = document.getElementById('data-table');
    const tableRow = document.createElement('tr');
    tableRow.innerHTML = `
        <td>${data.catchWeight}</td>
        <td>${data.dateTime}</td>
        <td>${data.location}</td>
        <td>${data.vendorID}</td>
    `;
    dataTable.appendChild(tableRow);
});
