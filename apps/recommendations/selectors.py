# qubitgyanpro\apps\recommendations\selectors.py

from apps.recommendations.models import UserRecommendation


def get_user_recommendations(user):
    return UserRecommendation.objects.select_related("lesson").filter(user=user)[:5]