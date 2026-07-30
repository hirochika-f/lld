from models import RecommendationEvent


COOLDOWN_DAYS = 30


def is_in_cooldown(
    product_id: str,
    history: list[RecommendationEvent],
    current_day: int,
    cooldown_days: int = COOLDOWN_DAYS,
) -> bool:
    for event in history:
        age_days = current_day - event.day
        if age_days >= cooldown_days:
            break
        if event.product_id == product_id:
            return True
    return False
