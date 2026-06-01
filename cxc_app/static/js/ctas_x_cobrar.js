
document.addEventListener('DOMContentLoaded', function() {
    const conceptoSelect = document.querySelector("[name='concepto']");
    const cod_cxc = document.querySelector("[name='cod_cxc']");
    const cod_imp = document.querySelector("[name='cod_imp']");
    const currencyInput = document.querySelector('.currency');  // Mover aquí para asegurar que se declare en un solo lugar

    // Manejo del evento 'change' en linAhoSelect
    if (conceptoSelect) {
        conceptoSelect.addEventListener('change', function() {
            const conceptoId = conceptoSelect.value; // Asegúrate de obtener el valor correcto
            if (!conceptoId) {
                return;
            }
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
    }); 


    $('#buscarSocioModal').on('show.bs.modal', function () {
        $('#resultadosBusqueda').html(''); 
        $('#inputBuscarSocio').val('');
    });

    $(document).ready(function() {
        $('#inputBuscarSocio').on('input', function() {
            var query = $(this).val();
            var url = window.location.origin + "/comprobantes/subcuenta/?cod_con=APOR&filtro=" + encodeURIComponent(query);   
            $.ajax({
                url: url,
                success: function(data) {
                    var resultadosHtml = '<table class="table table-striped">';
                    resultadosHtml += '<thead><tr><th>Subcuenta</th><th>Nombre</th><th>Fecha</th><th>Estado</th></tr></thead><tbody>';          
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
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // Asegura que solo se añada el token CSRF en solicitudes locales
            if (!(/^http:.*|^https:.*|^\/.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#form_ctas_x_cobrar').on('submit', function(e) {
        e.preventDefault(); // Evitar el envío del formulario
        let cod_cxc = $('input[name="cod_cxc"]').val();
        let concepto = $('select[name="concepto"]').val();
        let cod_aso = $('#cod_aso').val();  // Usando el ID
        let fecha_des = $('input[name="fecha_des"]').val();  
        let fecha_exi = $('input[name="fecha_exi"]').val();  
        let valor = $('input[name="valor"]').val();
        let aplicado = $('select[name="aplicado"]').val();

        if (!concepto) {
            alert('Por favor, debe haber un concepto');
            $('#concepto').focus();
            return;
        }
        if (!cod_aso) {
            alert('Por favor, debe haber un tercero');
            $('#cod_aso').focus();
            return;
        }
        if (!valor) {
            alert('Por favor, debe haber un valor');
            $('#valor').focus();
            return;
        }
        if (!fecha_des) {
            alert('Por favor,debe hber una fecha de desembolso');
            $('#fecha_des').focus();
            return;
        }
        if (!fecha_exi) {
            alert('Por favor,debehaber una fecha exigible');
            $('#fecha_exi').focus();
            return;
        }
        if (!aplicado) {
            alert('Por favor, seleccione una opción en el campo Aplicado');
            $('#aplicado').focus();
            return;
        }

        // Crear el objeto formData con los datos
        var formData = {
            cod_cxc : cod_cxc,
            cod_aso : cod_aso,
            fecha_des : fecha_des,
            fecha_exi : fecha_exi,
            valor : valor,
            concepto : concepto,
            aplicado : aplicado,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        };

        let url;
        if (operation === 'create') {
            url = urlCrearCxc; // Reemplaza con tu URL de creación
        } else if (operation === 'update') {
            url = urlModificarCxc // Reemplaza con tu URL de actualización
        }
        $.ajax({
            url: url,  // Cambia la URL según corresponda
            type: 'POST',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            data: formData,  // Enviar los datos como formulario
            success: function(response) {
                if (response.success) {
                    var btnGuardar = document.getElementById('btnGuardar');
                    alert(response.mensaje+' Cuenta Numero -->' + response.cod_cxc);
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

