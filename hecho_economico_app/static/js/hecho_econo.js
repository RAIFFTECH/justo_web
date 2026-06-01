// ----------------------- Inicializar Comprobante --------------------------- //
function initializeForm() {
    const operation = "{{ operation }}";
    const crearButton = document.getElementById('guardar');
    const modificarButton = document.getElementById('modificar');
    const imprimirButton = document.getElementById('imprimir');
    const borrarButton = document.getElementById('eliminar');
    if (operation === 'create') {
        crearButton.innerText = 'Crear';
        modificarButton.style.display = 'none';
        imprimirButton.style.display = 'none';
        borrarButton.style.display = 'none';
    } else if (operation === 'update') {
        modificarButton.innerText = 'Actualizar';
        crearButton.style.display = 'inline';
        imprimirButton.style.display = 'inline';
        borrarButton.onclick = () => deleteRecord(recordId);
    } else if (operation === 'delete') {
        crearButton.style.display = 'none';
        borrarButton.style.display = 'inline';
        imprimirButton.style.display = 'inline';
        borrarButton.onclick = () => deleteRecord(recordId);
    }
}

function deleteRecord(recordId) {
    fetch(`/hecho_econo/${recordId}/delete/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
          document.getElementById('error').innerText = data.error;
        } else {
          document.getElementById('message').innerText = 'Registro eliminado correctamente';
          document.getElementById('error').innerText = '';
          setTimeout(() => {
            window.location.href = '/hecho_econo/';
          }, 2000);
        }
    })
    .catch(error => {
        document.getElementById('error').innerText = 'Ocurrió un error';
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
}

window.onload = initializeForm;

function formatCurrency(value) {
    // Convertir el valor a número y asegurar que tenga dos decimales solo si no es cero
    var numericValue = parseFloat(value);
    if (numericValue === 0) {
        return '0';
    } else {
        return '$ ' + numericValue.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }
}


function formatValue(inputId) {
    var input = document.getElementById(inputId);
    input.addEventListener('blur', function() {
        var value = this.value.trim(); // Eliminar espacios en blanco al inicio y al final
        if (value !== '') {
            // Convertir valor a número y formatear como moneda
            var formattedValue = parseFloat(value.replace(/[^\d.]/g, '')).toFixed(2);
            this.value = '$ ' + formattedValue.replace(/\d(?=(\d{3})+\.)/g, '$&,'); // Aplicar formato
        }
    })
};
  

//  
function enviarDatos(event) {
    event.preventDefault(); // Evitar el envío del formulario por defecto
    const relativeUrl = this.getAttribute('data-url');
    const urlHechoEconoCreate = relativeUrl.startsWith('http') ? relativeUrl : `${window.location.origin}${relativeUrl}`;
    // Obtener los datos del formulario maestro
    const hechoEconomico = {
        docto_conta: document.getElementById('id_docto_conta').value,
        numero: document.getElementById('id_numero').value,
        canal: document.getElementById('id_canal').value,
        fecha: document.getElementById('id_fecha').value,
        descripcion: document.getElementById('id_descripcion').value,
        protegido: document.getElementById('id_protegido').checked,
        anulado: document.getElementById('id_anulado').checked,
        beneficiario : document.getElementById('id_beneficiario').value,
        banco : document.getElementById('id_banco').value,
        cheque : document.getElementById('id_cheque').value,
        ciudad : document.getElementById('id_ciudad').value,
        valor : document.getElementById('id_valor').value
    };

    if (!validarCampos(hechoEconomico)) {
        return; // Detener el envío si los campos no son válidos
    }

    function validarCampos(hechoEconomico) {
        if (!hechoEconomico.docto_conta || !hechoEconomico.numero || !hechoEconomico.canal ||
            !hechoEconomico.fecha || !hechoEconomico.descripcion) {
            alert('Todos los campos son obligatorios');
            return false;
        }    
        if (hechoEconomico.descripcion.length < 5) {
            alert('La descripción debe tener al menos 5 caracteres');
            return false;
        }
        const fechaRegex = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;
        console.log('fecha ----', hechoEconomico.fecha);
        if (!fechaRegex.test(hechoEconomico.fecha)) {
            console.log('esta mal la fecha ')
            alert('La fecha debe estar en formato dd mm aaaa');
            return false;
        }
        return true; // Todos los campos son válidos
    }
    
    // Construir la lista de detalles
    const detalles = [];
    $('#detalle_prod_table tr').each(function() {
        const detalle = {
            id: $(this).find('td:eq(0)').text().trim() || null,
            concepto: $(this).find('td:eq(1)').text().trim() || null,
            subcuenta: $(this).find('td:eq(2)').text().trim() || null,
            valor: obtenerValorNumerico($(this).find('td:eq(3)').text().trim()) || null,
            det_pro: $(this).find('td:eq(4)').text().trim() || null,
        };
        detalles.push(detalle);
    });
    const data = {
        ...hechoEconomico,
        detalles: detalles
    };

    $.ajax({
        url: urlHechoEconoCreate,
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: JSON.stringify(data),
        success: function(response) {
            if (response.success) {
                alert(response.message +' '+ response.Numero+'  Pk '+response.pk);
                $('#documentPk').val(response.pk);
                $('#btnImprimir').prop('disabled', false);
                var imprimirUrl = '../imprime/' + response.pk;
                $('#btnImprimir').off('click').on('click', function() {
                    window.location.href = imprimirUrl;  // Redirigir a la URL de impresión
                });
            } else {
                if (response.error) {
                    // Mostrar mensaje específico del error de lógica
                    alert(response.error);
                }
                if (response.errors) {
                    // Concatenar los errores en un mensaje
                    let errorMessage = "Errores en el formulario:\n";
                    for (let key in response.errors) {
                        errorMessage += `${key}: ${response.errors[key].join(', ')}\n`;
                    }
                    // Mostrar errores en un alert
                    alert(errorMessage);
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error en la solicitud AJAX:', error);
            alert('Se produjo un error al enviar los datos. Por favor, revisa la consola para más detalles.');
        }
    });
}


function inicializarDocumento() {
    var valorInicial = 0;
    document.getElementById('txtConcepto').value = '';
    document.getElementById('txtSubCuenta').value = '';
    document.getElementById('txtDebito').value = formatCurrency(valorInicial.toString());
    formatValue('txtDebito');
    document.getElementById('txtCredito').value = formatCurrency(valorInicial.toString());
    formatValue('txtCredito');
    document.getElementById('txtValor1').value = formatCurrency(valorInicial.toString());
    formatValue('txtValor1');
    document.getElementById('txtValor2').value = formatCurrency(valorInicial.toString());
    formatValue('txtValor2');
    document.getElementById('txtSaldo').value = formatCurrency(valorInicial.toString());
    formatValue('txtSaldo');

    var inputs = document.querySelectorAll('.navigate');
    inputs.forEach(function(input) {
        addNavigation(input);
    });
}

function addNavigation() {
    var inputs = document.querySelectorAll('.navigate');
    inputs.forEach((input, index) => {
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                var nextInput = inputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                }
            }
        });
    });
}


document.addEventListener('DOMContentLoaded', function() {
    console.log('Entra a guarar ');

    const guardarButton = document.getElementById('guardar');
    const modificarButton = document.getElementById('modificar');
    if (guardarButton) {
        guardarButton.addEventListener('click', enviarDatos);
    }
    else if (modificarButton) {
        modificarButton.addEventListener('click', enviarDatos);
    }
    else {
        console.error("Ni el botón guardar ni el botón modificar se encontraron en el DOM");
    }
    const btnBusConcepto = document.getElementById('busConcepto');
    const modalConcepto = document.getElementById('conceptoModal');
    var spanConcepto = document.getElementById("closeConcepto");
    var filterInputConcepto = document.getElementById("filterConceptoInput");

    $('#id_docto_conta').change(function() { 
        console.log('id_docto_conta');
        const doctoContaSelect = document.getElementById('id_docto_conta');
        if (doctoContaSelect) { 
            const doctoContaId = doctoContaSelect.value;
            const url = `${window.location.origin}/comprobantes/get_consecutivo_plus_one/?docto_conta_id=${doctoContaId}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log('esto es lo que devuelve el Back End---> ',data)
                    if (data.consecutivo_plus_one !== undefined && data.consecutivo_plus_one !== null) {
                        $('#id_numero').val(data.consecutivo_plus_one); 
                    } else {
                        console.error('Error:', data.error);
                    }
                })
                .catch(error => console.error('Error fetching data:', error));
        } else {
            $('#id_numero').val(''); // Si no hay un valor seleccionado, limpia el campo numero
        }
    });

    // propiedadas de btnBusConcepto
    btnBusConcepto.onclick = function() {
        modalConcepto.style.display = "block";
        filterInputConcepto.value = ""; // Clear filter input when opening modal
    };

    // cuando no retorna nada
    spanConcepto.addEventListener('click', function() {
        modalConcepto.style.display = 'none';
    });    

    spanConcepto.onclick = function() {
        modalConcepto.style.display = "none";   
    }; 

    window.onclick = function(event) {
        if (event.target == modalConcepto) {
            modalConcepto.style.display = "none";
        }
    };

    document.getElementById("filterConceptoInput").addEventListener("input", function() {
        var searchTerm = this.value.toLowerCase();
        if (searchTerm.length > 1) {
            var url = window.location.origin + "/comprobantes/conceptos/?query=" + encodeURIComponent(searchTerm);
            console.log("Url -->",url,"Termino --->",searchTerm);
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    var searchResults = document.getElementById("searchResultsConcepto");
                    searchResults.innerHTML = ""; 
                    data.forEach(function(item) {
                        var result = document.createElement("div");
                        result.className = "busqueda-result";
                        result.setAttribute("data-cod_con", item.cod_con);
                        let spaces = " ".repeat(8-item.cod_con.length)+'-'+" ".repeat(2); 
                        result.innerText = `${item.cod_con}${spaces}${item.descripcion}`;
                        searchResults.appendChild(result);
                    });
                })
                .catch(error => console.error('Error fetching data:', error));
        } else {
            document.getElementById("searchResultsConcepto").innerHTML = ""; // Limpiar resultados si el término de búsqueda está vacío
        }
    });

    document.getElementById("searchResultsConcepto").addEventListener("click", function(event) {
        if (event.target.classList.contains("busqueda-result")) {
            var cod_con = event.target.getAttribute("data-cod_con");
            document.getElementById("txtConcepto").value = cod_con; // Colocar la cédula en el campo de texto
            modalConcepto.style.display = "none"; // Cerrar el modal
        }
    });  

    var modalSubcuenta = document.getElementById("subcuentaModal");
    var btnBusSubcuenta = document.getElementById("busSubcuenta");
    var spanSubcuenta = document.getElementById("closeSubcuenta");
    var filterInputSubcuenta = document.getElementById("filterSubcuentaInput");

    btnBusSubcuenta.onclick = function() {
        modalSubcuenta.style.display = "block";
        filterInputSubcuenta.value = ""; // Clear filter input when opening modal
    };

    spanSubcuenta.onclick = function() {
        modalSubcuenta.style.display = "none";   
    }; 

    window.onclick = function(event) {
        if (event.target == modalSubcuenta) {
            modalSubcuenta.style.display = "none";
        }
    };

    document.getElementById("filterSubcuentaInput").addEventListener("input", function() {
        var searchTerm = this.value.toLowerCase();
        if (searchTerm.length > 4) {
            var url = window.location.origin + "/comprobantes/subcuenta/?"+"&cod_con=" + encodeURIComponent(document.getElementById("txtConcepto").value) + "&filtro=" + encodeURIComponent(searchTerm);
            fetch(url)
                .then(response => response.json())
                .then(data => { 
                var searchResults = document.getElementById("searchResultsSubcuenta");
                    searchResults.innerHTML = "";
                    data.forEach(function(item) {
                        var result = document.createElement("div");
                        result.className = "busqueda-result";
                        result.setAttribute("data-subcuenta", item.subcuenta);
                        result.setAttribute("data-tip_con",item.tip_con);
                        result.setAttribute("data-valor",item.valor);                       
                        if (item.tip_con == '3') {
                            result.innerText = `${item.subcuenta} - ${item.nombre} - ${item.fec_des} - ${item.cap_ini}`;
                            if (document.getElementById("txtConcepto").value == 'DESEM') {
                                result.setAttribute("data-valor",item.cap_ini);
                            }
                            else{
                                result.setAttribute("data-valor",-item.val_cuo);
                            }
                        }
                        else {
                            result.innerText = `${item.subcuenta} - ${item.nombre} - ${item.valor} `;
                        }
                        searchResults.appendChild(result);   
                    }); 
                })
                .catch(error => console.error('Error fetching data:', error));
        } else {
            document.getElementById("searchResultsSubcuenta").innerHTML = ""; // Limpiar resultados si el término de búsqueda está vacío
        }
    });
    
    document.getElementById("searchResultsSubcuenta").addEventListener("click", function(event) {
        if (event.target.classList.contains("busqueda-result")) {
            var subcuenta = event.target.getAttribute("data-subcuenta");
            var tipcon = event.target.getAttribute("data-tip_con");
            var valor = event.target.getAttribute("data-valor");
            document.getElementById("txtSubCuenta").value = subcuenta;
            console.log('tipo ----> ',tipcon);
            console.log('Valor  ',valor);
            if (tipcon == '3') {
                if (valor >= 0){
                    document.getElementById("txtDebito").value = valor;
                    document.getElementById("txtCredito").value = 0;
                }
                else{
                    document.getElementById("txtDebito").value = 0;
                    document.getElementById("txtCredito").value = -valor;
                }
            }
            if (tipcon == '6') {
                document.getElementById("txtDebito").value = 0;
                document.getElementById("txtCredito").value = valor;
            }
            // Colocar la cédula en el campo de texto
            modalSubcuenta.style.display = "none"; // Cerrar el modal
        }
    });
    
    
    // Selecciona todos los campos con la clase específica
    document.querySelectorAll('.form-control.d-inline-block.navigate').forEach(function(input) {
        // Restricción para aceptar solo números y decimales

        input.addEventListener("input", function() {
            this.value = this.value.replace(/[^0-9]/g, '');  // Solo números
        });
    
        input.addEventListener("blur", function() {
            let value = parseInt(this.value.replace(/,/g, ''));  // Elimina los separadores de miles
            if (!isNaN(value)) {
                this.value = `$ ${value.toLocaleString('en-US')}`;  // Aplica separadores de miles
            }
        });
    });

});


