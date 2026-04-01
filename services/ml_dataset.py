# qubitgyanpro\services\ml_dataset.py

import numpy as np

from apps.analytics.models import UserLessonInteraction
from services.ml_features import build_features


def build_training_dataset():
    interactions = UserLessonInteraction.objects.select_related("lesson", "user")

    X, y = [], []

    for i in interactions:
        features = build_features(i.user, i.lesson)
        X.append(features)
        y.append(int(i.completed))

    if not X:
        return None

    return np.array(X), np.array(y)