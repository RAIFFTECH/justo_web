

$(document).ready(function() {
    $('#id_lin_aho').on('select2:select', function(e) {
        let linahoId = e.params.data.id;
        console.log("Cambio detectado en lin_aho (Select2):", linahoId);

        if (!linahoId) {
            console.log("❌ lin_aho_id está vacío, no se hace nada.");
            return;
        }

        const url = `${window.location.origin}/cta_ahorro/max-consecutivo/?lin_aho_id=${linahoId}`;
        console.log("🔗 URL de la petición:", url);

        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log("📩 Respuesta del servidor:", data);
                if (data.max_consecutivo) {
                    document.querySelector("[name='num_cta']").value = data.max_consecutivo;
                    document.querySelector("[name='cod_imp']").value = data.max_consecutivo.substring(0, 2);
                    console.log("✅ num_cta actualizado:", data.max_consecutivo);
                } else {
                    console.error("❌ Error en la respuesta:", data.error);
                }
            })
            .catch(error => console.error("❌ Error fetching data:", error));
    });
});


$(document).ready(function() {
    console.log('El script se ha cargado.');
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
  
    $('#inputBuscarSocio').on('input', function() {
        var query = $(this).val();
        var url = window.location.origin + "/comprobantes/subcuenta/?cod_con=APOR&filtro=" + encodeURIComponent(query);
        console.log('url ', url);    
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

    $('#form_ctas_aho').on('submit', function(e) {
        console.log('El documento está listo');
        e.preventDefault(); // Evitar el envío del formulario
        let lin_aho = $('select[name="lin_aho"]').val();
        let num_cta = $('input[name="num_cta"]').val();
        let cod_aso = $('#cod_aso').val();  // Usando el ID
        let fec_apertura = $('input[name="fec_apertura"]').val();  // Cambié el nombre correcto
        let fec_cancela = $('input[name="fec_cancela"]').val();
        let est_cta = $('select[name="est_cta"]').val();
        let exc_tas_mil = $('select[name="exc_tas_mil"]').val();
        let fec_ini_exc = $('input[name="fec_ini_exc"]').val();
        let cod_imp = $('input[name="cod_imp"]').val();

        // Validaciones
        if (!lin_aho) {
            alert('Por favor, seleccione una opción en el campo de línea de ahorro.');
            $('#lin_aho').focus();
            return;
        }
        if (!est_cta) {
            alert('Por favor, seleccione una opción en el campo Estado de Cuenta');
            $('#est_cta').focus();
            return;
        }
        if (!exc_tas_mil) {
            alert('Por favor, seleccione una opción en el campo Excepcion 4 por mil');
            $('#exc_tas_mil').focus();
            return;
        }

        // Crear el objeto formData con los datos
        var formData = {
            'lin_aho': lin_aho,
            'num_cta': num_cta,
            'cod_aso': cod_aso,
            'fec_apertura': fec_apertura,
            'fec_cancela': fec_cancela,
            'est_cta': est_cta,  // Ajustado
            'exc_tas_mil': exc_tas_mil,
            'fec_ini_exc': fec_ini_exc,
            'cod_imp': cod_imp,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        };

        console.log('Enviando datos', formData);
        let url;
        if (operation === 'create') {
            url = urlCrearCuenta; // Reemplaza con tu URL de creación
        } else if (operation === 'update') {
            url = urlModificarCuenta; // Reemplaza con tu URL de actualización
        }
        
        console.log('Url  --->',url);

        $.ajax({
            url: url,  // Cambia la URL según corresponda
            type: 'POST',
            data: formData,  // Enviar los datos como formulario
            success: function(response) {
                if (response.success) {
                    var btnGuardar = document.getElementById('btnGuardar');
                    var btnImprimir = document.getElementById('btnImprimir');
                    var botonBuscarSocio = document.querySelector('.btn-secondary');
                    if (btnGuardar && btnImprimir) {
                        btnGuardar.style.display = 'none';
                        btnImprimir.style.display = 'block';
                        botonBuscarSocio.style.display = 'none';
                    }
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