document.getElementById('id_cheque').addEventListener('input', function (e) {
    // Solo permitir valores numéricos
    this.value = this.value.replace(/[^0-9]/g, '');
});


var detalleProdIdCounter = -1;

function obtenerValorNumerico(valorFormateado) {
  var valorNumerico = parseFloat(valorFormateado.replace(/[^0-9.-]+/g, ''));
  return isNaN(valorNumerico) ? 0 : valorNumerico;
}

function MensajeRapido(mensaje, duracion) {
    let alerta = window.open("", "", "width=200,height=100");
    alerta.document.write(`<p style="font-size:18px;">${mensaje}</p>`);
    setTimeout(() => {
        alerta.close();
    }, duracion);
}


function ValidarExiste(iconcepto, isubCuenta,ivalor) {
    var YaExiste = 0;
    var filas = $('#detalle_prod_table tr'); // Selecciona todas las filas de la tabla
    for (var i = 0; i < filas.length; i++) {
        var concepto = $(filas[i]).find('td:eq(1)').text().trim(); // Obtener el texto del segundo td (concepto)
        var subCuenta = $(filas[i]).find('td:eq(2)').text().trim(); // Obtener el texto del tercer td (subCuenta)
        if (subCuenta === isubCuenta) {
            if (concepto === iconcepto) {
                YaExiste = parseInt($(filas[i]).find('td:eq(0)').text().trim(), 10);
                if (YaExiste < 0) {  //  Se puede modificar el valor sin problema por que aun no ha sido grabado
                    $(filas[i]).find('td:eq(3)').text(ivalor);
                    return YaExiste;
                }
                else {
                    return YaExiste;
                }
            }
            if ((iconcepto == 'ABOCA' || iconcepto == 'CUOTA' || iconcepto == 'ABOCU') && (concepto == 'ABOCA' || concepto == 'CUOTA' || concepto == 'ABOCU')) {
                YaExiste = parseInt($(filas[i]).find('td:eq(0)').text().trim(), 10);
                return YaExiste;
            }
        }
    }
    return YaExiste;
}

