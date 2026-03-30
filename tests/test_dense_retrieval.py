import numpy as np
import pytest
import torch
from unittest.mock import MagicMock
from tools.dense_retrieval import hybrid_dense_retrieval


class DummyState:
    def __init__(self):
        self.user_query = "dummy query"
        self.repositories = [
            {"combined_doc": "Test document one about machine learning."},
            {"combined_doc": "Another test document with more text about deep learning."},
        ]


class DummyConfig:
    def __init__(self):
        self.configurable = {
            "colbert_model_name": "dummy-colbert",
            "dense_retrieval_k": 10,
        }


def _make_dummy_model_output(text):
    """Return a fake last_hidden_state tensor based on text length."""
    seq_len = max(1, len(text.split()))
    hidden = torch.ones(1, seq_len, 4)  # (batch, seq, hidden_dim)
    out = MagicMock()
    out.last_hidden_state = hidden
    return out


def test_neural_dense_retrieval(monkeypatch):
    dummy_tokenizer = MagicMock()
    dummy_tokenizer.side_effect = lambda text, **kwargs: {
        "input_ids": torch.zeros(1, max(1, len(text.split())), dtype=torch.long)
    }
    dummy_tokenizer.__call__ = dummy_tokenizer.side_effect

    dummy_model = MagicMock()
    dummy_model.return_value = _make_dummy_model_output("placeholder")
    dummy_model.side_effect = lambda **inputs: _make_dummy_model_output(
        " ".join(str(v.shape) for v in inputs.values())
    )

    mock_tokenizer_cls = MagicMock(return_value=dummy_tokenizer)
    mock_model_cls = MagicMock(return_value=dummy_model)

    monkeypatch.setattr("tools.dense_retrieval.AutoTokenizer", mock_tokenizer_cls)
    monkeypatch.setattr("tools.dense_retrieval.AutoModel", mock_model_cls)

    state = DummyState()
    config = DummyConfig().__dict__
    result = hybrid_dense_retrieval(state, config)

    ranked = state.semantic_ranked
    assert len(ranked) == len(state.repositories)
    assert "semantic_ranked" in result
    assert ranked[0]["semantic_similarity"] >= ranked[-1]["semantic_similarity"]
