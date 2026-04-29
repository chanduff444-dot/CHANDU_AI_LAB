import base64
import html
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import requests
import streamlit as st


OUTPUT_DIR = Path("tool_outputs") / "neocortex"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_SD_URL = "http://127.0.0.1:7860"


def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "concept"


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("The model did not return JSON.")
    return json.loads(match.group(0))


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [_as_text(item) for item in value]
        return " ".join(part for part in parts if part).strip()
    if isinstance(value, dict):
        parts = [_as_text(item) for item in value.values()]
        return " ".join(part for part in parts if part).strip()
    return str(value).strip()


def _normalize_packet(data: dict, concept: str, language: str) -> dict:
    fallback = _fallback_payload(concept, language)
    normalized = {}
    for key in ("explanation", "image_prompt", "narration"):
        normalized[key] = _as_text(data.get(key)) or fallback[key]
    normalized["language"] = _as_text(data.get("language")) or language
    return normalized


def _fallback_payload(concept: str, language: str) -> dict:
    return {
        "explanation": (
            f"{concept} is an important idea that can be understood step by step. "
            "First, identify the main parts involved in the concept. "
            "Next, notice how those parts interact with each other. "
            "Then, connect the process to a familiar real-world example. "
            "Finally, remember the core cause-and-effect relationship."
        ),
        "image_prompt": (
            f"clear educational illustration of {concept}, simple labeled diagram, "
            "student friendly, bright classroom poster style, accurate, 512x512"
        ),
        "narration": (
            f"Let's understand {concept} in a simple way. We will break it into parts, "
            "see how the parts work together, and connect it to something familiar."
        ),
        "language": language,
    }


def generate_learning_packet(concept: str, language: str, model: str, ollama_url: str) -> dict:
    prompt = f"""
You are Neocortex, an offline learning explainer for students aged 12 to 22.
Return only valid JSON with exactly these keys:
explanation, image_prompt, narration, language.

Rules:
- explanation must be exactly 5 clear sentences.
- image_prompt must describe one simple educational 512x512 illustration.
- narration must be warm, teacher-like, and easy to speak aloud.
- Use this language for explanation and narration: {language}.
- Keep terms accurate for science, math, history, or general knowledge.
- No markdown. No extra keys.

Concept:
{concept}
""".strip()

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You write compact, valid JSON for an offline educational app.",
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=90)
        response.raise_for_status()
        content = response.json()["message"]["content"]
        data = _extract_json(content)
    except Exception as exc:
        st.warning(f"Ollama structured output failed, using fallback text: {exc}")
        data = _fallback_payload(concept, language)

    return _normalize_packet(data, concept, language)


def generate_image_a1111(prompt: str, base_url: str, concept: str) -> str | None:
    _ensure_output_dir()
    endpoint = base_url.rstrip("/") + "/sdapi/v1/txt2img"
    payload = {
        "prompt": prompt,
        "negative_prompt": "blurry, dark, distorted text, watermark, low quality",
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "sampler_name": "Euler a",
        "batch_size": 1,
    }

    response = requests.post(endpoint, json=payload, timeout=180)
    response.raise_for_status()
    images = response.json().get("images", [])
    if not images:
        return None

    image_bytes = base64.b64decode(images[0].split(",", 1)[-1])
    image_path = OUTPUT_DIR / f"{_safe_slug(concept)}-{int(time.time())}.png"
    image_path.write_bytes(image_bytes)
    return str(image_path)


