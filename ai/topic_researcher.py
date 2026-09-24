import json
import logging
from typing import Dict, Any, List
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.topics")


def discover_kids_topics(limit: int = 8) -> List[Dict[str, Any]]:
    """
    Exclusively uses the configured Live AI model (OpenRouter / Ollama / Claude) to research 
    and generate 100% dynamic, fresh YouTube Kids topic opportunities.
    ZERO static fallback.
    """
    provider = get_ai_provider()
    provider_name = provider.__class__.__name__
    model_name = getattr(provider, "model", "default")

    logger.info(f"Researching dynamic kids topics using {provider_name} (Model: {model_name})...")

    prompt = f"""Generate {limit} brand new, unique, high-performing YouTube Kids 3D animated nursery rhyme and preschool educational song topic opportunity cards.
Target Audience: Toddlers & Preschoolers (Ages 1-5).
Style Reference: Cocomelon, Super Simple Songs, Little Baby Bum.

Return ONLY a valid JSON object with a "topics" array containing exactly {limit} creative topic objects.
Each topic object MUST contain:
- "topic": Short punchy theme name
- "suggested_title": High-CTR engaging YouTube title with friendly emojis
- "category": Choose from ("Vehicles & Animals", "Numbers & Counting", "Good Habits", "Bedtime Lullabies", "Colors & Shapes", "Social-Emotional", "Adventure & Science")
- "target_age": e.g. "1–3 Years" or "2–5 Years"
- "search_keywords": list of 5 high-intent preschool search keywords
- "content_angle": 1 sentence explaining the musical & visual engagement hook
- "why_worth_considering": 1 sentence audience & parental appeal rationale
- "opportunity_signals": 1 sentence search trend & repetition value indicator
- "suggested_characters": list of 3-4 cute character names
- "suggested_story_concept": 1-2 sentence animated storyboard concept
"""
    system_prompt = "You are a world-class YouTube Kids preschool content strategist and song idea creator. Output strictly valid JSON with no markdown and no conversational preamble."

    try:
        res = provider.generate_json(prompt, system_prompt, max_tokens=2500)
        if res and "topics" in res and isinstance(res["topics"], list) and len(res["topics"]) > 0:
            logger.info(f"Successfully generated {len(res['topics'])} dynamic topics via {model_name}")
            return res["topics"][:limit]
        
        last_err = getattr(provider, "last_error", "Model returned empty response or invalid JSON.")
        raise RuntimeError(f"{model_name}: {last_err}")
    except Exception as e:
        err_msg = getattr(provider, "last_error", str(e))
        logger.error(f"AI Topic Generation failed for model {model_name}: {err_msg}")
        raise RuntimeError(f"AI Topic Generation Failed for {model_name}: {err_msg}. Please check your OpenRouter API Key, model selection, or credits in Settings.")
