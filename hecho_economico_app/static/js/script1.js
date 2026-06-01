
document.addEventListener('DOMContentLoaded', (event) => {
    
    function eliminar() {
        var x = confirm("¿Está seguro de que desea eliminar el registro?");
        return x;
    }

    var currentRow = 0;
    var rows = document.querySelectorAll('#order-listing tbody tr');
    
    function updateRowVisibility() {
        rows.forEach((row, index) => {
            row.style.display = (index === currentRow) ? 'table-row' : 'none';
        });
    }


    document.getElementById('next').addEventListener('click', () => {
        if (currentRow < rows.length - 1) {
            currentRow++;
            updateRowVisibility();
        }
    });

    // Inicializa la visibilidad de las filas
    updateRowVisibility();

// Agrega un manejador de eventos al botón Limpiar
    document.getElementById('Limpiar').addEventListener('click', function() {
        // Limpia los campos seleccionándolos por su id
        document.getElementById('txtConcepto').value = '';
        document.getElementById('txtSubCuenta').value = '';
        document.getElementById('txtDebito').value = '';
        document.getElementById('txtCredito').value = '';
        document.getElementById('txtValor1').value = '';
        document.getElementById('txtValor2').value = '';
        document.getElementById('txtDetalle').value = '';
        document.getElementById('cboCanal').value = 'CHE';
    });


    document.getElementById('Agregar').addEventListener('click', function() {
        var nuevaFila = document.createElement('tr');
        var nvoConcepto = document.getElementById('txtConcepto').value;
        var nvoSubCuenta = document.getElementById('txtSubCuenta').value;
        var nvoDebito = document.getElementById('txtDebito').value;
    
        // Agrega las celdas a la fila
        nuevaFila.innerHTML = `
            <td>AP</td>
            <td>${nvoConcepto}</td>
            <td>${nvoSubCuenta}</td>
            <td>${nvoDebito}</td>
            <td>Por Identificar</td>
            <td>
                <div class="btn-group">
                    <button title="Editar" type="button" class="btn btn-light rounded-pill"><i class="bi bi-pencil-square"></i> Editar</button>
                    <button title="Detalle" type="button" class="btn btn-light rounded-pill"><i class="bi bi-eye"></i> Detalle</button>
                    <button title="Eliminar" class="btn btn-light rounded-pill" onclick="return eliminar();" type="button"><i class="bi bi-trash3"></i> Eliminar</button>
                </div>
            </td>
        `;
        // Agrega la nueva fila a la tabla
        document.getElementById('order-listing').appendChild(nuevaFila);
    });



    document.querySelector('.filtrar').addEventListener('click', function() {
        alert('Filtrar');
    });

    document.querySelector('.nuevo').addEventListener('click', function() {
        alert('Nuevo');
    });

    document.querySelector('.grabar').addEventListener('click', function() {
        alert('Grabar');
    });

    document.querySelector('.imprimir').addEventListener('click', function() {
        alert('Imprimir');
    });

    document.querySelector('.eliminar').addEventListener('click', function() {
        alert('Eliminar');
    });


    function enviarDatosAlServidor(data) {
        // Enviar los datos mediante una solicitud AJAX
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'tu_url_del_servidor');
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200) {
            // Procesar la respuesta del servidor si es necesario
                console.log('Datos enviados correctamente.');
            } else {
                console.error('Error al enviar datos al servidor.');
            }
        };
        xhr.send(JSON.stringify(data));
    }

    // Obtener el elemento del campo de entrada
    const inputValor2 = document.getElementById('txtValor2');

    // Agregar un listener para el evento de entrada
    inputValor2.addEventListener('input', function() {
        // Obtener el valor actual del campo de entrada
        let value = this.value;
        value = FormatoMoneda.formatearComoMoneda(value);
        this.value = value;
    });
});

