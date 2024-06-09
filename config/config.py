config_curve = {
    "forgetting_T": 24,
    "expand_overall": 5,
    "expand_y": 20,
    "offset_x": 1,
    "forever_remember": 5,
    "forgetting_min": 0.3
}

short_term_space = {
    "prefetch_space_size": 512,
    "history_turn_max": 4,
    "prefetch_frequency": 5,
    "top_p_summaries": 5,
    "top_p_dialogs_in_summary": 2,
    "top_p_dialogs": 1
}

language = ['cn', 'en']
top_p_for_personality = 5
top_p_for_summary = 5
without_topic_history_turn_max = 8  # 8
trigger_forgetting_frequency = 1 * 3600

openai_key = []