def generate_svg_concept_image(concept: str, image_prompt: str) -> str:
    _ensure_output_dir()
    lower = f"{concept} {image_prompt}".lower()
    title = html.escape(concept.strip().title() or "Concept")
    prompt_text = html.escape(image_prompt.strip())
    svg_path = OUTPUT_DIR / f"{_safe_slug(concept)}-{int(time.time())}.svg"

    if "cpu" in lower and "gpu" in lower:
        main_visual = """
        <rect x="58" y="168" width="132" height="118" rx="16" fill="#1a73e8"/>
        <text x="124" y="226" text-anchor="middle" class="nodeText">CPU</text>
        <rect x="322" y="168" width="132" height="118" rx="16" fill="#00897b"/>
        <text x="388" y="226" text-anchor="middle" class="nodeText">GPU</text>
        <rect x="204" y="214" width="104" height="26" rx="13" fill="#2b3445"/>
        <text x="256" y="233" text-anchor="middle" class="smallText">PCIe Bus</text>
        <path d="M190 205 C232 172 280 172 322 205" fill="none" stroke="#f29900" stroke-width="8" marker-end="url(#arrow)"/>
        <path d="M322 250 C280 284 232 284 190 250" fill="none" stroke="#7c4dff" stroke-width="8" marker-end="url(#arrowPurple)"/>
        <circle cx="236" cy="185" r="6" fill="#f29900"/>
        <circle cx="278" cy="270" r="6" fill="#7c4dff"/>
        """
    elif "photosynthesis" in lower:
        main_visual = """
        <circle cx="96" cy="96" r="42" fill="#f29900"/>
        <path d="M256 312 C250 250 252 210 256 168" stroke="#1e8e3e" stroke-width="14" fill="none"/>
        <ellipse cx="218" cy="196" rx="58" ry="28" fill="#00897b" transform="rotate(-24 218 196)"/>
        <ellipse cx="300" cy="196" rx="58" ry="28" fill="#00897b" transform="rotate(24 300 196)"/>
        <path d="M118 118 C156 148 188 164 220 176" stroke="#f29900" stroke-width="7" fill="none" marker-end="url(#arrow)"/>
        <text x="108" y="164" class="smallText">sunlight</text>
        <text x="318" y="172" class="smallText">oxygen</text>
        <text x="186" y="338" class="smallText">water + CO2</text>
        """
    else:
        main_visual = """
        <circle cx="256" cy="160" r="58" fill="#1a73e8"/>
        <text x="256" y="170" text-anchor="middle" class="nodeText">Idea</text>
        <rect x="72" y="292" width="110" height="72" rx="14" fill="#00897b"/>
        <rect x="201" y="292" width="110" height="72" rx="14" fill="#7c4dff"/>
        <rect x="330" y="292" width="110" height="72" rx="14" fill="#f29900"/>
        <path d="M226 204 L136 292" stroke="#5f6f86" stroke-width="6" marker-end="url(#arrowGray)"/>
        <path d="M256 220 L256 292" stroke="#5f6f86" stroke-width="6" marker-end="url(#arrowGray)"/>
        <path d="M286 204 L386 292" stroke="#5f6f86" stroke-width="6" marker-end="url(#arrowGray)"/>
        <text x="127" y="333" text-anchor="middle" class="smallText">Part 1</text>
        <text x="256" y="333" text-anchor="middle" class="smallText">Process</text>
        <text x="385" y="333" text-anchor="middle" class="smallText">Result</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L0,6 L9,3 z" fill="#f29900"/>
      </marker>
      <marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L0,6 L9,3 z" fill="#7c4dff"/>
      </marker>
      <marker id="arrowGray" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L0,6 L9,3 z" fill="#5f6f86"/>
      </marker>
      <style>
        .title {{ fill: #f8fbff; font: 700 25px Arial, sans-serif; }}
        .caption {{ fill: #aeb7c4; font: 400 14px Arial, sans-serif; }}
        .nodeText {{ fill: #ffffff; font: 700 25px Arial, sans-serif; }}
        .smallText {{ fill: #ffffff; font: 700 14px Arial, sans-serif; }}
      </style>
    </defs>
    <rect width="512" height="512" rx="24" fill="#0d0d0d"/>
    <rect x="24" y="24" width="464" height="464" rx="20" fill="#121820" stroke="#2a3442"/>
    <text x="40" y="64" class="title">{title}</text>
    {main_visual}
    <foreignObject x="40" y="398" width="432" height="70">
      <div xmlns="http://www.w3.org/1999/xhtml" style="color:#aeb7c4;font:14px Arial,sans-serif;line-height:1.35;">
        {prompt_text}
      </div>
    </foreignObject>
    </svg>"""

    svg_path.write_text(svg, encoding="utf-8")
    return str(svg_path)


