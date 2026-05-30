"""
reranker.py — Qwen3-Reranker cross-encoder reranking for CLIbrary.

Replaces the MaxSim heuristic in router.py with a generative cross-encoder.
Qwen3-Reranker outputs logits for token "yes" (9693) vs "no" (2152); the
softmax probability of "yes" is used as the relevance score.

Usage:
    from clibrary_hub.reranker import Qwen3Reranker
    reranker = Qwen3Reranker()
    scores = reranker.score(query, candidates)  # list of floats, same order as candidates
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

_DEFAULT_RERANKER_MODEL = "Qwen/Qwen3-Reranker-0.6B"
_YES_TOKEN_ID = 9693
_NO_TOKEN_ID  = 2152

_SYSTEM_PROMPT = (
    "Judge whether the Document meets the requirements based on the Query and "
    "the Instruct provided. Note that the answer can only be \"yes\" or \"no\"."
)
_INSTRUCT = (
    "Given a tool search query, determine if the following CLI tool description is relevant."
)


def _format_pair(query: str, cli_name: str, description: str, triggers: list[str]) -> str:
    trigger_str = "; ".join(triggers[:5]) if triggers else ""
    doc = f"{cli_name}: {description}"
    if trigger_str:
        doc += f". Example triggers: {trigger_str}"
    return doc


class Qwen3Reranker:
    """
    Wraps Qwen3-Reranker-0.6B for scoring (query, CLI) pairs.

    Parameters
    ----------
    model_name : str
        HuggingFace model ID.
    max_length : int
        Max token length for each (query, document) pair.
    """

    def __init__(
        self,
        model_name: str = _DEFAULT_RERANKER_MODEL,
        max_length: int = 512,
    ) -> None:
        self._model_name = model_name
        self._max_length = max_length
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForCausalLM | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name, padding_side="left")
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_name,
            torch_dtype=torch.float32,
        )
        self._model.eval()

    def _build_inputs(self, query: str, documents: list[str]) -> dict:
        assert self._tokenizer is not None
        # Template uses custom roles: "system"=instruction, "query"=query, "document"=document
        pairs = []
        for doc in documents:
            messages = [
                {"role": "system",   "content": _INSTRUCT},
                {"role": "query",    "content": query},
                {"role": "document", "content": doc},
            ]
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,  # template already adds <think></think>
            )
            pairs.append(text)

        return self._tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=self._max_length,
            return_tensors="pt",
        )

    @torch.no_grad()
    def score(
        self,
        query: str,
        candidates: list[dict],
    ) -> list[float]:
        """
        Score each candidate against the query.

        Parameters
        ----------
        query : str
            User intent.
        candidates : list[dict]
            Each dict must have keys: name, description. Optionally: triggers (list[str]).

        Returns
        -------
        list[float]
            Relevance scores in [0, 1], same order as candidates.
        """
        self._load()
        assert self._model is not None

        documents = [
            _format_pair(
                query,
                c["name"],
                c.get("description", ""),
                c.get("triggers", []),
            )
            for c in candidates
        ]

        inputs = self._build_inputs(query, documents)
        outputs = self._model(**inputs)

        # Last token logits → softmax over [yes, no]
        last_logits = outputs.logits[:, -1, :]
        yes_no_logits = last_logits[:, [_YES_TOKEN_ID, _NO_TOKEN_ID]]
        probs = F.softmax(yes_no_logits, dim=-1)
        return probs[:, 0].tolist()  # probability of "yes"

    def rerank(
        self,
        query: str,
        candidates: list[dict],
    ) -> list[tuple[dict, float]]:
        """
        Score and sort candidates by relevance descending.

        Returns list of (candidate_dict, score) tuples.
        """
        scores = self.score(query, candidates)
        return sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
