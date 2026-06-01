document

document.addEventListener('DOMContentLoaded', function() {

    var modalCredito = document.getElementById("creditosModal");
    var btnBusCredito = document.getElementById("busCredito");
    var spanCredito = document.getElementById("closeCredito");
    var filterInputCredito = document.getElementById("filterCreditoInput");

    btnBusCredito.onclick = function() {
        modalCredito.style.display = "block";
        filterInputCredito.value = ""; // Clear filter input when opening modal
    };

    spanCredito.onclick = function() {
        modalCredito.style.display = "none";   
    }; 

    window.onclick = function(event) {
        if (event.target == modalCredito) {
            modalCredito.style.display = "none";
        }
    };


    document.getElementById("filterCreditoInput").addEventListener("input", function() {
        var searchTerm = this.value.toLowerCase();
        if (searchTerm.length > 2) {
            var url = window.location.origin + "/comprobantes/subcuenta/?"+"&cod_con=" + "CUOTA" + "&filtro=" + encodeURIComponent(searchTerm);
            console.log("Url -->",url,"Termino --->",searchTerm);
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    var searchResults = document.getElementById("searchResultsCredito");
                    searchResults.innerHTML = ""; 
                    data.forEach(function(item) {
                        var result = document.createElement("div");
                        result.className = "busqueda-result";
                        result.setAttribute("data-subcuenta", item.subcuenta);
                        result.innerText = `${item.subcuenta} - ${item.nombre}`;
                        searchResults.appendChild(result);
                    });
                })
                .catch(error => console.error('Error fetching data:', error));
        } else {
            document.getElementById("searchResultsCredito").innerHTML = ""; // Limpiar resultados si el término de búsqueda está vacío
        }
    });
    

    document.getElementById("searchResultsCredito").addEventListener("click", function(event) {
        if (event.target.classList.contains("busqueda-result")) {
            var subcuenta = event.target.getAttribute("data-subcuenta");
            document.getElementById("codigoCredito").value = subcuenta; // Colocar la cédula en el campo de texto
            modalCredito.style.display = "none"; // Cerrar el modal
        }
    });

});    