def generate_audio_piper(narration: str, piper_exe: str, voice_model: str, concept: str) -> str | None:
    _ensure_output_dir()
    if not piper_exe.strip() or not voice_model.strip():
        return None

    audio_path = OUTPUT_DIR / f"{_safe_slug(concept)}-{int(time.time())}.wav"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as temp_file:
        temp_file.write(narration)
        input_path = temp_file.name

    try:
        result = subprocess.run(
            [piper_exe, "--model", voice_model, "--output_file", str(audio_path)],
            input=Path(input_path).read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "Piper failed.").strip())
        return str(audio_path)
    finally:
        try:
            os.remove(input_path)
        except OSError:
            pass


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?।])\s+", text.strip())
    return [sentence for sentence in sentences if sentence.strip()]


def render_synced_player(explanation: str, audio_path: str | None) -> None:
    sentences = _split_sentences(explanation)
    spans = []
    for index, sentence in enumerate(sentences):
        spans.append(
            f'<span class="neo-sentence" data-index="{index}">{html.escape(sentence)}</span>'
        )

    audio_markup = ""
    script = ""
    if audio_path and Path(audio_path).exists():
        audio_bytes = Path(audio_path).read_bytes()
        encoded = base64.b64encode(audio_bytes).decode("ascii")
        audio_markup = (
            f'<audio id="neoAudio" controls autoplay src="data:audio/wav;base64,{encoded}"></audio>'
        )
        script = """
<script>
const audio = document.getElementById("neoAudio");
const spans = Array.from(document.querySelectorAll(".neo-sentence"));
function updateHighlight() {
  if (!audio || !audio.duration || !spans.length) return;
  const index = Math.min(spans.length - 1, Math.floor((audio.currentTime / audio.duration) * spans.length));
  spans.forEach((span, i) => span.classList.toggle("active", i === index));
}
if (audio) {
  audio.addEventListener("timeupdate", updateHighlight);
  audio.addEventListener("play", updateHighlight);
}
</script>
"""

    st.components.v1.html(
        f"""
<style>
.neo-player {{
  border: 1px solid #2a2a2a;
  background: #111;
  border-radius: 8px;
  padding: 18px;
}}
.neo-text {{
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}}
.neo-sentence {{
  color: #9aa0a6;
  font: 15px/1.6 system-ui, -apple-system, Segoe UI, sans-serif;
  padding: 8px 10px;
  border-left: 3px solid transparent;
  background: #171717;
  border-radius: 6px;
}}
.neo-sentence.active {{
  color: #f8fbff;
  border-left-color: #1a73e8;
  background: #1a2433;
}}
audio {{
  width: 100%;
}}
</style>
<div class="neo-player">
  <div class="neo-text">{''.join(spans)}</div>
  {audio_markup}
</div>
{script}
""",
        height=360,
        scrolling=True,
    )


