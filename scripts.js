// Documento listo.
$(document).ready(function () {
    cargarProyectos();
});

// Carga el combo de proyectos con los datos del json
function cargarProyectos() {
    var proyectos = obtenerProyectos();

    $.each(proyectos, function (i, item) {
        if (item != undefined) {
            codigo = item.ProjectId;
            nombre = item.ProjectName;

            $("#slProyecto").append('<option value="' + codigo + '">' + nombre + '</option>');
        }
    });
}

// Al seleccionar un proyecto carga las tareas resumen como posibles sprints
$("#slProyecto").change(function () {
    $("#slSprint option").remove();
    $("#slSprint").append('<option>Selecciona un sprint</option>');

    var proyecto = Number($("#slProyecto option:selected").val());
    var tareasResumen = obtenerTareasResumen();

    $.each(tareasResumen, function (i, item) {
        if (item != undefined && item.ProjectId == proyecto) {
            codigo = item.TaskId;
            nombre = item.TaskName;

            $("#slSprint").append('<option value="' + codigo + '">' + nombre + '</option>');
        }
    });
});

// Al seleccionar un sprint hay que colocar los postits de sus taeas en la pizarra
$("#slSprint").change(function () {

    $("#lsBacklog li").remove();
    $("#lsPendiente li").remove();
    $("#lsProceso li").remove();
    $("#lsHecho li").remove();
    var tareaResumen = Number($("#slSprint option:selected").val());
    var tareas = obtenerTareas();

    $.each(tareas, function (i, item) {
        if (item != undefined && item.ParentTask == tareaResumen) {
            var tarjeta = crearTarjeta(item);

            if (item.TaskStatus == "Pendiente") {
                $("#lsPendiente").append(tarjeta);
            }
            else if (item.TaskStatus == "En curso") {
                $("#lsProceso").append(tarjeta);
            }
            else if (item.TaskStatus == "Completada") {
                $("#lsHecho").append(tarjeta);
            }
            else {
                $("#lsBacklog").append(tarjeta);
            }
        }
    });
});

// Crear tarjeta a partir de los datos
function crearTarjeta(tarea)
{
    var equipo = "";
    $.each(tarea.TaskManagers, function (i, item)
    {
        if (equipo != "")
        {
            equipo = equipo + "|";
        }
        equipo = equipo + item;
    });
    
    var tarjeta = '<li id="' + tarea.TaskId + '" class="card bg-danger" data-toggle="modal" data-target="#myModal"> ';
    tarjeta = tarjeta + '<div class="cardTitle">' + tarea.TaskName + '</div> ';
    tarjeta = tarjeta + '<div class="cardContent">' + tarea.TaskName + '</div> ';
    tarjeta = tarjeta + '<div class="priority">' + tarea.TaskPriority + '</div> ';
    tarjeta = tarjeta + '<div class="user">' + equipo + '</div> ';
    tarjeta = tarjeta + '</li>';

    return tarjeta;
}

// Cargar contenido al abrir la pantalla modal
$('#myModal').on('show.bs.modal', function (event) {
    var sId = $(event.relatedTarget).attr('id');
    $('#myModal .modal-title').html($('#' + sId + ' .priority').text());
    $('#myModal .modal-body #description').html($('#' + sId + ' .cardContent').html());
    $('#myModal .modal-body #team').html('Team: ' + $('#' + sId + ' .user').html());
});

// Eliminar contenido al cerrar la pantalla modal
$('#myModal').on('hide.bs.modal', function (event) {
    $('#myModal .modal-body #team').html('');
    $('#myModal .modal-body #team').html('');
});