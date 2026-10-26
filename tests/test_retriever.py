
from app.services.rag_service import RunbookRetriever


def test_runbook_retrieval():
    retriever = RunbookRetriever()

    results = retriever.search(
        "HDFS DataNode block replication failure",
        top_k=3,
    )

    print(f"\nMatching runbooks: {len(results)}")

    for result in results:
        print(result)

    assert isinstance(results, list)
