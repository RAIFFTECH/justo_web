console.log("Compobantes 2 Se ha cargado");

async function initializeDataTables() {
    const response = await fetch(`/comprobantes/get_hecho_econos/11377?page=1`);
    if (!response.ok) {
        console.error("Error fetching data");
        return;
    }

    const data = await response.json();
    const hechoEconomico = data.data.hecho_econo;
    const detallesProd = data.data.detalles_prod;
    const detalleTableBody = document.querySelector("#detalle_prod_table tbody");
    detalleTableBody.innerHTML = "";
    addHechoRowToTable(hechoEconomico);
    /*detallesProd.forEach(addDetalleRowToTable);*/
    detallesProd.forEach(agregarFilas);

    function addHechoRowToTable(element) {
        cboDocto.value = element.docto_conta_id;
        txtNumero.value = element.numero;
        txtFecha.value = element.fecha;
        txtDescripcion.value = element.descripcion;
        cboCanal.value = element.canal;
        if (element.protegido === "S" ) {
            chkProtegido.checked = true;
        }
        else {
            chkProtegido.checked = false;
        }
        if (element.anulado === "S" ) {
            chkAnulado.checked = true;
        }
        else {
            chkAnulado.checked = false;
        }
    }

    function addDetalleRowToTable(element) {
    /*    const template = document.getElementById("detalle_prod_template").content.cloneNode(true);  */
        const template = document.getElementById("detalle_prod_template").content.cloneNode(true);
        let newHTML = template.firstElementChild.outerHTML;
        newHTML = newHTML.replace("[id]", element.id);
        newHTML = newHTML.replace("[producto]", element.producto);
        newHTML = newHTML.replace("[concepto]", element.concepto);
        newHTML = newHTML.replace("[subcuenta]", element.subcuenta);
        if (element.valor > 0){
            newHTML = newHTML.replace("[debito]", element.valor);    
            newHTML = newHTML.replace("[credito]", 0);    
        } else{
            newHTML = newHTML.replace("[debito]", 0);    
            newHTML = newHTML.replace("[credito]", -element.valor);
        }
        newHTML = newHTML.replace("[valor_1]", 0);
        newHTML = newHTML.replace("[valor_2]", 0);
        detalleTableBody.insertAdjacentHTML('beforeend', newHTML);
    }

    function agregarFilas(element) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${element.producto}</td>
            <td>${element.concepto}</td>
            <td>${element.subcuenta}</td>
            <td>${element.valor}</td>
            <td>${element.valor}</td>
        `;
        const actionsCell = row.lastElementChild;
        const editarLink = document.createElement('a');
        editarLink.href = '#';
        editarLink.title = 'Editar';
        editarLink.type = 'button';
        editarLink.classList.add('btn', 'btn-light', 'rounded-pill');
        editarLink.innerHTML = '<i class="bi bi-pencil-square"></i>';
        const detallesLink = document.createElement('a');
        detallesLink.href = element.id ; // Suponiendo que tienes un ID en tus datos
        detallesLink.title = 'Detalle';
        detallesLink.type = 'button';
        detallesLink.classList.add('btn', 'btn-light', 'rounded-pill');
        detallesLink.innerHTML = '<i class="bi bi-eye"></i>';
        const eliminarButton = document.createElement('button');
        eliminarButton.title = 'Eliminar';
        eliminarButton.classList.add('btn', 'btn-light', 'rounded-pill');
        eliminarButton.onclick = function () { return eliminar(); };
        eliminarButton.type = 'submit';
        eliminarButton.innerHTML = '<i class="bi bi-trash3"></i>';
        actionsCell.appendChild(editarLink);
        actionsCell.appendChild(detallesLink);
        actionsCell.appendChild(eliminarButton);
        detalleTableBody.appendChild(row);        
    }
}


document.addEventListener("DOMContentLoaded", initializeDataTables);

function toggleCheckbox(checkboxId, newValue) {
    var checkbox = document.getElementById(checkboxId);
    if (checkbox && checkbox.type === "checkbox") {
        checkbox.checked = (newValue === "S");
        checkbox.value = newValue;
    } else {
        console.error("El elemento con el ID " + checkboxId + " no es un checkbox.");
    }
}