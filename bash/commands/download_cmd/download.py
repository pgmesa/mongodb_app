
import json

from grades import db_contollers as db
from grades.settings import BASE_DIR

def get_download_cmd():
    ...
    
def download(args:list=[]) -> None:
    stages = db.get_stages()
    for stage in stages:
        collection_docs = db.get_grades(stage, as_doc=True)
        with open(BASE_DIR/f'db_migrations/{stage}.json', "w") as file:
            json.dump(collection_docs, file, indent=4, sort_keys=True)
            
    