import os
import json
import time
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageEnhance

logger = logging.getLogger("studio.ai.image_provider")


class ImageGenerationProvider(ABC):
    """
    Abstract Base Class for AI Image Generation.
    Provides standard interfaces for Character Reference Images,
    Environment Reference Images, and YouTube Thumbnail Backgrounds.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_path: str,
        aspect_ratio: str = "16:9",
        image_size: str = "landscape_16_9",
    ) -> bool:
        """Generates a single image file at output_path."""
        pass

    @abstractmethod
    def generate_thumbnail_base(
        self,
        song_title: str,
        srt_theme: str,
        character_bible: Optional[Dict[str, Any]],
        environment_bible: Optional[Dict[str, Any]],
        output_path: str,
        main_action: str = "",
        visual_style: str = "3D Pixar Animation",
        aspect_ratio: str = "16:9",
    ) -> bool:
        """
        Generates an AI background and character image for YouTube Thumbnail.
        DOES NOT render title text inside the image so that the existing
        crisp 3D typography overlay can be safely applied.
        """
        pass

    @abstractmethod
    def generate_character_reference(
        self,
        character: Dict[str, Any],
        output_path: str,
        aspect_ratio: str = "1:1",
    ) -> bool:
        """Generates a character reference portrait for visual continuity."""
        pass


class ExistingImageProvider(ImageGenerationProvider):
    """
    Default local image provider using PIL procedural graphics and color harmony.
    100% offline, free, and instantaneous.
    """

    @property
    def name(self) -> str:
        return "existing_local"

    def generate_image(
        self,
        prompt: str,
        output_path: str,
        aspect_ratio: str = "16:9",
        image_size: str = "landscape_16_9",
    ) -> bool:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        width, height = (1280, 720) if aspect_ratio == "16:9" else (1080, 1920) if aspect_ratio == "9:16" else (1024, 1024)
        img = Image.new("RGB", (width, height), "#1E1B4B")
        draw = ImageDraw.Draw(img)

        # Procedural pleasant sunrise gradient
        for y in range(height):
            ratio = y / height
            r = int(255 * (1 - ratio * 0.4))
            g = int(140 * (1 - ratio * 0.3) + 70 * ratio)
            b = int(50 * (1 - ratio) + 220 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Decorative soft circles
        draw.ellipse([int(width * 0.7), int(height * 0.05), int(width * 0.98), int(height * 0.45)], fill="#FDE047", outline="#F59E0B", width=6)
        draw.ellipse([int(width * 0.05), int(height * 0.6), int(width * 0.45), int(height * 1.1)], fill="#10B981", outline="#059669", width=6)

        img.save(output_path, "JPEG", quality=92)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500

    def generate_thumbnail_base(
        self,
        song_title: str,
        srt_theme: str,
        character_bible: Optional[Dict[str, Any]],
        environment_bible: Optional[Dict[str, Any]],
        output_path: str,
        main_action: str = "",
        visual_style: str = "3D Pixar Animation",
        aspect_ratio: str = "16:9",
    ) -> bool:
        return self.generate_image(
            prompt=f"{song_title} {srt_theme}",
            output_path=output_path,
            aspect_ratio=aspect_ratio,
        )

    def generate_character_reference(
        self,
        character: Dict[str, Any],
        output_path: str,
        aspect_ratio: str = "1:1",
    ) -> bool:
        return self.generate_image(
            prompt=character.get("name", "Hero Character"),
            output_path=output_path,
            aspect_ratio=aspect_ratio,
        )


def _get_db_config(key: str) -> str:
    """Reads configuration key from studio.db studio_config table."""
    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).resolve().parent.parent / "projects" / "studio.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path), timeout=5)
            c = conn.cursor()
            c.execute("SELECT value FROM studio_config WHERE key = ?", (key,))
            row = c.fetchone()
            conn.close()
            if row and row[0]:
                val = row[0].strip()
                if "..." not in val and len(val) > 15:
                    return val
    except Exception:
        pass
    return ""


class NewAIImageProvider(ImageGenerationProvider):
    """
    Fal.ai Cloud AI Image Provider (fal-ai/flux/dev, fal-ai/recraft-v3, or fal-ai/flux-pro).
    Generates rich 3D character references and YouTube thumbnail backgrounds without text.
    Uses server-side FAL_KEY environment variable. Never exposes keys to client.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "fal-ai/flux/dev"):
        db_key = _get_db_config("FAL_KEY")
        resolved = (api_key or db_key or os.environ.get("FAL_KEY", "")).strip()
        # Ignore masked string placeholders like 'e080bf...b844'
        if "..." in resolved or len(resolved) < 15:
            resolved = ""
        self.api_key = resolved
        self.model = model or "fal-ai/flux/dev"
        self._fallback = ExistingImageProvider()

    @property
    def name(self) -> str:
        return "fal_ai"

    def _call_fal_image(self, prompt: str, aspect_ratio: str = "16:9") -> Optional[str]:
        if not self.api_key:
            logger.warning("FAL_KEY is not configured for NewAIImageProvider.")
            return None

        # Map aspect ratios to Fal supported image sizes
        image_size = "landscape_16_9"
        if aspect_ratio == "9:16":
            image_size = "portrait_16_9"
        elif aspect_ratio == "1:1":
            image_size = "square_hd"

        url = f"https://fal.run/{self.model}"
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MotionStoryLab/2.0",
        }
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 28,
            "guidance_scale": 4.5,
            "enable_safety_checker": True,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    images = data.get("images", [])
                    if images and len(images) > 0 and images[0].get("url"):
                        return images[0]["url"]
        except Exception as e:
            logger.warning(f"Fal AI image generation request failed: {e}")
            return None

        return None

    def generate_image(
        self,
        prompt: str,
        output_path: str,
        aspect_ratio: str = "16:9",
        image_size: str = "landscape_16_9",
    ) -> bool:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        img_url = self._call_fal_image(prompt, aspect_ratio=aspect_ratio)

        if img_url:
            try:
                urllib.request.urlretrieve(img_url, output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    logger.info(f"Successfully generated AI image via {self.model}: {output_path}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to download image from {img_url}: {e}")

        # Fallback to local provider on error
        logger.info("Falling back to ExistingImageProvider for image generation.")
        return self._fallback.generate_image(prompt, output_path, aspect_ratio)

    def generate_thumbnail_base(
        self,
        song_title: str,
        srt_theme: str,
        character_bible: Optional[Dict[str, Any]],
        environment_bible: Optional[Dict[str, Any]],
        output_path: str,
        main_action: str = "",
        visual_style: str = "3D Pixar Animation",
        aspect_ratio: str = "16:9",
    ) -> bool:
        """
        Builds detailed prompt according to Section 12:
        Song title + SRT theme + Character Bible + Environment Bible + Main action + Visual style.
        CRITICAL: Does NOT render text inside image to avoid spelling errors.
        """
        char = character_bible or {}
        char_name = char.get("name", "small cute light-brown teddy bear")
        char_app = char.get("appearance", "small cute light-brown teddy bear with soft fur, big warm expressive eyes, round ears")
        char_clothing = char.get("clothing", "cute blue pajamas with red bow")

        env = environment_bible or {}
        env_name = env.get("name", "cozy colorful children's bedroom")

        action = main_action or "looking cheerfully and surprised while exploring, high excitement"

        prompt = (
            f"Create a bright, colorful, high-quality 3D children's animation YouTube thumbnail background for a kids rhyme called '{song_title}'. "
            f"Subject: The same {char_name}, {char_app}, wearing the same {char_clothing}. "
            f"Action & Emotion: Character is {action}. "
            f"Environment: Inside a {env_name}, filled with playful animated props, toy details, and warm sunny golden lighting. "
            f"Visual Quality: {visual_style}, large expressive friendly eyes, clean composition, high contrast, vibrant saturated preschool colors, "
            f"16:9 cinematic widescreen composition, polished Unreal Engine 5 render, no text, no watermark, no words, no letters on image."
        )

        return self.generate_image(prompt, output_path, aspect_ratio=aspect_ratio)

    def generate_character_reference(
        self,
        character: Dict[str, Any],
        output_path: str,
        aspect_ratio: str = "1:1",
    ) -> bool:
        char_name = character.get("name", "Hero Character")
        appearance = character.get("appearance", "adorable animated 3D preschool character with joyful eyes")
        clothing = character.get("clothing", "vibrant colorful overalls")

        prompt = (
            f"Character reference turnaround portrait: {char_name}, {appearance}, wearing {clothing}. "
            f"3D Pixar CGI animation style, high detail character design, friendly warm smile, clean plain pastel background, "
            f"soft rim lighting, centered composition, high fidelity reference sheet, 8k render, no text."
        )

        return self.generate_image(prompt, output_path, aspect_ratio=aspect_ratio)


def get_image_provider(provider_type: Optional[str] = None) -> ImageGenerationProvider:
    """
    Factory function returning the active ImageGenerationProvider:
    - If USE_AI_THUMBNAIL=true or USE_AI_REFERENCE_IMAGES=true (or FAL_KEY is present and provider_type == 'ai'):
      Returns NewAIImageProvider
    - Otherwise:
      Returns ExistingImageProvider (100% offline, local, safe fallback)
    """
    if provider_type == "ai":
        return NewAIImageProvider()
    elif provider_type == "existing":
        return ExistingImageProvider()

    use_ai_thumb = os.environ.get("USE_AI_THUMBNAIL", "false").lower() in ("true", "1", "yes")
    use_ai_ref = os.environ.get("USE_AI_REFERENCE_IMAGES", "false").lower() in ("true", "1", "yes")
    fal_key = os.environ.get("FAL_KEY", "").strip()

    if (use_ai_thumb or use_ai_ref) and fal_key:
        return NewAIImageProvider(api_key=fal_key)

    return ExistingImageProvider()
