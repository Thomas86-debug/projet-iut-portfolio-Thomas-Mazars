import os
from pathlib import Path

def load_files(data_dir: str | None = None) -> dict[str, str]:
    '''
    Charge tous les fichiers Markdown du dossier data
    
    :param data_dir: Chemin du dossier contenant les fichiers
    :type data_dir: str
    :return: Dictionnaire avec chemin du fichier comme clé et contenu comme valeur
    :rtype: dict[str, str]
    '''
    loaded_files = {}
    
    # Obtenir le chemin absolu du dossier data (par défaut : ../data depuis ce fichier)
    if data_dir is None:
        data_path = (Path(__file__).resolve().parent / ".." / "data").resolve()
    else:
        data_path = Path(data_dir).resolve()
    
    # Vérifier que le dossier existe
    if not data_path.exists():
        raise FileNotFoundError(f"Le dossier {data_path} n'existe pas")
    
    # Parcourir tous les fichiers .md du dossier
    for file_path in data_path.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                loaded_files[file_path.name] = file.read()
        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {e}")
    
    return loaded_files