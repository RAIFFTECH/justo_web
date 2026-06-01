
$(document).ready(function () {
    // Manejar el evento blur para obtener el nombre del asociado
    $('#doc_ide').on('blur', function () {
        var codAsociado = $(this).val();
        $.ajax({
            url: window.location.origin + "/terceros/obtener/" + encodeURIComponent(codAsociado),
            data: { 'cod_asociado': codAsociado },
            success: function (data) {
                $('#tercero_nombre').val(data.nombre);
            },
            error: function (xhr, status, error) {
                console.error('Error al obtener el nombre del asociado:', error);
                $('#tercero_nombre').val('');
            }
        });
    });

    $('#id_user').on('change', function() {
        var userId = $(this).val(); // Obtener el ID del usuario seleccionado
        console.log('url-----> ',window.location.origin + '/usuarios/profiles/user-photo/' + userId)
        if (userId) {
            $.ajax({
                url: window.location.origin + '/usuarios/profiles/user-photo/' + userId, // Cambia esta URL al endpoint que vas a crear
                method: 'GET',
                success: function(data) {
                    if (data.photo_url) {
                        $('#user-photo').attr('src', data.photo_url).show(); // Mostrar la imagen
                    } else {
                        $('#user-photo').hide(); // Ocultar si no hay foto
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error al obtener la foto:', error);
                }
            });
        } else {
            $('#user-photo').hide(); // Ocultar si no hay usuario seleccionado
        }
    });

});


// Cajeros.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        const redirectUrl = document.querySelector('form').dataset.redirectUrl;
        event.preventDefault();
        const formData = new FormData(form);
        fetch("/cajeros/cajeros/nuevo/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
        })
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Error al guardar el cajero");
            }
        })
        .then((data) => {
            alert("Cajero guardado con éxito");
            window.location.href = redirectUrl;
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Hubo un problema al guardar el cajero");
        });
    });
});
