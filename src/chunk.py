def chunk_by_structure(text: str, max_chunk_size: int = 500) -> list[str]:
    '''
    Divise un document Markdown en chunks cohérents basés sur la structure des titres
    
    :param text: Contenu du fichier Markdown
    :type text: str
    :param max_chunk_size: Taille maximale d'un chunk (en caractères)
    :type max_chunk_size: int
    :return: Liste de chunks textuels
    :rtype: list[str]
    '''
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 pour la newline
        
        # Si c'est un titre (niveau 1 ou 2) et on a déjà du contenu, sauvegarder le chunk
        if (line.startswith('# ') or line.startswith('## ')) and current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
            current_chunk = [line]
            current_size = line_size
        
        # Si ajouter cette ligne dépasse la limite, sauvegarder le chunk
        elif current_size + line_size > max_chunk_size and current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
            current_chunk = [line]
            current_size = line_size
        
        # Sinon, ajouter la ligne au chunk courant
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Ajouter le dernier chunk s'il n'est pas vide
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)
    
    return chunks


def chunk_documents(loaded_files: dict[str, str], max_chunk_size: int = 500) -> dict[str, list[str]]:
    '''
    Découpe tous les documents chargés en chunks cohérents
    
    :param loaded_files: Dictionnaire de fichiers chargés (clé: nom du fichier, valeur: contenu)
    :type loaded_files: dict[str, str]
    :param max_chunk_size: Taille maximale d'un chunk
    :type max_chunk_size: int
    :return: Dictionnaire avec chunks par fichier
    :rtype: dict[str, list[str]]
    '''
    chunked_documents = {}
    
    for file_name, content in loaded_files.items():
        chunked_documents[file_name] = chunk_by_structure(content, max_chunk_size)
    
    return chunked_documents