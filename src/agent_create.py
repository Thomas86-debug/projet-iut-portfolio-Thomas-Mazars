import asyncio
from agents import Agent, Runner, function_tool
from index import create_index_connection
from dotenv import load_dotenv

load_dotenv(override=True)


@function_tool
def search_portfolio(query: str) -> str:
    """
    Cherche dans l'index Upstash pour trouver des informations du portfolio.
    
    :param query: Requête de recherche (expériences, compétences, projets)
    :type query: str
    :return: Résultats pertinents du portfolio
    :rtype: str
    """
    try:
        index = create_index_connection()
        results = index.query(
            data=query,
            top_k=5,
            include_metadata=True,
            include_data=True,
        )
        
        # Formater les résultats
        formatted_results = []
        for result in results:
            metadata = result.metadata or {}
            source = metadata.get("source", "Unknown")
            content = result.data or ""
            if content:
                formatted_results.append(f"[{source}] {content}")

        return "\n".join(formatted_results) if formatted_results else "Aucune information trouvée"
    except Exception as e:
        return f"Erreur lors de la recherche: {str(e)}"


def create_portfolio_agent() -> Agent:
    """
    Crée et configure l'agent portfolio avec les outils appropriés.
    
    :return: Instance de l'agent configuré
    :rtype: Agent
    """
    agent = Agent(
        name="Portfolio Assistant",
        instructions=(
            "Tu es un assistant utile qui répond à des questions sur mon portfolio. "
            "Utilise l'outil search_portfolio pour trouver des informations pertinentes. "
            "Réponds en français de manière claire et précise."
        ),
        model="gpt-4o-mini",
        tools=[search_portfolio]
    )
    return agent


async def main():
    """
    Pipeline complet : indexation puis interaction avec l'agent.
    """
    print("🚀 Démarrage du pipeline complet...")
    print("=" * 50)
    
    # 1. Indexer les documents (load → chunk → index)
    print("\n📚 Phase 1 : Indexation des documents...")
    try:
        from index import index_documents_pipeline
        result = index_documents_pipeline()
        print(f"✓ {result['total_chunks']} chunks indexés depuis {result['files_processed']} fichiers")
    except Exception as e:
        print(f"❌ Erreur lors de l'indexation: {e}")
        return
    
    # 2. Créer l'agent
    print("\n🤖 Phase 2 : Initialisation de l'agent...")
    agent = create_portfolio_agent()
    print(f"✓ Agent '{agent.name}' créé avec succès")
    
    # 3. Interagir avec l'agent
    print("\n💬 Phase 3 : Test de l'agent...")
    print("=" * 50)
    
    test_queries = [
        "Quelles sont mes principales compétences?",
        "Décris mes expériences professionnelles",
        "Quels sont mes projets les plus importants?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Question: {query}")
        try:
            result = await Runner.run(agent, query)
            print(f"🤖 Réponse: {result.final_output}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Pipeline complet terminé!")


if __name__ == "__main__":
    asyncio.run(main())