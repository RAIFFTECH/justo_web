
function formatCurrency(value) {
  // Primero, asegurémonos de tener un número limpio para trabajar
  value = parseFloat(value.replace(/[^\d.-]/g, ''));

  if (isNaN(value)  ) {
      return '0'; // Devolver cadena vacía si el valor no es válido
  };
  if (value === 0) {
    return '0';
  } else {
            var sign = (value < 0) ? '-' : ''; // Mantener el signo si es negativo
            value = Math.abs(value); // Convertir a valor absoluto para el formateo
            var parts = value.toFixed(2).split('.');
            var integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            var decimalPart = parts[1] || '00'; // Asegurar que siempre hay dos decimales
            return sign + '$ ' + integerPart + '.' + decimalPart;
          };            
}


function formatCurrency(value) {
  // Convertir el valor a número y asegurar que tenga dos decimales solo si no es cero
  var numericValue = parseFloat(value);
  if (numericValue === 0) {
      return '0';
  } else {
      return '$ ' + numericValue.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
  }
}


// Obtiene el valor numérico de un valor formateado
function obtenerValorNumerico(valorFormateado) {
  var valorNumerico = parseFloat(valorFormateado.replace(/[^0-9.-]+/g, ''));
  return isNaN(valorNumerico) ? 0 : valorNumerico;
}

// Mantiene el formato de moneda mientras se edita el campo
function formatValue(inputId) {
  var input = document.getElementById(inputId);

/*  input.addEventListener('input', function() {
      var cursorPos = this.selectionStart;
      var value = this.value;

      // Limpiar el valor de caracteres no numéricos excepto el punto decimal
      var cleanedValue = value.replace(/[^\d.]/g, '');

      // Formatear el valor
      var formattedValue = formatCurrency(cleanedValue);

      // Asignar el valor formateado al campo
      this.value = formattedValue;

      // Restaurar la posición del cursor
      this.selectionStart = cursorPos;
      this.selectionEnd = cursorPos;
  });   */

  // Manejar el evento de pérdida de foco
  input.addEventListener('blur', function() {
    var value = this.value.trim(); // Eliminar espacios en blanco al inicio y al final
    if (value !== '') {
        // Convertir valor a número y formatear como moneda
        var formattedValue = parseFloat(value.replace(/[^\d.]/g, '')).toFixed(2);
        this.value = '$ ' + formattedValue.replace(/\d(?=(\d{3})+\.)/g, '$&,'); // Aplicar formato
    }
});


  // Formatear el valor inicial al cargar la página
  var initialValue = input.value.replace(/[^\d.]/g, '');
  input.value = formatCurrency(initialValue);
}
 
// Inicializa el campo con el valor inicial y aplica formateo de moneda
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
  var inputs = document.querySelectorAll('.navigate');
  inputs.forEach(function(input) {
      addNavigation(input);
  });
}

// Habilita la navegación entre campos con la tecla Enter
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

// Envía los datos al servidor
function enviarDatos() {
  var valorFormateado = document.getElementById('txtCredito').value;
  var valorNumerico = obtenerValorNumerico(valorFormateado);

  fetch('/endpoint', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ valor: valorNumerico })
  })
  .then(response => response.json())
  .then(data => {
      console.log('Respuesta del servidor:', data);
  })
  .catch(error => {
      console.error('Error al enviar datos al servidor:', error);
  });
}
