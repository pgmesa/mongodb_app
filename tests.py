from controllers.db_controller import get_model

from bash.commands.migrate_cmd.migrate import migrate
# print(get_model("grades", "Carrera"))

order = ["_id",
        "Asignatura", 
        "Curso",
        "Cuatri",
        "Nota Entregas",
        "Nota Practicas",
        "Parcial 1",
        "Parcial 2",
        "Nota Final",
        "Calificacion"]
print(order)
migrate('Carrera (Ingenieria Biomedica).json',
        "Grades",
        "Carrera (Ingenieria Biomedica)",
        attrs_order=order,
        reverse=True)

def sort_dict(attrs_order:list, dict_:dict) -> dict:
    sorted_dict = {}
    for i in range(len(dict_)):
        attr = attrs_order[i]
        keys = list(dict_.keys())
        values = list(dict_.values())
        for key, value in zip(keys, values):
            if key == attr:
                dict_.pop(key)
                sorted_dict[key] = value
                break
    return sorted_dict

# a = {"adios":"pepe", "buenas": "luis", "tardes": "manolo"}

# sorted_dict = sort_dict(["buenas", "tardes", "adios"], a)

# print(sorted_dict)