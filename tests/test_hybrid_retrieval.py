"""
Unit tests for Hybrid Retrieval (Dense Vector Embeddings + Sparse BM25 FTS5).
"""

import unittest
from database.hybrid_retrieval import DenseSemanticEmbedder, HybridRetriever, get_hybrid_engine


class TestHybridRetrieval(unittest.TestCase):
    def setUp(self):
        self.retriever = get_hybrid_engine()
        self.embedder = self.retriever.embedder

    def test_dense_embedder_similarity(self):
        sim1 = self.embedder.cosine_similarity("heartburn and acid reflux", "burning chest and acid indigestion")
        sim2 = self.embedder.cosine_similarity("heartburn and acid reflux", "fractured bone in leg")

        self.assertGreater(sim1, 0.3, "Related acid reflux queries should show high semantic similarity")
        self.assertLess(sim2, sim1, "Unrelated query should have lower similarity than related query")

    def test_colloquial_synonym_expansion(self):
        # Query with colloquial terms: "tummy burning throat" should retrieve Acid Reflux / GERD
        results = self.retriever.hybrid_search("tummy burning and acid in throat", top_k=3)
        self.assertTrue(len(results) > 0)
        top_names = [r["disease_name"] for r in results]
        self.assertTrue(any("Reflux" in name or "GERD" in name or "Acidity" in name for name in top_names))

    def test_exact_medical_term_retrieval(self):
        # Query with exact condition name
        results = self.retriever.hybrid_search("Migraine photophobia aura", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("Migraine", results[0]["disease_name"])

    def test_respiratory_wheezing_retrieval(self):
        results = self.retriever.hybrid_search("asthma wheezing breathlessness inhaler", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("Asthma", results[0]["disease_name"])

    def test_empty_query_resilience(self):
        results = self.retriever.hybrid_search("", top_k=3)
        self.assertEqual(len(results), 0)

    def test_singleton_retriever_is_loaded(self):
        engine = get_hybrid_engine()
        self.assertIsNotNone(engine)
        self.assertTrue(engine.embedder.is_indexed)
        self.assertGreater(len(engine.embedder.doc_vectors), 10)


if __name__ == '__main__':
    unittest.main()
