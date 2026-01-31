import os
from dotenv import load_dotenv
from upstash_vector import Index, Vector

load_dotenv(override=True)


def create_index_connection() -> Index:
    '''
    Crée une connexion à l'index Upstash Vector
    
    :return: Instance de l'index Upstash
    :rtype: Index
    '''
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"), 
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )
    return index


def index_chunks(chunked_documents: dict[str, list[str]], index: Index = None) -> dict:
    '''
    Indexe les chunks de documents dans Upstash Vector
    
    :param chunked_documents: Dictionnaire avec chunks par fichier
    :type chunked_documents: dict[str, list[str]]
    :param index: Instance de l'index Upstash (optionnel)
    :type index: Index
    :return: Résultat de l'indexation avec statistiques
    :rtype: dict
    '''
    if index is None:
        index = create_index_connection()
    
    vectors = []
    total_chunks = 0
    
    # Préparer tous les vecteurs
    for file_name, chunks in chunked_documents.items():
        for i, chunk in enumerate(chunks):
            vector_id = f"{file_name}-chunk-{i}"
            
            vectors.append(
                Vector(
                    id=vector_id,
                    data=chunk,
                    metadata={
                        "source": file_name,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
            )
            total_chunks += 1
    
    # Indexer tous les vecteurs dans Upstash
    result = index.upsert(vectors=vectors)
    
    return {
        "status": "success",
        "total_chunks": total_chunks,
        "files_processed": len(chunked_documents),
        "upstash_result": result
    }


def index_documents_pipeline(index: Index = None) -> dict:
    '''
    Pipeline complet : charge, découpe et indexe les documents
    
    :param index: Instance de l'index Upstash (optionnel)
    :type index: Index
    :return: Résultat de l'indexation
    :rtype: dict
    '''
    from load import load_files
    from chunk import chunk_documents
    
    # 1. Charger les fichiers
    loaded_files = load_files()
    print(f"✓ {len(loaded_files)} fichiers chargés")
    
    # 2. Découper en chunks
    chunked = chunk_documents(loaded_files)
    total_chunks = sum(len(chunks) for chunks in chunked.values())
    print(f"✓ {total_chunks} chunks créés")
    
    # 3. Indexer dans Upstash
    result = index_chunks(chunked, index)
    print(f"✓ Indexation terminée")
    
    return result


if __name__ == "__main__":
    print("🚀 Démarrage du pipeline : load → chunk → index")
    result = index_documents_pipeline()
    print(f"\n✅ Pipeline terminé avec succès!")
    print(f"Résumé : {result['total_chunks']} chunks indexés depuis {result['files_processed']} fichiers")