$(document).ready(function() {
    // Delegación de eventos para  gestionar detalles
    //  Editar
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    $('#txtSubCuenta').on('blur', function() {
        console.log('Ejecutando asociacion concepto subcuenta');
        var concepto = $('#txtConcepto').val().trim();;
        var subCuenta = $('#txtSubCuenta').val().trim();;
        if (concepto && subCuenta) {
            let url = `${window.location.origin}/comprobantes/concepto_subcuenta/?cod_con=${concepto}&sub_cuenta=${subCuenta}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    let detalle = ''; 
                    let saldo = 0;
                    for (let item of data) {
                        if (item.subcuenta.trim() === subCuenta.trim()) {
                            detalle = item.nombre;
                            saldo = item.saldo;
                            break; // Sale del ciclo for cuando se encuentra el item buscado
                        }
                    }
                    if (detalle === '') {
                        MensajeRapido('Falta asociacion entre el Concepto y la Subcuenta.',2000);
                        return false; // Detener la acción de agregar
                    } 
                    else 
                    {
                        $('#txtSaldo').val(formatCurrency(saldo))
                    }
            })
            .catch(error => console.error('Error fetching data:', error));    
        } else {
            MensajeRapido('Se deben completar los datos ',2000);
        }

    });


    $('#detalle_prod_table').on('click', '.edit-btn', function() {
        var id = this.id;  // Obtener el ID del botón de editar
        var row = $(this).closest('tr');
        if (row.length) {
            var cells = row.find('td');
            $('#txtConcepto').val(cells.eq(1).text());
            $('#txtSubCuenta').val(cells.eq(2).text());
            var valorCelda = parseFloat(cells.eq(3).text().replace(/[^\d.-]/g, ''));
            $('#txtDetalle').val(cells.eq(4).text());
            console.log('Entra a Edit ',cells.eq(2).text(),'     ',cells.eq(4).text());
            if (!isNaN(valorCelda) && valorCelda > 0) {
                $('#txtDebito').val(valorCelda);
                $('#txtCredito').val('');
            } else {
                $('#txtDebito').val('');
                $('#txtCredito').val(-valorCelda);
            }
        } else {
            console.error('Row containing edit button with ID ' + id + ' not found.');
        }
    });
    
    //  Eliminar
    $('#detalle_prod_table').on('click', '.eliminar-btn', function() {
        var id = this.id;  // Obtener el ID del botón de eliminar
        var confirmar = confirm('¿Estás seguro de que quieres eliminar esta fila?');
        if (confirmar) {
            $(this).closest('tr').remove();
        } 
    });

    //  Agregar 
    $('#Agregar').on('click', function(event) {
        event.preventDefault();
        var concepto = $('#txtConcepto').val().trim();;
        var subCuenta = $('#txtSubCuenta').val().trim();;
        var debito = obtenerValorNumerico($('#txtDebito').val());
        var credito = obtenerValorNumerico($('#txtCredito').val());
        var saldo = obtenerValorNumerico($('#txtSaldo').val());
        var detallei = $('#txtDetalle').val().trim();;
        var valor = debito - credito; // Asumimos que solo uno de ellos tiene valor
        if ((concepto == 'AHO' || concepto == 'APOR')  && saldo < valor) {
            MensajeRapido('El saldo de la Cuenta es Inferior al valor de Retiro',2000);
            return false; // Detener la acción de agregar
        }
        if (concepto && subCuenta && valor) {
            var Existe = ValidarExiste(concepto, subCuenta,valor);
            if (Existe !== 0) {
                MensajeRapido('Ya existe una Subcuenta con el Id '+Existe.toString(),2000);
                return false; // Detener la acción de agregar
            }
            let url = `${window.location.origin}/comprobantes/concepto_subcuenta/?cod_con=${concepto}&sub_cuenta=${subCuenta}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    let detalle = ''; 
                    for (let item of data) {
                        console.log('------> ',item.subcuenta.trim());
                        if (item.subcuenta.trim() === subCuenta.trim()) {
                            detalle = detallei;
                            console.log('Detalle',detalle);
                            break; // Sale del ciclo for cuando se encuentra el item buscado
                        }
                        console.log('item.SUBCUENTA ---> ',item.subcuenta,'item.nombre ---> ',item.nombre)
                    }
                    if (detalle === '') {
                        MensajeRapido('No Hay Asociacion entre el Concepto y la Subcuenta.',2000);
                        return false; // Detener la acción de agregar
                    } 
                    else 
                    {
                        valorFor = formatCurrency(valor.toString());
                        var newRowId = detalleProdIdCounter--;
                        var newRow = `<tr id="detalle_prod_${newRowId}">
                            <td>${newRowId}</td>
                            <td>${concepto}</td>
                            <td>${subCuenta}</td>
                            <td>${valorFor}</td>
                            <td>${detalle}</td>
                            <td>
                                <a href="#" class="btn btn-info btn-sm detalles-btn" title="Detalles">
                                    <i class="fas fa-print"></i> Detalles
                                </a>
                                <a href="#" class="btn btn-warning btn-sm edit-btn" title="Editar">
                                    <i class="fas fa-edit"></i> Editar
                                </a>
                                <a href="#" class="btn btn-danger btn-sm eliminar-btn" id="eliminar-btn-${newRowId}" title="Eliminar">
                                    <i class="fas fa-trash-alt"></i> Eliminar
                                </a>
                            </td>
                        </tr>`;
                        $('#detalle_prod_table').append(newRow);
                        $('#mensaje').show().delay(2000).fadeOut();
                        $('#txtConcepto').val('');
                        $('#txtSubCuenta').val('');
                        $('#txtDetalle').val('');
                        inicializarDocumento();
                    }
            })
            .catch(error => console.error('Error fetching data:', error));    
        } else {
            MensajeRapido('Se deben completar los datos ',2000);
        }
    });

    //  Limpiar
    $('#Limpiar').on('click', function(event) {
        $('#txtConcepto').val('');
        $('#txtSubCuenta').val('');
        $('#txtDetalle').val('');
        $('#txtDebito').val(0);
        $('#txtCredito').val(0);
        $('#txtValor1').val(0);
        $('#txtValor2').val(0);
        inicializarDocumento();
    });

    //  Cuadrar contra caja
    $('#Cuadrar').on('click', function(event) {
        console.log('Entra a Cuadrar');
        event.preventDefault();
        var concepto = $('#txtConcepto').val().trim();
        var subCuenta = $('#txtSubCuenta').val().trim();
        var bancoSelect = document.getElementById('id_banco'); 
        var xconcepto = '',xsubcuenta;
        if (!bancoSelect.value){ 
            xconcepto = 'CAJA';
            xsubcuenta = '11050501'
        }
        else{ 
            var banco = bancoSelect.value;
            var bancoText = bancoSelect.options[bancoSelect.selectedIndex].text; 
            var firstSpaceIndex = bancoText.indexOf(" ");
            var bancoCtaCon;
            if (firstSpaceIndex !== -1) {  // Si hay un espacio en blanco
                bancoCtaCon = bancoText.substring(0, firstSpaceIndex);
            } else {
                bancoCtaCon = bancoText;  // Si no hay espacio en blanco, toma todo el texto
            }
            xconcepto = 'BANCO';
            xsubcuenta = bancoCtaCon;
        }
        var totalValor = 0;
        /*var tabla = document.getElementById('TablaDetalle');*/
        var tabla = document.querySelector('#detalle_prod_table')  
        var filas = tabla.getElementsByTagName('tr'); 
        yaCaja = false;
        filaCaja = 0;
        for (var fil = 0; fil < filas.length; fil++) { 
            var celdas = filas[fil].getElementsByTagName('td'); 
            var cuenta = celdas[1].textContent.trim(); 
            if (cuenta !== 'CAJA' && cuenta !== 'BANCO') {
                var valorStr = celdas[3].textContent.trim(); 
                var valor = parseFloat(valorStr.replace(/[$,]/g, '')) || 0;
            }
            else{
                yaCaja = true;
                filaCaja = fil;
            }   
            totalValor += valor; 
        }
        if (yaCaja === true){
            var celdaValor = fila.getElementsByTagName('td')[filaCaja];
            celdaValor.textContent = totalValor;
        }
        else{
            valorFor = formatCurrency(-totalValor.toString());
            detalle = 'Entidad Solidaria';
            var newRow = `<tr id="detalle_prod_${0}">
                <td>${0}</td>
                <td>${xconcepto}</td>
                <td>${xsubcuenta}</td>
                <td>${valorFor}</td>
                <td>${detalle}</td>
                <td>
                    <a href="#" class="btn btn-info btn-sm detalles-btn" title="Detalles">
                        <i class="fas fa-print"></i> Detalles
                    </a>
                    <a href="#" class="btn btn-warning btn-sm edit-btn" title="Editar">
                        <i class="fas fa-edit"></i> Editar
                    </a>
                    <a href="#" class="btn btn-danger btn-sm eliminar-btn" id="eliminar-btn-${0}" title="Eliminar">
                        <i class="fas fa-trash-alt"></i> Eliminar
                    </a>
                </td>
            </tr>`;
            $('#detalle_prod_table').append(newRow);
            $('#mensaje').show().delay(2000).fadeOut();
            $('#txtConcepto').val('');
            $('#txtSubCuenta').val('');
            var campoValor = document.getElementById('id_valor')
            campoValor.value = -totalValor ; // Asigna el nuevo valor
            inicializarDocumento();
        }
    });

});


