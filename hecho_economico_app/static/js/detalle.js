document.addEventListener('DOMContentLoaded', () => {
    renderTable(detalleData, currentPage);
});

let detalleData = [...document.querySelectorAll('#order-listing tbody tr')].map(row => ({
    id: row.dataset.id,
    producto: row.cells[0].textContent,
    subcuenta: row.cells[1].textContent,
    concepto: row.cells[2].textContent,
    valor: parseFloat(row.cells[3].textContent)
}));

let currentPage = 1;
const rowsPerPage = 5;
let filteredData = [...detalleData];

function renderTable(data, page = 1) {
    currentPage = page;
    const tbody = document.querySelector('#order-listing tbody');
    tbody.innerHTML = '';
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = data.slice(start, end);
    pageData.forEach(item => {
        const row = document.createElement('tr');
        row.dataset.id = item.id;
        row.innerHTML = `
            <td>${item.producto}</td>
            <td>${item.subcuenta}</td>
            <td>${item.concepto}</td>
            <td>${item.valor}</td>
            <td>
                <button onclick="editarDetalle(${item.id})">Editar</button>
                <button onclick="eliminarDetalle(${item.id})">Eliminar</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    updatePaginationControls(data.length);
}

function updatePaginationControls(totalItems) {
    const totalPages = Math.ceil(totalItems / rowsPerPage);
    document.getElementById('page-controls').innerHTML = `
        <button ${currentPage === 1 ? 'disabled' : ''} onclick="prevPage()">Anterior</button>
        <span>Página ${currentPage} de ${totalPages}</span>
        <button ${currentPage === totalPages ? 'disabled' : ''} onclick="nextPage()">Siguiente</button>
    `;
}

function filterTable() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    filteredData = detalleData.filter(item => {
        return Object.values(item).some(value =>
            String(value).toLowerCase().includes(searchText)
        );
    });
    renderTable(filteredData, 1);
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderTable(filteredData, currentPage);
    }
}

function nextPage() {
    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderTable(filteredData, currentPage);
    }
}

function mostrarFormularioAgregar() {
    document.getElementById('formulario-agregar').style.display = 'block';
}

function ocultarFormularioAgregar() {
    document.getElementById('formulario-agregar').style.display = 'none';
}

function agregarDetalle(hecho_econo_id) {
    const producto = document.getElementById('producto').value;
    const subcuenta = document.getElementById('subcuenta').value;
    const concepto = document.getElementById('concepto').value;
    const valor = document.getElementById('valor').value;

    fetch('/agregar-detalle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            hecho_econo: hecho_econo_id,
            producto: producto,
            subcuenta: subcuenta,
            concepto: concepto,
            valor: parseFloat(valor)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            detalleData.push({
                id: data.detalle,
                producto: producto,
                subcuenta: subcuenta,
                concepto: concepto,
                valor: parseFloat(valor)
            });
            filterTable();
            ocultarFormularioAgregar();
        } else {
            alert('Error al agregar detalle: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function eliminarDetalle(detalle_id) {
    fetch(`/eliminar-detalle/${detalle_id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            detalleData = detalleData.filter(item => item.id != detalle_id);
            filterTable();
        } else {
            alert('Error al eliminar detalle: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
