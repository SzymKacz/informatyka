import json
from pathlib import Path
from streamlit_lottie import st_lottie

def load_lottie(name: str):
    filepath = Path(__file__).parent.parent / "assets" / "lottie" / f"{name}.json"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def lottie_animation(name: str, height=200):
    animation = load_lottie(name)
    st_lottie(animation, height=height)