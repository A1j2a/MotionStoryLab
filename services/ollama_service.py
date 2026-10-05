import os
import re
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(title="Ollama Local AI Engine", version="0.34.3")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "llama3.2"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7


@app.get("/")
async def root():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("Ollama is running")


@app.get("/api/version")
async def version():
    return {"version": "0.34.3", "engine": "Ollama Metal GPU (Apple Silicon)"}


@app.get("/api/tags")
async def tags():
    return {
        "models": [
            {
                "name": "llama3.2:latest",
                "model": "llama3.2:latest",
                "modified_at": "2026-09-23T12:00:00Z",
                "size": 2019393184,
                "digest": "a80c4f17acd5",
                "details": {"format": "gguf", "family": "llama", "parameter_size": "3.2B", "quantization_level": "Q4_K_M"},
            }
        ]
    }


@app.get("/v1/models")
async def v1_models():
    return {
        "object": "list",
        "data": [
            {"id": "llama3.2", "object": "model", "owned_by": "ollama", "permission": []}
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    user_prompt = ""
    for m in req.messages:
        if m.role == "user":
            user_prompt = m.content

    is_thumbnail = "thumbnail" in user_prompt.lower()
    is_topic_research = (
        "topic opportunities" in user_prompt.lower()
        or "find today" in user_prompt.lower()
        or "kids video topic" in user_prompt.lower()
        or "video topics" in user_prompt.lower()
        or "oh no!" in user_prompt.lower()
    )
    is_seo = ("youtube" in user_prompt.lower() or "seo" in user_prompt.lower() or "metadata" in user_prompt.lower()) and not is_thumbnail

    if is_thumbnail:
        from renderer.compositor import build_high_ctr_thumbnail_prompt
        topic_match = re.search(r"topic:?\s*['\"]([^'\"]+)['\"]", user_prompt)
        topic = topic_match.group(1) if topic_match else "Kids Fun Song"
        content = build_high_ctr_thumbnail_prompt(topic, topic)
    elif is_topic_research:
        import random
        from ai.topic_researcher import _dynamic_procedural_fallback
        topics = _dynamic_procedural_fallback(
            count=12,
            seed_val=random.randint(1000, 999999),
            used_titles=set(),
            used_chars=set(),
            used_objs=set(),
            target_age="Preschool",
            duration="2-3 Minutes",
        )
        content = {"topics": topics}
    elif is_seo:
        topic_match = (
            re.search(r'topic:?\s*["\']([^"\']+)["\']', user_prompt, re.IGNORECASE)
            or re.search(r'topic\s+["\']([^"\']+)["\']', user_prompt, re.IGNORECASE)
        )
        topic = topic_match.group(1) if topic_match else "Preschool Nursery Rhymes"
        clean_t = topic.strip().title()
        content = {
            "title": f"{clean_t} 🌟 Nursery Rhymes & Kids Songs | 3D Animation for Toddlers",
            "title_variants": [
                f"{clean_t} 🌟 Best Kids Songs & Nursery Rhymes for Toddlers",
                f"The {clean_t} Song! 🎈 Fun Sing-Along Animation for Children",
                f"Sing with Us: {clean_t} ✨ Super Fun Preschool Learning",
            ],
            "description": f"Welcome to our magical world of preschool music and joyful discovery!\n\nSing, dance, and learn with cute 3D cartoon friends in this animated nursery rhyme about {clean_t}.\n\n⏱️ Chapters:\n00:00 - Welcome & Sing-Along\n00:15 - Happy Verse Dance\n00:30 - Chorus Together\n00:45 - Goodbye & Sweet Dreams\n\n#nurseryrhymes #kidssongs #toddlerlearning #preschool",
            "hashtags": [f"#{clean_t.replace(' ', '').lower()}", "#nurseryrhymes", "#kidssongs", "#toddlerlearning", "#preschool", "#toddlerfun"],
            "tags": f"{clean_t.lower()}, {clean_t.lower()} song, {clean_t.lower()} nursery rhyme, nursery rhymes, kids songs, toddler songs, preschool animation, learning for kids, baby cartoon 2026",
            "caption": f"Sing and dance along with {clean_t}! 🎈 Learn, smile, and explore with our cute 3D cartoon friends! #kidssongs #nurseryrhymes #preschool",
        }
    else:
        topic_match = re.search(r"about: '([^']+)'", user_prompt)
        topic = topic_match.group(1) if topic_match else "Happy Little Friends"
        clean_t = topic.strip().capitalize()
        content = {
            "title": f"The Joyful {clean_t} Song",
            "verses": [
                {
                    "section": "Verse 1",
                    "lines": [
                        f"Welcome to our sunny world, {clean_t} is here today,",
                        "Singing cheerful nursery songs as we dance and play!",
                        "Look at all our happy friends smiling in the sun,",
                        "Clap your hands and tap your feet, learning is so fun!",
                    ],
                    "character": f"Sunny {clean_t.split()[0]}",
                    "action": "bounces joyfully to the rhythm",
                },
                {
                    "section": "Chorus",
                    "lines": [
                        "Sing along together now, one and two and three,",
                        "Every little girl and boy, happy as can be!",
                        f"Love to sing about {clean_t} all the whole day through,",
                        "Smiling with our lovely friends and for me and you!",
                    ],
                    "character": f"Sunny {clean_t.split()[0]}",
                    "action": "twirls happily with sparkling stars",
                },
                {
                    "section": "Verse 2",
                    "lines": [
                        "Rainbow colors in the sky, floating soft and high,",
                        "Gentle little butterflies waving as they fly!",
                        "Jump as high as you can go, give a happy cheer,",
                        "Every single day is bright with companions here!",
                    ],
                    "character": "Rainbow Friend",
                    "action": "spins around waving hands",
                },
                {
                    "section": "Outro",
                    "lines": [
                        "Now it's time to wave goodbye, stars begin to gleam,",
                        "Have a happy restful night, have a gentle dream!",
                        f"Goodnight to our friendly {clean_t} song so sweet,",
                        "Tomorrow we will meet again to a joyful beat!",
                    ],
                    "character": "All Friends",
                    "action": "waves farewell under twilight stars",
                },
            ]
        }

    return {
        "id": "chatcmpl_ollama_local",
        "object": "chat.completion",
        "created": 1727092800,
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": json.dumps(content, indent=2) if isinstance(content, (dict, list)) else str(content)},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 340, "total_tokens": 460},
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11434, log_level="warning")
