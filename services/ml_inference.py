# qubitgyanpro\services\ml_inference.py

from services.ml_model import load_model
from services.ml_features import build_features


def score_lessons(user, lessons):
    model, scaler = load_model()

    if not model or not scaler:
        return [(lesson, 0.5) for lesson in lessons]

    scored = []

    for lesson in lessons:
        features = build_features(user, lesson)
        features_scaled = scaler.transform([features])

        prob = model.predict_proba(features_scaled)[0][1]
        scored.append((lesson, prob))

    return sorted(scored, key=lambda x: x[1], reverse=True)

