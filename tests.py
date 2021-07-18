from controllers.db_controller import get_model

from bash.commands.migrate_cmd.migrate import migrate
# print(get_model("grades", "Carrera"))

# order = ["_id",
#         "Asignatura", 
#         "Curso",
#         "Cuatri",
#         "Nota Entregas",
#         "Nota Practicas",
#         "Parcial 1",
#         "Parcial 2",
#         "Nota Final",
#         "Calificacion"]
# print(order)
# migrate('Carrera (Ingenieria Biomedica).json',
#         "Grades",
#         "Carrera (Ingenieria Biomedica)",
#         attrs_order=order,
#         reverse=True)

from server.server import _get_extra_vars, _set_extra_vars, _extra_vars

_set_extra_vars({"hola": "pepe"}, "home")
print(_extra_vars)
print(_get_extra_vars("home"))
print(_get_extra_vars("home"))
print(_get_extra_vars("luis"))