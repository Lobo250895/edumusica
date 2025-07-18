document.addEventListener('DOMContentLoaded', function() {
  const meses = document.querySelectorAll('.mes-circulo');
  const modal = document.getElementById('modalEfemerides');
  const spanCerrar = document.querySelector('.cerrar-modal');
  const tituloModal = document.getElementById('titulo-mes-modal');
  const contenidoModal = document.getElementById('efemerides-content');
  const nombreMesSeleccionado = document.getElementById('nombre-mes-seleccionado');
  
  // Datos de ejemplo de efemérides (deberías reemplazarlos con tus datos reales)
  const efemerides = {
    JAN: ["1 de enero: Año Nuevo","3 de enero: Usurpación de las Islas Malvinas","4 de enero: Firma del Pacto Federal",
       "6 de enero: Día de Reyes",
       "27 de enero: Día Internacional de Conmemoración en Memoria de las Víctimas del Holocausto",
       "31 de enero: Inauguracion de la asamblea del año Xlll"],
    FEB: ["14 de febrero: Día de San Valentín","20 de febrero: Dia mundial de la justicia social",
        "21 de febrero:Dia internacional de la lengua Materna"],
    MAR: ["1 de marzo: Inicio del ciclo lectivo de los Centros de Educación Física.",
        "3 de marzo al 4 de marzo: Carnaval - FERIADO NACIONAL (Ley N° 27.399).",
        "5 de marzo: Inicio del Ciclo Lectivo. Nivel Inicial - Nivel Primario - Nivel Secundario,",
         "Secundaria Técnica - Secundaria Agraria - Educación de Jóvenes Adultos y Adultos Mayores - Educación Artística (Esc. Artística) - Psicología Comunitaria y Pedagogía Social y Educación Especial.",
        "8 de marzo: Día Internacional de la Mujer","12 de marzo: Día del Escudo Nacional (Dec. PEN Nº 10.302/44).",
        "17 de marzo al 21 de marzo: Semana de reflexión en relación al Golpe de Estado perpetrado el24 de marzo de 1976 y las características del régimen que impuso. (Ley Prov. N° 11.782).",
        "21 de marzo: Día mundial del agua",
        "24  de marzo: Día Nacional de la Memoria por la Verdad y la Justicia (Leyes Nac. Nº 25.633 y Nº 26.085).",
        "25 de marzo al 28 de marzo: Primera Semana de la Convivencia Escolar (a excepción del Nivel Secundario, cuya implementación se ajusta a lo establecido en el Régimen Académico – Res. 1650/24).",
        "26 de marzo: Día del Mercosur Tratado de Asunción -1991- (Ley N° 25.783).",
        "27 de marzo: Día Mundial del Teatro (Ley Prov Nº 13.194).",
        "31 de marzo: Jornada de reflexión en homenaje a las víctimas de la tragedia ocurrida en la ","República de Cromañón (Decreto Nº 391/05).",
        "31 de marzo: Día de la Hermandad Latinoamericana (2-4)."],
    APR: ["1 de abril: Día Nacional de Concienciación sobre el Autismo. (Ley Nac.27053) (2-4).",
        "2 de abril: Día del Veterano y de los Caídos en la Guerra de Malvinas. - FERIADO NACIONAL Inamovible.",
        "3 de abril: Jornada de Reflexión por Día del Veterano y de los Caídos en la Guerra de Malvinas",
        "4 de abril: Día Mundial de la Actividad Física",
        "10 de abril: Día de la Ciencia y de la Técnica. Fecha de Nacimiento de Bernardo Houssay",
        "12 de abril al 13 de abril: Primeros dos días de la Pascua Judía",
        "14 de abril: Día de las Américas en conmemoración a la creación dela Organización de los Estados Americanos (OEA).",
        "14 de abril: Día de la Constitución Provincial.",
        "16 de abril: Día de la convivencia en la diversidad cultural, fecha del levantamiento del Ghetto de Varsovia",
        "17 de abril al 18 de abril: JUEVES SANTO DIA NO LABORABLE y VIERNES SANTO FERIADO NACIONAL ",
        "19 de abril y 20 de abril: Día del Aborigen Americano - Últimos dos días de la Pascua Judía.",
        "22 de abril: 40° aniversario del inicio del Juicio a las Juntas.",
        "23 de abril: Jornada de concientización en el marco de la Semana de la Vacunación en las Américas.",
        "24 de abril: Día de acción por la tolerancia y el respeto entre los pueblos, en conmemoración del primer genocidio del siglo XX.",
        "25 de abril: Día Internacional de las Niñas en las TIC - ONU.",
        "29 de abril: Día Internacional de la Danza UNESCO 1982. - Dia del animal",
        "30 de abril: Día de las trabajadoras y los trabajadores."
        
    ],
    MAY: ["1 de mayo: Día del Trabajador",  "3 de mayo: Día Mundial de la Libertad de Prensa",
      "8 de mayo: Día de la Cruz Roja Internacional","10 de mayo: Día de la Madre (en algunos países)",
      "11 de mayo: Día del Himno Nacional Argentino","17 de mayo: Día Mundial del Reciclaje",
      "25 de mayo: Dia de la revolucion de mayo  )"],
    JUN: ["3 de junio: Ni Una Menos (movilización contra la violencia de género)","5 de junio: Día Mundial del Medio Ambiente",
       "17 de junio: Paso a la Inmortalidad del General Martín Miguel de Güemes","20 de junio: Día de la Bandera, conmemorando el fallecimiento del General Manuel Belgrano, creador de la bandera argentina.",
       "21 de junio: Solsticio de verano","26 de junio: Día Internacional de Apoyo a las Víctimas de la Tortura"],
    JUL: ["4 de julio: Día de la Independencia de EE.UU.","9 de julio: Dia de la Independencia",
      "18 de julio: Conmemoración del atentado a la AMIA","20 de julio: Día del Amigo"],
    AUG: ["1 de agosto: Día de la Pachamama","12 de agosto: Día Internacional de la Juventud",
      "17 de agosto: Paso a la Inmortalidad del General José de San Martín",
       "22 de agosto: Día Mundial del Folklore",
      "30 de agosto: Día Internacional de las Víctimas de Desapariciones Forzadas"
    ],
    SEP: ["4 de septiembre: Día del Inmigrante",
          "11 de septiembre: Día del Maestro",
          "13 de septiembre: Día del Bibliotecario",
          "21 de septiembre: Día del Estudiante, Día de la Primavera y Día del Fotógrafo",
          "23 de septiembre: Día Nacional de los Derechos Políticos de la Mujer"],
    OCT: ["4 de octubre: Día del Voluntariado Hospitalario",
          "12 de octubre: Día del Respeto a la Diversidad Cultural",
          "17 de octubre: Día de la Lealtad",
          "24 de octubre: Día de las Naciones Unidas"],
    NOV: [ "1 de noviembre: Día de Todos los Santos",
          "8 de noviembre: Día del Empleado Municipal",
          "10 de noviembre: Día de la Tradición",
          "19 de noviembre: Día Internacional del Hombre",
          "20 de noviembre: Día de la Soberanía Nacional",
          "25 de noviembre: Día Internacional de la Eliminación de la Violencia contra la Mujer"],
    DEC: ["1 de diciembre: Día Mundial de la Lucha contra el SIDA",
          "8 de diciembre: Día de la Inmaculada Concepción de María",
          "10 de diciembre: Día de la Restauración de la Democracia",
          "25 de diciembre: Navidad",
          "31 de diciembre: Fin de Año"],
  };
  
  meses.forEach(mes => {
    mes.addEventListener('click', function() {
      // Remover clase active de todos los meses
      meses.forEach(m => m.classList.remove('active'));
      
      // Agregar clase active al mes seleccionado
      this.classList.add('active');
      
      const mesSeleccionado = this.getAttribute('data-month');
      const nombresMeses = {
        JAN: "Enero", FEB: "Febrero", MAR: "Marzo", APR: "Abril",
        MAY: "Mayo", JUN: "Junio", JUL: "Julio", AUG: "Agosto",
        SEP: "Septiembre", OCT: "Octubre", NOV: "Noviembre", DEC: "Diciembre"
      };
      
      // Actualizar el indicador del mes seleccionado
      nombreMesSeleccionado.textContent = `Mes seleccionado: ${nombresMeses[mesSeleccionado]}`;
      
      // Mostrar el modal con las efemérides
      tituloModal.textContent = `Efemérides de ${nombresMeses[mesSeleccionado]}`;
      
      // Cargar las efemérides del mes seleccionado
      if (efemerides[mesSeleccionado]) {
        contenidoModal.innerHTML = `
          <ul>
            ${efemerides[mesSeleccionado].map(efem => `<li>${efem}</li>`).join('')}
          </ul>
        `;
      } else {
        contenidoModal.innerHTML = `<p>No hay efemérides registradas para este mes.</p>`;
      }
      
      modal.style.display = "block";
    });
  });
  
  // Cerrar modal al hacer clic en la X
  spanCerrar.addEventListener('click', function() {
    modal.style.display = "none";
  });
  
  // Cerrar modal al hacer clic fuera del contenido
  window.addEventListener('click', function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
});


 // Función para mostrar el PDF en el visor y abrir el modal
 function verPDFModal(url) {
  const visor = document.getElementById('visor-pdf');
  visor.src = url;  // Establece la URL del PDF
  document.getElementById('visor-modal').style.display = 'block';  // Muestra el modal
}

// Cierra el modal y limpia el iframe
function cerrarModal() {
  document.getElementById('visor-modal').style.display = 'none';
  document.getElementById('visor-pdf').src = '';  // Limpia el src para detener carga
}

// Cerrar el modal si se hace clic fuera del contenido
window.onclick = function(event) {
  const modal = document.getElementById('visor-modal');
  if (event.target === modal) {
    cerrarModal();
  }
}


