document.addEventListener('DOMContentLoaded', function() {
    // Encuentra el campo 'doc_ide' y 'nom_soc' en el DOM
    var docIdeField = document.querySelector('input[name="doc_ide"]');
    var nomSocField = document.querySelector('input[name="nom_soc"]');
    console.log('Entra  a poner socio')
    if (docIdeField && nomSocField) {
        // Escucha el evento 'blur' para el campo 'doc_ide'
        docIdeField.addEventListener('blur', function() {
            var docIde = this.value.trim();  // Obtén el valor del campo doc_ide y elimina espacios en blanco
            if (docIde) {
                fetch(window.location.origin + "/asociados/obtener/?doc_ide="+encodeURIComponent(searchTerm))
                    .then(response => response.json())
                    .then(data => {
                        if (data.nombre) {
                            // Actualiza el campo nom_soc con el nombre recibido
                            nomSocField.value = data.nombre;
                        } else if (data.error) {
                            // Maneja el error (opcional)
                            console.error('Error:', data.error);
                            nomSocField.value = '';  // Borra el campo si hay error
                        }
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                // Si doc_ide está vacío, limpia el campo nom_soc
                nomSocField.value = '';
            }
        });
    }
});

