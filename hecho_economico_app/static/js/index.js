console.log("JavaScript ha sido cargada 2");
alert("RaiffTechSas 3");

document.addEventListener('DOMContentLoaded', async () => {
    var dataElement = document.getElementById('django-data');
    var data = JSON.parse(dataElement.getAttribute('data-json'));
    await cargaInicial();
    cboDocto.value = data.docto_conta_id;
    txtNumero.value = data.numero;
    txtFecha.value = data.fecha;
    txtDescripcion.value = data.descripcion;
    cboCanal.value = data.canal;
    const table = document.getElementById('order-listing');
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    data.items.forEach(item => {
        if (item.valor > 0) {
            txtDebito.value = item.valor;
        }

        const row = document.createElement('tr');
        row.className = (data.items.indexOf(item) % 2 === 0) ? 'even' : 'odd';
        row.id = `row-${item.id}`; // Asignar un id único a cada fila
        row.innerHTML = `
            <td>${item.producto}</td>
            <td>${item.concepto}</td>
            <td>${item.subcuenta}</td>
            <td>${item.valor}</td>
            <td>${item.tercero}</td>
            <td>
                <form method="POST" action="eliminar/${item.id}">
                    <div class="btn-group">
                        <a href="actualizar/${item.id}" title="Editar" type="button" class="btn btn-light rounded-pill"><i class="bi bi-pencil-square"></i> Editar</a>
                        <a href="detalles/${item.id}" title="Detalle" type="button" class="btn btn-light rounded-pill"><i class="bi bi-eye"></i> Detalle</a>
                        <button title="Eliminar" class="btn btn-light rounded-pill" onclick="return eliminar();" type="submit"><i class="bi bi-trash3"></i> Eliminar</button>
                    </div>
                </form>
            </td>
        `;
        tbody.appendChild(row);
    });

});

const listaDocumentos = async() => {
    try {
        const response = await fetch("../documentos/2023");
        const data = await response.json();
        if (data.message == "Correcto"){
            cboDocto.innerHTML = ''
            data.doctos.forEach(docto => {
                const option = document.createElement('option');
                option.value = docto.id; // Establecer el valor como el ID del documento
                option.textContent = docto.nombre;
                cboDocto.appendChild(option);
            });
        } else {
            alert("No hay Documentos para esta Vigencia")
        }
    } catch (error){
        console.log(error);
    }
}

const listaCanales = async() => {
    try {
        const response = await fetch("../canales");
        const data = await response.json();
        if (data.message == "Correcto"){
            let opciones = "";
            data.canales.forEach(canal => {
                opciones += `<option value='${canal.codigo}'>${canal.nombre}</option>`;
            });
            cboCanal.innerHTML = opciones;
        } else {
            alert("No hay Canales como Opcion")
        }
    } catch (error){
        console.log(error);
    }
    console.log("Valor de canal-->",cboCanal.options.length);

}

const listaCiudades = async() => {
    try {
        const response = await fetch("../ciudades");
        const data = await response.json();
        console.log(data)
        if (data.message == "Correcto"){
            let opciones = ``;
            data.localidades.forEach(ciudad => {
                opciones+= `<option value='$ciudad.id'>${ciudad.nombre+"-"+ciudad.departamento}</option>`;
            });
            cboCiudad.innerHTML = opciones;
        } else {
            alert("No hay Ciudades para esta Vigencia")
        }
    } catch (error){
        console.log(error);
    }
}


const listaBancos = async() => {
    try {
        const response = await fetch("../bancos");
        const data = await response.json();
        console.log(data)
        if (data.message == "Correcto"){
            let opciones = ``;
            data.bancos.forEach(banco => {
                opciones+= `<option value='$banco.id'>${banco.nom_cta}</option>`;
            });
            cboBanco.innerHTML = opciones;
        } else {
            alert("No hay Bancos registrados para esta Vigencia")
        }
    } catch (error){
        console.log(error);
    }
}


const cargaInicial = async () => {
    await listaDocumentos();
    await listaCanales();
    await listaCiudades();
    await listaBancos();
    document.getElementById("cboCanal").value = "{{ data.canal }}";
};