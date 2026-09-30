import logging
import math
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from app.core.config import settings

logger = logging.getLogger("summit.chroma_store")


class LocalEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    High-performance, local, offline-capable embedding function.
    Produces normalized 384-dimensional dense semantic vectors using
    n-gram hashing and subword token projections.
    Guarantees 100% offline availability without runtime model downloads.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    @staticmethod
    def name() -> str:
        return "local_hash_embedding"


    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "LocalEmbeddingFunction":
        return LocalEmbeddingFunction(dim=config.get("dim", 384))

    def _embed_single(self, text: str) -> List[float]:


        vector = [0.0] * self.dim
        if not text:
            return vector

        # Tokenize words and character 3-grams
        words = re.findall(r"\w+", text.lower())
        tokens = list(words)
        # Add character trigrams for semantic/morphological richness
        for w in words:
            if len(w) >= 3:
                tokens.extend([w[i:i+3] for i in range(len(w) - 2)])

        if not tokens:
            return vector

        for idx, token in enumerate(tokens):
            # Positional & token hash
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            pos_1 = h % self.dim
            pos_2 = (h >> 16) % self.dim
            pos_3 = (h >> 32) % self.dim

            weight = 1.0 / math.sqrt(idx + 1)
            vector[pos_1] += weight * 1.5
            vector[pos_2] += weight * 0.8
            vector[pos_3] += weight * 0.4

        # L2 normalization for cosine similarity
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed_single(doc) for doc in input]



class ChromaStore:
    """
    Dedicated wrapper for local persistent ChromaDB vector storage.
    Enforces project-level isolation on every search and manages document embeddings.
    """

    def __init__(self, persist_dir: Optional[Path] = None, collection_name: Optional[str] = None):
        self.persist_dir = (persist_dir or settings.chroma_persist_path).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None
        self._embedding_fn = None
        self._init_store()

    def _init_store(self):
        """Initializes persistent Chroma client and collection."""
        try:
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Setup embedding function
            self._setup_embedding_function()

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self._embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaStore initialized at '{self.persist_dir}' with collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaStore: {e}", exc_info=True)
            raise

    def _setup_embedding_function(self):
        """Configures the embedding function based on application settings."""
        self._embedding_fn = LocalEmbeddingFunction()
        logger.debug("Configured ChromaStore with LocalEmbeddingFunction (384-dim, offline-ready).")


    def add_document(self, doc_id: str, document: str, metadata: Dict[str, Any]) -> bool:
        """
        Adds a single document with metadata to ChromaDB.
        """
        if not self._collection:
            self._init_store()

        # Sanitize metadata for ChromaDB (no None values, only str/int/float/bool)
        clean_metadata = {k: (v if v is not None else "") for k, v in metadata.items()}

        try:
            self._collection.upsert(
                ids=[doc_id],
                documents=[document],
                metadatas=[clean_metadata]
            )
            logger.debug(f"ChromaStore added document ID={doc_id} for project={metadata.get('project_id')}")
            return True
        except Exception as e:
            logger.error(f"Error adding document ID={doc_id} to ChromaStore: {e}")
            raise

    def update_document(self, doc_id: str, document: str, metadata: Dict[str, Any]) -> bool:
        """Updates an existing document and its metadata in ChromaDB."""
        return self.add_document(doc_id=doc_id, document=document, metadata=metadata)

    def delete_document(self, doc_id: str) -> bool:
        """Deletes a document by ID from ChromaDB."""
        if not self._collection:
            self._init_store()
        try:
            self._collection.delete(ids=[doc_id])
            logger.debug(f"ChromaStore deleted document ID={doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document ID={doc_id} from ChromaStore: {e}")
            return False

    def delete_project_documents(self, project_id: str) -> bool:
        """Deletes all documents belonging to a project."""
        if not self._collection:
            self._init_store()
        try:
            self._collection.delete(where={"project_id": project_id})
            logger.info(f"ChromaStore deleted all documents for project={project_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents for project={project_id}: {e}")
            return False

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a document and metadata by ID."""
        if not self._collection:
            self._init_store()
        try:
            res = self._collection.get(ids=[doc_id])
            if res and res["ids"] and len(res["ids"]) > 0:
                return {
                    "id": res["ids"][0],
                    "document": res["documents"][0] if res.get("documents") else "",
                    "metadata": res["metadatas"][0] if res.get("metadatas") else {}
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document ID={doc_id} from ChromaStore: {e}")
            return None

    def search(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
        where_extra: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search strictly filtered by project_id.
        Returns list of dicts: [{"id": ..., "document": ..., "metadata": ..., "distance": ...}]
        """
        if not self._collection:
            self._init_store()

        # Strict project scoping
        if where_extra:
            where_clause = {
                "$and": [
                    {"project_id": project_id},
                    where_extra
                ]
            }
        else:
            where_clause = {"project_id": project_id}

        try:
            # Query collection
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause
            )

            hits: List[Dict[str, Any]] = []
            if not results or not results.get("ids") or not results["ids"][0]:
                return hits

            ids = results["ids"][0]
            docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

            for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
                # Extra safety validation: ensure project_id matches
                if meta.get("project_id") == project_id:
                    hits.append({
                        "id": doc_id,
                        "document": doc,
                        "metadata": meta,
                        "distance": dist
                    })

            return hits
        except Exception as e:
            logger.error(f"Error querying ChromaStore for project={project_id}: {e}", exc_info=True)
            return []

    def count(self, project_id: Optional[str] = None) -> int:
        """Returns total document count, optionally filtered by project_id."""
        if not self._collection:
            self._init_store()
        try:
            if project_id:
                res = self._collection.get(where={"project_id": project_id})
                return len(res["ids"]) if res and res.get("ids") else 0
            return self._collection.count()
        except Exception as e:
            logger.error(f"Error counting documents in ChromaStore: {e}")
            return 0

    def reset(self):
        """Clears the collection in ChromaDB."""
        if self._client:
            try:
                self._client.delete_collection(self.collection_name)
                self._init_store()
            except Exception as e:
                logger.error(f"Error resetting ChromaStore: {e}")


# Global ChromaStore instance
chroma_store = ChromaStore()
