"""
Conversation memory management using FAISS and sentence-transformers.
This module stores and retrieves conversational context across sessions.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import numpy as np
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class ConversationMemory:
    """Manages conversational memory using a FAISS vector index."""

    def __init__(
        self,
        storage_dir: str = "memory_store",
        index_filename: str = "memory.index",
        metadata_filename: str = "metadata.json",
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.storage_dir = storage_dir
        self.index_path = os.path.join(storage_dir, index_filename)
        self.metadata_path = os.path.join(storage_dir, metadata_filename)
        self.embedding_model_name = embedding_model

        os.makedirs(self.storage_dir, exist_ok=True)

        self.model = SentenceTransformer(self.embedding_model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        self.index = self._load_index()
        self.metadata: List[Dict[str, Any]] = self._load_metadata()

        # Ensure index and metadata sizes match; rebuild if necessary
        if self.index.ntotal != len(self.metadata):
            self._rebuild_index_from_metadata()

    def _load_index(self) -> faiss.Index:
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        return faiss.IndexFlatIP(self.dimension)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _rebuild_index_from_metadata(self):
        """Rebuild FAISS index from stored metadata embeddings."""
        self.index = faiss.IndexFlatIP(self.dimension)
        if not self.metadata:
            self._save_index()
            return

        embeddings = np.array(
            [entry["embedding"] for entry in self.metadata], dtype="float32"
        )
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self._save_index()

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)

    def _save_metadata(self):
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def _create_embedding(self, text: str) -> np.ndarray:
        embedding = self.model.encode(
            text, convert_to_numpy=True, normalize_embeddings=True
        )
        return embedding.astype("float32")

    def _format_embedding_text(
        self, user_query: str, sql_query: str, analysis: str, data_preview: str
    ) -> str:
        parts = [
            f"User Query: {user_query}",
            f"SQL Query: {sql_query}",
            f"Analysis: {analysis}",
        ]
        if data_preview:
            parts.append(f"Data Preview: {data_preview}")
        return "\n".join(parts)

    def add_entry(
        self,
        session_id: str,
        user_query: str,
        sql_query: str,
        analysis: str,
        data_preview: str,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a new conversational memory entry."""
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        embedding_text = self._format_embedding_text(
            user_query=user_query,
            sql_query=sql_query,
            analysis=analysis,
            data_preview=data_preview,
        )
        embedding = self._create_embedding(embedding_text)

        metadata_entry: Dict[str, Any] = {
            "id": entry_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "user_query": user_query,
            "sql_query": sql_query,
            "analysis": analysis,
            "data_preview": data_preview,
            "embedding_text": embedding_text,
            "embedding": embedding.tolist(),
        }

        if extra_metadata:
            metadata_entry.update(extra_metadata)

        self.metadata.append(metadata_entry)
        self.index.add(np.expand_dims(embedding, axis=0))

        self._save_index()
        self._save_metadata()

        return metadata_entry

    def _prepare_context_snippet(self, entry: Dict[str, Any]) -> str:
        snippet = [
            f"- Timestamp: {entry.get('timestamp')}",
            f"- User Query: {entry.get('user_query')}",
            f"- SQL Query: {entry.get('sql_query')}",
            f"- Analysis Summary: {entry.get('analysis')}",
        ]
        if entry.get("data_preview"):
            snippet.append(f"- Data Preview: {entry.get('data_preview')}")
        return "\n".join(snippet)

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k_session: int = 5,
        top_k_global: int = 5,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search for relevant conversation memories."""
        if not self.metadata or self.index.ntotal == 0:
            return []

        embedding = self._create_embedding(query)
        top_k = min(len(self.metadata), max(top_k_session, top_k_global) * 2)
        scores, indices = self.index.search(
            np.expand_dims(embedding, axis=0), top_k
        )

        flat_indices = indices[0]
        flat_scores = scores[0]

        session_results: List[Dict[str, Any]] = []
        global_results: List[Dict[str, Any]] = []

        for idx, score in zip(flat_indices, flat_scores):
            if idx < 0 or idx >= len(self.metadata):
                continue
            if float(score) < similarity_threshold:
                continue
            entry = {
                key: value
                for key, value in self.metadata[idx].items()
                if key != "embedding"
            }
            entry["similarity"] = float(score)

            if session_id and entry.get("session_id") == session_id:
                if len(session_results) < top_k_session:
                    entry["context_snippet"] = self._prepare_context_snippet(entry)
                    session_results.append(entry)
            else:
                if len(global_results) < top_k_global:
                    entry["context_snippet"] = self._prepare_context_snippet(entry)
                    global_results.append(entry)

            if len(session_results) >= top_k_session and len(global_results) >= top_k_global:
                break

        combined_results = session_results + [
            entry for entry in global_results if entry not in session_results
        ]
        return combined_results[: top_k_session + top_k_global]

    def reset_session(self, session_id: str):
        """Remove all entries for a given session and rebuild the index."""
        if not session_id:
            return

        original_length = len(self.metadata)
        self.metadata = [
            entry for entry in self.metadata if entry.get("session_id") != session_id
        ]

        if len(self.metadata) != original_length:
            self._rebuild_index_from_metadata()
            self._save_metadata()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Return summary information about stored sessions."""
        sessions: Dict[str, Dict[str, Any]] = {}
        for entry in self.metadata:
            sid = entry.get("session_id")
            if sid not in sessions:
                sessions[sid] = {
                    "session_id": sid,
                    "count": 0,
                    "latest_timestamp": entry.get("timestamp"),
                }
            sessions[sid]["count"] += 1
            if entry.get("timestamp") > sessions[sid]["latest_timestamp"]:
                sessions[sid]["latest_timestamp"] = entry.get("timestamp")

        return sorted(
            sessions.values(), key=lambda s: s.get("latest_timestamp", ""), reverse=True
        )

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all entries for a given session ordered by timestamp."""
        if not session_id:
            return []
        entries = [
            entry for entry in self.metadata if entry.get("session_id") == session_id
        ]
        return sorted(entries, key=lambda e: e.get("timestamp", ""))


