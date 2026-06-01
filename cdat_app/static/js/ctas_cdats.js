
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("AdiAmpliacion").addEventListener("click", function() {
        // Obtener valores de los campos
        let ampliacion = document.getElementById("ampliacion").value;
        let valor_cdat = document.getElementById("id_valor").value;
        let fecha = document.getElementById("id_fecha_amp").value;  // Asegúrate de que este ID es correcto
        let tiae = document.getElementById("id_tiae_amp").value;  // Asegúrate de que este ID es correcto
        let plazo_mes = document.getElementById("id_plazo_mes").value
       
        if (!valor_cdat ||!ampliacion || !fecha || !tiae || !plazo_mes) {
            alert("Por favor, complete todos los campos antes de agregar.");
            return;
        }
        if (tiae <= 0 || plazo_mes <=0) {
            alert("valor Incorrecto en la tasa de Interes o  plazo en mese.");
        }
        let tableBody = document.querySelector(".table tbody");
        let noDataRow = document.getElementById("no-ampliaciones");
        if (noDataRow) {
            noDataRow.remove();
        }
        let filas = tableBody.getElementsByTagName("tr");
        let filaExistente = null;

        for (let fila of filas) {
            let celdaAmpliacion = fila.cells[0]; // Primera celda con el valor de ampliación
            if (celdaAmpliacion.textContent.trim() === ampliacion) {
                filaExistente = fila;
                break;
            }
        }

        if (filaExistente) {
            // Si ya existe, actualizar los valores
            filaExistente.cells[1].textContent = fecha;
            filaExistente.cells[2].textContent = valor_cdat;
            filaExistente.cells[3].textContent = plazo_mes;
            filaExistente.cells[4].textContent = tiae;
        } else {
            // Si no existe, agregar una nueva fila
            let newRow = document.createElement("tr");
            newRow.innerHTML = `
                <td>${ampliacion}</td>
                <td>${fecha}</td>
                <td>${valor_cdat}</td>
                <td>${plazo_mes}</td>
                <td>${tiae}</td>
                <td>No</td>
                <td>
                    <a href="#" class="btn btn-sm btn-success">
                        <i class="fas fa-print"></i>
                    </a>
                    <a href="#" class="btn btn-sm btn-danger" onclick="eliminarFila(this)">
                        <i class="fas fa-trash"></i>
                    </a>
                </td>`;
            tableBody.appendChild(newRow);
        }
        return;
        });
    });