def export_offline_html(concept: str, packet: dict, image_path: str | None, audio_path: str | None) -> str:
    image_markup = ""
    if image_path and Path(image_path).exists():
        suffix = Path(image_path).suffix.lower()
        mime = "image/svg+xml" if suffix == ".svg" else "image/png"
        encoded_image = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        image_markup = f'<img src="data:{mime};base64,{encoded_image}" alt="Concept illustration">'

    audio_markup = ""
    if audio_path and Path(audio_path).exists():
        encoded_audio = base64.b64encode(Path(audio_path).read_bytes()).decode("ascii")
        audio_markup = f'<audio controls src="data:audio/wav;base64,{encoded_audio}"></audio>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Neocortex - {html.escape(concept)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #0d0d0d; color: #e8eaed; }}
    main {{ max-width: 920px; margin: 0 auto; }}
    h1 {{ color: #fff; }}
    .grid {{ display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 24px; align-items: start; }}
    img {{ width: 100%; border-radius: 8px; border: 1px solid #333; }}
    audio {{ width: 100%; margin-top: 20px; }}
    p {{ line-height: 1.7; color: #c7cbd1; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(concept)}</h1>
    <div class="grid">
      <section>
        <h2>Explanation</h2>
        <p>{html.escape(packet["explanation"])}</p>
        <h2>Narration</h2>
        <p>{html.escape(packet["narration"])}</p>
        {audio_markup}
      </section>
      <aside>{image_markup}</aside>
    </div>
  </main>
</body>
</html>"""


def show_neocortex_page(page_header, model_map: dict) -> None:
    page_header("NC", "Neocortex", "Offline multimodal concept explainer")

    st.markdown(
        "Build a synchronized learning packet from one concept: explanation, visual prompt, "
        "optional local image, and optional local narration."
    )

    available_models = list(dict.fromkeys(["mistral:latest", "llama3:latest", "qwen3:14b", *model_map.values()]))

    with st.sidebar:
        st.markdown("---")
        st.markdown("**Neocortex Engines**")
        llm_model = st.selectbox("Ollama model", available_models, index=0)
        language = st.selectbox("Language", ["English", "Tamil", "Hindi", "Telugu", "Kannada", "Malayalam"], index=0)
        image_engine = st.selectbox(
            "Image engine",
            ["Built-in SVG preview", "Automatic1111 API", "Text prompt only"],
            index=0,
        )
        sd_url = st.text_input("Stable Diffusion URL", value=DEFAULT_SD_URL)
        enable_audio = st.checkbox("Generate audio with Piper", value=False)
        piper_exe = st.text_input("Piper executable", value="piper")
        voice_model = st.text_input("Piper voice model path", value="")

    concept = st.text_area(
        "Concept",
        placeholder="Example: How does photosynthesis work?",
        height=96,
    )

    col_a, col_b = st.columns([1, 1])
    generate = col_a.button("Generate Neocortex packet", use_container_width=True)
    clear = col_b.button("Clear packet", use_container_width=True)

    if clear:
        st.session_state.pop("neocortex_packet", None)
        st.session_state.pop("neocortex_image_path", None)
        st.session_state.pop("neocortex_audio_path", None)

    if generate and concept.strip():
        with st.spinner("Generating explanation, visual prompt, and narration locally..."):
            packet = generate_learning_packet(concept.strip(), language, llm_model, DEFAULT_OLLAMA_URL)

        image_path = None
        if image_engine == "Built-in SVG preview":
            image_path = generate_svg_concept_image(concept.strip(), packet["image_prompt"])
        elif image_engine == "Automatic1111 API":
            with st.spinner("Generating local concept image..."):
                try:
                    image_path = generate_image_a1111(packet["image_prompt"], sd_url, concept)
                except Exception as exc:
                    st.warning(f"Image generation skipped: {exc}")
                    image_path = generate_svg_concept_image(concept.strip(), packet["image_prompt"])

        audio_path = None
        if enable_audio:
            with st.spinner("Generating local narration audio..."):
                try:
                    audio_path = generate_audio_piper(packet["narration"], piper_exe, voice_model, concept)
                except Exception as exc:
                    st.warning(f"Audio generation skipped: {exc}")

        st.session_state["neocortex_packet"] = packet
        st.session_state["neocortex_image_path"] = image_path
        st.session_state["neocortex_audio_path"] = audio_path
        st.session_state["neocortex_concept"] = concept.strip()

    packet = st.session_state.get("neocortex_packet")
    if not packet:
        st.info("Enter a topic and generate your first offline learning packet.")
        return

    concept_title = st.session_state.get("neocortex_concept", concept or "Concept")
    image_path = st.session_state.get("neocortex_image_path")
    audio_path = st.session_state.get("neocortex_audio_path")

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Explanation")
        render_synced_player(packet["explanation"], audio_path)

        st.subheader("Narration")
        st.write(packet["narration"])
        if audio_path and Path(audio_path).exists():
            st.audio(audio_path)

    with right:
        st.subheader("Concept Image")
        if image_path and Path(image_path).exists():
            st.image(image_path, use_container_width=True)
        else:
            st.code(packet["image_prompt"], language="text")
            st.caption("Select Built-in SVG preview for an immediate offline visual, or start Automatic1111 for AI image generation.")

    with st.expander("Structured JSON"):
        st.json(packet)

    html_export = export_offline_html(concept_title, packet, image_path, audio_path)
    st.download_button(
        "Export offline HTML summary",
        data=html_export,
        file_name=f"neocortex-{_safe_slug(concept_title)}-{uuid.uuid4().hex[:6]}.html",
        mime="text/html",
        use_container_width=True,
    )
