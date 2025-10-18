from datetime import datetime, timedelta

# --- Helper Function for Standard Badge Creation ---
def create_badge(name, icon, current, target):
    """Creates a standardized badge dictionary with safe progress formatting."""
    achieved = current >= target
    target = max(target, 1)  # avoid division by zero
    progress = f"{min(current, target)}/{target}"
    percentage = min(int((min(current, target) / target) * 100), 100)
    return {
        'name': name,
        'icon': icon,
        'progress': progress,
        'percentage': percentage,
        'achieved': achieved
    }

# --- Helper Function for Streak Calculation ---
def calculate_streak_badge(user):
    if not user.thoughts:
        return None

    unique_dates = sorted({t.timestamp.date() for t in user.thoughts}, reverse=True)
    streak_days = 0
    last_date = datetime.utcnow().date() + timedelta(days=1)

    for current_date in unique_dates:
        diff = (last_date - current_date).days
        if diff == 1:
            streak_days += 1
            last_date = current_date
        elif diff == 0:
            last_date = current_date
        else:
            break

    today = datetime.utcnow().date()
    if unique_dates and (today - unique_dates[0]).days > 1:
        return None  # streak broken

    STREAK_TARGET = 7
    if streak_days >= 3:
        return create_badge("Soul Architect", "🔥", streak_days, STREAK_TARGET)
    return None

# --- Main Milestone Calculator Function ---
def get_milestones(user):
    """Returns all actual earned/earned-progress badges for the user."""
    badges = []
    all_thoughts = user.thoughts
    current_posts = len(all_thoughts)
    current_likes = user.total_likes_received()

    # 1. Consistent Contributor (Post Count)
    POST_TARGET = 10
    badges.append(create_badge("Consistent Contributor", "📝", current_posts, POST_TARGET))

    # 2. Beloved Listener (Likes Received)
    LIKES_TARGET = 20
    badges.append(create_badge("Beloved Listener", "❤️", current_likes, LIKES_TARGET))

    # 3. First Feather (Long posts)
    FEATHER_TARGET = 1
    long_posts = sum(1 for thought in all_thoughts if len(thought.content or "") >= 100)
    badges.append(create_badge("First Feather", "🕊️", long_posts, FEATHER_TARGET))

    # 4. Mood Master (Diversity of moods)
    MOOD_TARGET = 6
    moods_posted = {thought.mood for thought in all_thoughts if thought.mood}
    badges.append(create_badge("Mood Master", "🎭", len(moods_posted), MOOD_TARGET))

    # 5. Soul Architect (Streak)
    streak_badge = calculate_streak_badge(user)
    if streak_badge:
        badges.append(streak_badge)

    # 6. Connector (Posts with high engagement)
    CONNECTOR_TARGET = 5
    ENGAGEMENT_THRESHOLD = 5
    connector_count = sum(1 for thought in all_thoughts if thought.liked_by.count() >= ENGAGEMENT_THRESHOLD)
    badges.append(create_badge("Connector", "🌐", connector_count, CONNECTOR_TARGET))

    # 7. Soul Whisperer (Highly liked thoughts)
    WHISPERER_TARGET = 15
    highly_liked = [t for t in all_thoughts if t.liked_by.count() >= 3]
    badges.append(create_badge("Soul Whisperer", "✨", len(highly_liked), WHISPERER_TARGET))

    # 8. Badge Hunter (counts only actual milestones above)
    HUNTER_TARGET = 5
    actual_achieved = sum(1 for badge in badges if badge['achieved'])
    badges.append(create_badge("Badge Hunter", "🏆", actual_achieved, HUNTER_TARGET))

    return badges