function eliminarFila(btn) {
    let row = btn.closest("tr");
    row.remove();
    let tableBody = document.querySelector(".table tbody");
    if (tableBody.children.length === 0) {
        tableBody.innerHTML = `<tr id="no-ampliaciones"><td colspan="7">No hay ampliaciones</td></tr>`;
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const linAhoSelect = document.querySelector("[name='lin_aho']");
    const num_cta = document.querySelector("[name='num_cta']");
    const cod_imp = document.querySelector("[name='cod_imp']");
    const currencyInput = document.querySelector('.currency');  // Mover aquí para asegurar que se declare en un solo lugar

    // Manejo del evento 'change' en linAhoSelect
    if (linAhoSelect) {
        linAhoSelect.addEventListener('change', function() {
            const linahoId = linAhoSelect.value; // Asegúrate de obtener el valor correcto
            if (!linahoId) {
                return;
            }
            const url = `${window.location.origin}/cta_ahorro/max-consecutivo/?lin_aho_id=${linahoId}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.max_consecutivo) {
                        num_cta.value = data.max_consecutivo; // Asegúrate de que num_cta esté definido en tu HTML
                        cod_imp.value = data.max_consecutivo.substring(0, 2);
                    } else {
                        console.error('Error:', data.error);
                    }
                })
                .catch(error => console.error('Error fetching data:', error));
        });
    }

    const decimalInputs = document.querySelectorAll('.numericInput');
    decimalInputs.forEach(input => {
        input.addEventListener('blur', function() {
            let value = parseFloat(input.value); // Convierte a número
            if (!isNaN(value)) { // Verifica que el valor sea un número
                input.value = value.toFixed(3); // Formatea a 4 decimales
            }
        });
    });

    // Formato de entrada de moneda
    function formatCurrencyInput(input) {
        let value = input.value.replace(/[^\d]/g, '');  // Elimina todo lo que no sea número
        if (value) {
            input.value = '$ ' + parseInt(value, 10).toLocaleString('es-ES');  // Formato sin decimales
        }
    }

    // Manejo del campo de entrada de moneda
    if (currencyInput) {
        currencyInput.addEventListener('blur', function() {
            formatCurrencyInput(currencyInput);
        });

        document.querySelector('form').addEventListener('submit', function() {
            currencyInput.value = currencyInput.value.replace(/[^\d]/g, '');  // Solo números antes de enviar el formulario
        });
    } else {
        console.error("El campo con la clase 'currency' no existe en el DOM.");
    }
});


$(document).ready(function() {

    if (operation === 'create') {
        $('#ampliacion').attr('readonly', true);
        $('#id_fecha_amp').attr('readonly', true);
        $('#id_tiae_amp').attr('readonly', true);
    }

    $(function() {
        $('#cod_aso').on('blur', function() {
            var codAsociado = $(this).val();
            $.ajax({
                url: window.location.origin + "/asociados/obtener/" + encodeURIComponent(codAsociado),
                data: { 'cod_asociado': codAsociado },
                success: function(data) {
                    $('#asociado_nombre').val(data.nombre);
                },
                error: function(xhr, status, error) {
                    console.error('Error al obtener el nombre del asociado:', error);
                    $('#asociado_nombre').val('');  
                }
            });
        });

        $('#id_fecha').on('blur', function() {
            if (operation === 'create') {
                var fecha = $(this).val();
                $('#id_fecha_amp').val(fecha);
            }
        });

        $('#id_tiae').on('blur', function() {
            console.log('tiae');
            if (operation === 'create') {
                var tiae = $(this).val();
                $('#id_tiae_amp').val(tiae);
            }
        });
    }); 


    $('#buscarSocioModal').on('show.bs.modal', function () {
        $('#resultadosBusqueda').html(''); 
        $('#inputBuscarSocio').val('');
    });

    $(document).ready(function() {
        $('#inputBuscarSocio').on('input', function() {
            var query = $(this).val();
            console.log('query ', query);
            var url = window.location.origin + "/comprobantes/subcuenta/?cod_con=APOR&filtro=" + encodeURIComponent(query);
            console.log('url ', url);    
            $.ajax({
                url: url,
                success: function(data) {
                    var resultadosHtml = '<table class="table table-striped">';
                    resultadosHtml += '<thead><tr><th>Subcuenta</th><th>Nombre</th><th>Fecha</th><th>Estado</th></tr></thead><tbody>';
                    console.log('item Ok ', data);                
                    data.forEach(function(item) {
                        resultadosHtml += '<tr class="resultado-socio" data-subcuenta="' + item.subcuenta + '" data-nombre="' + item.nombre + '">' +
                            '<td>' + item.subcuenta + '</td>' +
                            '<td>' + item.nombre + '</td>' +
                            '</tr>';
                    });
                    resultadosHtml += '</tbody></table>';
                    $('#resultadosBusqueda').html(resultadosHtml);
                },
                error: function(xhr, status, error) {
                    console.log('Error en la solicitud: ', error);
                }
            });
        });

        $('#resultadosBusqueda').on('click', '.resultado-socio', function() {
            var subcuenta = $(this).data('subcuenta');
            var nombre = $(this).data('nombre');
            $('#cod_aso').val(subcuenta);
            $('#asociado_nombre').val(nombre);
            var myModal = bootstrap.Modal.getInstance(document.getElementById('buscarSocioModal'));
            myModal.hide();
            $('.modal-backdrop').remove();
        });
    });

    function cargarCuentasDeAhorro(codigoSocio) {
        const url = window.location.origin + `/cdats/buscar_cta_aho/${codigoSocio}`; 
        console.log('entra a url --------------->',url);
        $.ajax({
            url: url,
            success: function(data) {
                var resultadosHtml = '<table class="table table-striped">';
                resultadosHtml += '<thead><tr><th>num_cta_aho</th><th>Fecha Apertura</th><th>Estado</th></tr></thead><tbody>';          
                data.forEach(function(item) {
                    resultadosHtml += '<tr class="resultado-socio" data-num_cta="' + item.num_cta + '" data-fecha="' + item.fec_apertura + '">' +
                        '<td>' + item.num_cta + '</td>' +
                        '<td>' + item.fec_apertura + '</td>' +
                        '<td>' + item.estado + '</td>' +
                        '</tr>';
                });
                resultadosHtml += '</tbody></table>';
                $('#listaCuentas').html(resultadosHtml);
            },
            error: function(xhr, status, error) {
                console.log('Error en la solicitud: ', error);
            }
        });
    }
    
    // Ejemplo de cómo abrir la modal y cargar las cuentas al abrirla
    document.getElementById('BuscarCtaAho').addEventListener('click', function() {
        const cod_aso = $('#cod_aso').val();  // Usando el ID
        cargarCuentasDeAhorro(cod_aso);
        $('#seleccionarCuentaModal').modal('show');
    });


    $('#listaCuentas').on('click', '.resultado-socio', function() {
        var numCta = $(this).data('num_cta');
        console.log('Número de Cuenta: ', numCta); // Asegúrate de que esto imprima correctamente
        $('#cta_int_ret').val(numCta); // O cualquier otro campo donde quieras usar este valor
        $('#seleccionarCuentaModal').modal('hide'); // Cierra el moda
        setTimeout(() => { $('.modal-backdrop').remove(); }, 100);
    });
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Compara el nombre de la cookie que queremos (csrftoken)
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;  // Devuelve el valor de la cookie
    }
    
    // Llamada a la función getCookie para obtener el token CSRF
    const csrftoken = getCookie('csrftoken');  // Aquí se llama a la función
    console.log('Token CSRF obtenido:', csrftoken);
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // Asegura que solo se añada el token CSRF en solicitudes locales
            if (!(/^http:.*|^https:.*|^\/.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#form_ctas_cdat').on('submit', function(e) {
        console.log('El documento está listo  para empezar');
        e.preventDefault(); // Evitar el envío del formulario
        let imp_con = $('select[name="imp_con"]').val();
        let num_cta = $('input[name="num_cta"]').val();
        let est_cta = $('input[name="est_cta"]').val();
        let cod_aso = $('#cod_aso').val();  // Usando el ID
        let fecha = $('input[name="fecha"]').val();  // Cambié el nombre correcto
        let valor = $('input[name="valor"]').val();
        let tiae = $('input[name="tiae"]').val();
        let plazo_mes = $('input[name="plazo_mes"]').val();
        let Periodicidad = $('input[name="Periodicidad"]').val();
        let cta_int_ret = $('input[name="cta_int_ret"]').val();
        let ampliacion = $('input[name="ampliacion"]').val();
        let aplicado = $('select[name="aplicado"]').val();
        let fecha_amp = $('input[name="fecha_amp"]').val();
        let tiae_amp = $('input[name="tiae_amp"]').val();

        if (!cod_aso) {
            alert('Por favor,el Cdat debe tener un codigo de asociado');
            $('#cod_aso').focus();
            return;
        }
        if (!valor) {
            alert('Por favor,el Cdat debe tener un valor');
            $('#valor').focus();
            return;
        }
        if (!tiae) {
            alert('Por favor,el Cdat debe tener una tasa de interes anual efectiva');
            $('#tiae').focus();
            return;
        }
        if (!plazo_mes) {
            alert('Por favor,el Cdat debe tener un termino en meses');
            $('#plazo_mes').focus();
            return;
        }
        if (!Periodicidad) {
            alert('Por favor,el Cdat debe establecer el numero de pagos de interes por cada ampliacion');
            $('#peridicidad').focus();
            return;
        }
        if (!Periodicidad) {
            alert('Por favor,el Cdat debe establecer el numero de pagos de interes por cada ampliacion');
            $('#peridicidad').focus();
            return;
        }
        if (!cta_int_ret) {
            alert('Por favor,el Cdat debe tener una cuenta en donde abonar intereses');
            $('#cta_int_ret').focus();
            return;
        }
        if (!aplicado) {
            alert('Por favor, seleccione una opción en el campo Aplicado');
            $('#aplicado').focus();
            return;
        }
        if (!fecha) {
            alert('Por favor,el Cdat debe tener una Fecha de Apertura');
            $('#fecha').focus();
            return;
        }
        if (!imp_con) {
            alert('Por favor, seleccione una opción en el campo Imputacion Contable.');
            $('#imp_con').focus();
            return;
        }
        let tableBody = document.querySelector(".table tbody");
        let filas = tableBody.getElementsByTagName("tr");
        let SinAplicar = 'N';
        for (let fila of filas) {
            let celdaAmpliacion = fila.cells[0]; // Primera celda con el valor de ampliación
            if (celdaAmpliacion.textContent.trim() === ampliacion) {
                SinAplicar = 'S';
                break;
            }
        }
        console.log('Sin Aplicar ',SinAplicar)

        // Crear el objeto formData con los datos
        var formData = {
            imp_con : imp_con,
            num_cta : num_cta,
            cod_aso : cod_aso,
            est_cta : est_cta,
            fecha : fecha,
            valor : valor,
            tiae : tiae,
            plazo_mes : plazo_mes,
            Periodicidad : Periodicidad,
            cta_int_ret : cta_int_ret,
            aplicado : aplicado,
            sinaplicar : SinAplicar,
            ampliacion : ampliacion,
            fecha_amp : fecha_amp,
            tiae_amp : tiae_amp,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        };

        console.log('Enviando datos', formData);
        let url;
        if (operation === 'create') {
            url = urlCrearCuenta; // Reemplaza con tu URL de creación
        } else if (operation === 'update') {
            url = urlModificarCuenta; // Reemplaza con tu URL de actualización
        }
        console.log('Url ----> ',url);
        $.ajax({
            url: url,  // Cambia la URL según corresponda
            type: 'POST',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            data: formData,  // Enviar los datos como formulario
            success: function(response) {
                if (response.success) {
                    var btnGuardar = document.getElementById('btnGuardar');
/*                    var btnImprimir = document.getElementById('btnImprimir');
                    var botonBuscarSocio = document.querySelector('.btn-secondary');
                    if (btnGuardar && btnImprimir) {
                        btnGuardar.style.display = 'none';
                        btnImprimir.style.display = 'block';
                        botonBuscarSocio.style.display = 'none';
                    }*/
                    alert(response.mensaje+' Cuenta Numero -->' + response.num_cta);
                } else {
                    let errores = Array.isArray(response.errors) ? response.errors : [response.errors];
                    alert('Errores:\n' + errores.join('\n'));
                }
            },
            error: function(xhr, status, error) {
                alert('Error en la solicitud: ' + error);
            }
        });
    });
 });

