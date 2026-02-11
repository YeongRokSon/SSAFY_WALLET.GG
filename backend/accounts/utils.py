# accounts/utils.py
import random

def make_nick():
    adjectives = ["부유한", "똑똑한", "배고픈", "성실한", "행복한", "즐거운", "대박난"]
    nouns = ["개미", "워렌버핏", "지갑", "금고", "투자자", "나무", "저금통"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}"