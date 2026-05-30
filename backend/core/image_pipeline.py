"""
ChristianMind AI - Image Generation Pipeline
============================================
Uses Pollinations.ai for free image generation with LLM-powered prompt enhancement
for theological appropriateness.
"""

import random
import urllib.request
import urllib.parse
import base64
import re

from backend.core.client import call_llm


# Keywords that indicate inappropriate content
BLOCK_KEYWORDS = [
    "nude", "naked", "nsfw", "explicit", "violent", "gore",
    "blood", "weapon", "gun", "knife", "kill", "murder",
    "hate", "racist", "discrimination"
]


SYSTEM_PROMPT = """You are an expert at creating reverent, theologically appropriate image prompts for Christian art generation.

Your task is to transform user requests into detailed, beautiful art prompts suitable for AI image generation.

CRITICAL RULES:
- Output ONLY the image prompt text - nothing else
- Do NOT include any thinking, explanations, or prefix text
- Do NOT wrap the prompt in quotes
- Maximum 200 characters
- Include: main subject, artistic style, lighting, atmosphere
- Be specific about who and what is in the scene

Examples of GOOD outputs:
- "Jesus Christ with Virgin Mary, Renaissance oil painting, warm golden light, peaceful serene atmosphere, classical composition"
- "The Madonna and Child, soft divine light, Renaissance master style, tender maternal love"
- "Jesus teaching his disciples, biblical scene, warm light, peaceful Galilean landscape"""


def classify_image_request(user_prompt: str) -> dict:
    """
    Classify an image request for safety.
    """
    prompt_lower = user_prompt.lower()

    for keyword in BLOCK_KEYWORDS:
        if keyword in prompt_lower:
            return {
                "safe_to_generate": False,
                "reason": f"Inappropriate content: {keyword}"
            }

    return {"safe_to_generate": True, "reason": None}


def sanitize_image_prompt(user_prompt: str) -> str:
    """
    Use LLM to generate an appropriate, reverent image prompt.
    """
    # Extract the core request from user's input
    # Remove common prefixes like "generate image of", "create image of", etc.
    clean_request = re.sub(r'^(generate|create|make|show|produce|give)\s+(an?\s+)?(image|picture|photo)\s+(of\s+)?', '', user_prompt, flags=re.IGNORECASE)
    clean_request = clean_request.strip()

    prompt_message = f"""Create a Christian art prompt for: {clean_request}

Output ONLY the prompt text, nothing else. Max 200 characters."""

    try:
        generated_prompt = call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_message=prompt_message,
            max_tokens=250
        )

        # Clean up the response thoroughly
        result = generated_prompt.strip()

        # Remove any leading/trailing quotes
        result = result.strip('"\'')

        # Remove common unwanted prefixes
        prefixes_to_remove = [
            'prompt:', 'image prompt:', 'here is the prompt:', 'the prompt is:',
            'result:', 'output:', 'generated prompt:', 'art prompt:',
            'sure,', 'okay,', 'here\'s', 'here is', 'here you go:',
            'of course,', 'absolutely,'
        ]
        result_lower = result.lower()
        for prefix in prefixes_to_remove:
            if result_lower.startswith(prefix):
                result = result[len(prefix):].strip()
                result_lower = result.lower()

        # Remove any thinking/reasoning text at the start
        # Look for the first period followed by actual content
        match = re.search(r'\.\s+([A-Z].*)', result)
        if match:
            potential = match.group(1).strip()
            if len(potential) > 20:
                result = potential

        # Validate
        if result and len(result) > 15 and not result.lower().startswith(('sorry', 'i ', 'as an', 'i\'m')):
            # Make sure it has Christian/relevant content
            if any(word in result.lower() for word in ['jesus', 'christ', 'mary', 'god', 'bible', 'biblical', 'christian', 'angel', 'cross', 'holy', 'nativity', 'disciple']):
                return result

    except Exception as e:
        print(f"LLM prompt generation failed: {e}")

    # Smart fallback based on the request
    fallback_prompts = {
        'jesus': 'Jesus Christ, warm golden divine light, serene compassionate expression, Renaissance oil painting, peaceful atmosphere, classical religious art',
        'mary': 'Virgin Mary, soft blue and white tones, gentle divine light, Renaissance style, maternal grace, peaceful serene atmosphere',
        'cross': 'Jesus Christ on the cross, peaceful expression, warm golden light from heaven, Renaissance oil painting, reverent sacred art',
        'angel': 'Heavenly angel figure, soft white divine light, peaceful serene atmosphere, classical religious art style',
        'nativity': 'Nativity scene with baby Jesus, Mary and Joseph, warm golden light, shepherds and angels, Renaissance oil painting',
        'disciple': 'Jesus with his disciples, biblical scene, warm golden light, peaceful Galilean landscape, Renaissance composition',
        'bible': 'Open Bible with divine golden light, peaceful sacred atmosphere, classical still life painting',
        'prayer': 'Figure in prayer, peaceful worship, warm divine light, classical religious art style',
    }

    # Try to find relevant fallback
    request_lower = user_prompt.lower()
    for key, prompt in fallback_prompts.items():
        if key in request_lower:
            return prompt

    # Generic fallback
    return "reverent Christian sacred imagery, warm golden divine light, classical Renaissance oil painting style, peaceful serene atmosphere, spiritually uplifting, high quality detail"


def generate_christian_image(user_prompt: str) -> dict:
    """
    Generate a Christian-themed image with full safety pipeline.
    """
    # Step 1: Safety check
    classification = classify_image_request(user_prompt)

    if not classification.get("safe_to_generate", False):
        return {
            "success": False,
            "error": f"Image request blocked: {classification.get('reason')}",
            "image_url": None,
            "sanitized_prompt": None
        }

    # Step 2: LLM-powered prompt generation
    sanitized = sanitize_image_prompt(user_prompt)

    # Step 3: Generate via Pollinations and download synchronously
    encoded = urllib.parse.quote(sanitized)
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={seed}"

    try:
        req = urllib.request.Request(
            image_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            }
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            image_data = response.read()

        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        return {
            "success": True,
            "image_url": image_data_url,
            "sanitized_prompt": sanitized,
            "original_prompt": user_prompt,
            "note": "Generated with Pollinations.ai"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Image generation failed: {str(e)}",
            "image_url": None,
            "sanitized_prompt": sanitized
        }
