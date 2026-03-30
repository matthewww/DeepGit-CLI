# tools/filtering.py
import logging

logger = logging.getLogger(__name__)

def threshold_filtering(state, config):
    """Filters out repos with too few stars AND too-low cross-encoder scores."""
    from agent import AgentConfiguration
    agent_config = AgentConfiguration.from_runnable_config(config)

    filtered = []
    for repo in state.reranked_candidates:
        stars = repo.get("stars", 0)
        ce_score = repo.get("cross_encoder_score", 0.0)
        # Drop only if BOTH star count AND cross-encoder score are too low.
        if stars < agent_config.min_stars and ce_score < agent_config.cross_encoder_threshold:
            continue
        filtered.append(repo)

    # If nothing passes, keep all reranked candidates.
    if not filtered:
        filtered = list(state.reranked_candidates)

    state.filtered_candidates = filtered
    logger.info(f"Filtering complete: {len(filtered)} candidates remain.")
    return {"filtered_candidates": filtered}
