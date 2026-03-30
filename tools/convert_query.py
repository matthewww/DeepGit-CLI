# tools/convert_query.py
import logging
from tools.chat import iterative_convert_to_search_tags

logger = logging.getLogger(__name__)

def convert_searchable_query(state, config):
    raw = iterative_convert_to_search_tags(state.user_query)
    state.searchable_query = raw
    logger.info(f"Converted searchable query: {raw}")
    return {"searchable_query": raw}
