
document.addEventListener('DOMContentLoaded', function() {
    const conceptoSelect = document.querySelector("[name='concepto']");
    if (conceptoSelect) {
        conceptoSelect.addEventListener('change', function() {
            const conceptoId = conceptoSelect.value; // Asegúrate de obtener el valor correcto
            if (!conceptoId) {
                return;
            }
        });
    }
});


$(document).ready(function() {    
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

    $('#form_exportar').on('submit', function(e) {
        console.log('El documento está listo  para empezar');
        e.preventDefault(); // Evitar el envío del formulario
        let concepto = $('select[name="concepto"]').val();
        let fecha_des = $('input[name="fecha_des"]').val();  
        let fecha_exi = $('input[name="fecha_exi"]').val();  
        var fileInput = document.getElementById('fileInput');
        var file = fileInput.files[0];
        if (!file) {
            alert('Por favor, seleccione un archivo.');
            return;
        }
        // Verificar que el archivo sea de tipo Excel
        var validExtensions = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!validExtensions.includes(file.type)) {
            alert('Por favor, seleccione un archivo Excel válido (.xls o .xlsx).');
        }
        if (!concepto) {
            alert('Por favor, debe haber un concepto');
            $('#concepto').focus();
            return;
        }
        if (!fecha_des) {
            alert('Por favor,debe haber una fecha de desembolso');
            $('#fecha_des').focus();
            return;
        }
        if (!fecha_exi) {
            alert('Por favor,debehaber una fecha exigible');
            $('#fecha_exi').focus();
            return;
        }
        var formData = new FormData();  // Crear un objeto FormData
        formData.append('concepto', concepto);
        formData.append('fecha_des', fecha_des);
        formData.append('fecha_exi', fecha_exi);
        formData.append('excelFile', file);  // 'file' debería ser el archivo seleccionado
        formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
        let url;
        console.log('url importar ',importarUrl);
        $.ajax({
            url: importarUrl, 
            type: 'POST',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            data: formData,
            processData: false,  // No procesar los datos
            contentType: false,  // No establecer el tipo de contenido
            success: function(response) {
                console.log(response);  // Verificar la respuesta
                if (response.success) {
                    alert(response.mensaje + ' Archivo Procesado Correctamente. resultados retornados en el archivo descargado');
                    window.location.href = response.download_url;
                } else {
                    var errores = response.errors;
                    var mensajeError = 'Errores No se graba ningun Registro\n';
                    for (var campo in errores) {
                        if (errores.hasOwnProperty(campo)) {
                            mensajeError += campo + ': ' + errores[campo] + '\n';
                        }
                    }
                    alert(mensajeError);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error en la solicitud:', error);  // Mostrar el error en la consola
            }
        });
    });

    $('#form_elimina_exp').on('submit', function(e) {
        console.log('El documento está listo  para empezar');
        e.preventDefault(); // Evitar el envío del formulario
        var fileInput = document.getElementById('fileInput');
        var file = fileInput.files[0];
        if (!file) {
            alert('Por favor, seleccione un archivo.');
            return;
        }
        // Verificar que el archivo sea de tipo Excel
        var validExtensions = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!validExtensions.includes(file.type)) {
            alert('Por favor, seleccione un archivo Excel válido (.xls o .xlsx).');
        }
        
        var formData = new FormData();  // Crear un objeto FormData
        formData.append('excelFile', file);  // 'file' debería ser el archivo seleccionado
        formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
        let url;
        console.log('url importar ',eliminarUrl);
        $.ajax({
            url: eliminarUrl, 
            type: 'POST',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            data: formData,
            processData: false,  // No procesar los datos
            contentType: false,  // No establecer el tipo de contenido
            success: function(response) {
                console.log(response);  // Verificar la respuesta
                if (response.success) {
                    alert(response.mensaje + ' Archivo Procesado Correctamente. resultados retornados en el archivo descargado');
                    window.location.href = response.download_url;
                } else {
                    var errores = response.errors;
                    var mensajeError = 'Errores No se Elimina ningun Registro\n';
                    for (var campo in errores) {
                        if (errores.hasOwnProperty(campo)) {
                            mensajeError += campo + ': ' + errores[campo] + '\n';
                        }
                    }
                    alert(mensajeError);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error en la solicitud:', error);  // Mostrar el error en la consola
            }
        });
    });
 });

