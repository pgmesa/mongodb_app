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

from controllers import db_controller as dbc

# def update_old_models(coll_to_fix=None):
#     dbs = dbc.list_dbs()
#     for db in dbs:
#         collections = dbc.list_collections(db)
#         for collection in collections:
#             if collection != coll_to_fix and coll_to_fix is not None: continue
#             model = dbc.get_model(db, collection)
#             if bool(model):
#                 if type(model["attr1"]) is not dict:
#                     print("fixed", db, collection)
#                     new_model = {}
#                     for attr, name in model.items():
#                         new_model[attr] = {"name": name, "type": "str"}
#                     dbc.update_model(db, collection, new_model.values(), fix_old_models=True)
                        
# update_old_models()


from mypy_modules.register import register
from server.server import _get_extra_vars, _set_extra_vars

reg = register.load()
print(reg)
