function addDetalleProd() {
    var form = document.getElementById('detalleProdForm');
    var formData = new FormData(form);

    fetch("{% url 'detalle_prod_create' object.id %}", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": formData.get('csrfmiddlewaretoken')
        }
    }).then(response => response.json()).then(data => {
        if (data.success) {
            var newRow = document.createElement('tr');
            newRow.id = 'detalle-' + data.id;
            newRow.innerHTML = `
                <td>${data.concepto}</td>
                <td>${data.subcuenta}</td>
                <td>${data.valor}</td>
                <td>
                    <a href="/detalle_prod_update/${data.id}">Editar</a>
                    <a href="/detalle_prod_delete/${data.id}">Eliminar</a>
                </td>`;
            document.getElementById('detalleProdTable').querySelector('tbody').appendChild(newRow);
        } else {
            alert('Error al agregar detalle');
        }
    });
}