// Abrir el modal al hacer clic en el botón de importación
document.getElementById('importButton').addEventListener('click', function() {
    var myModal = new bootstrap.Modal(document.getElementById('importModal'));
    z
    myModal.show();
});

// Cargar y procesar el archivo Excel o CSV
document.getElementById('loadFileButton').addEventListener('click', function() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (file) {
        var reader = new FileReader();

        reader.onload = function(event) {
            var data = event.target.result;
            var workbook = XLSX.read(data, { type: 'binary' });

            // Obtener la primera hoja del archivo Excel
            var sheetName = workbook.SheetNames[0];
            var worksheet = workbook.Sheets[sheetName];

            // Convertir la hoja a un formato JSON
            var jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

            // Limpiar la vista previa
            var tbody = document.getElementById('dataPreview').getElementsByTagName('tbody')[0];
            tbody.innerHTML = '';

            // Recorrer los datos y agregarlos a la tabla de vista previa
            jsonData.forEach(function(row, index) {
                if (index > 0) { // Salta la primera fila (que podría ser el encabezado)
                    var tr = document.createElement('tr');
                    row.forEach(function(cell) {
                        var td = document.createElement('td');
                        td.textContent = cell;
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                }
            });
        };

        reader.readAsBinaryString(file);
    } else {
        alert('Por favor, selecciona un archivo');
    }
});

// Guardar los datos en la tabla principal al hacer clic en "Grabar Movimientos"
document.getElementById('saveButton').addEventListener('click', function() {
    var tbodyPreview = document.getElementById('dataPreview').getElementsByTagName('tbody')[0];
    var rows = tbodyPreview.getElementsByTagName('tr');
    var tbody = document.getElementById('detalleProdTable').getElementsByTagName('tbody')[0];

    // Recorrer los datos de la vista previa y agregarlos a la tabla principal
    Array.from(rows).forEach(function(row) {
        var newRow = document.createElement('tr');
        Array.from(row.getElementsByTagName('td')).forEach(function(cell) {
            var newCell = document.createElement('td');
            newCell.textContent = cell.textContent;
            newRow.appendChild(newCell);
        });

        // Agregar las acciones (botones)
        var actionsCell = document.createElement('td');
        actionsCell.innerHTML = `
            <a href="#" class="btn btn-info btn-sm detalles-btn" title="Detalles">
                <i class="fas fa-print"></i> Detalles
            </a>
            <a href="#" class="btn btn-warning btn-sm edit-btn" title="Editar">
                <i class="fas fa-edit"></i> Editar
            </a>
            <a href="#" class="btn btn-danger btn-sm eliminar-btn" title="Eliminar">
                <i class="fas fa-trash-alt"></i> Eliminar
            </a>
        `;
        newRow.appendChild(actionsCell);

        tbody.appendChild(newRow);
    });

    // Cerrar el modal
    var myModal = bootstrap.Modal.getInstance(document.getElementById('importModal'));
    myModal.hide();
});