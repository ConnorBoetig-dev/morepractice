"""
Seed Avatars Data

This script populates the avatars table with initial avatars.
Run this AFTER seeding achievements if you want to link avatars to achievements.

Usage:
    python -m app.db.seed_avatars
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.gamification import Avatar, Achievement


def seed_avatars(db: Session):
    """Create initial avatars for the gamification system"""

    # First, get achievement IDs for linking (if achievements exist)
    # This allows us to unlock avatars as rewards for specific achievements
    achievement_map = {}
    achievements = db.query(Achievement).all()
    for ach in achievements:
        achievement_map[ach.name] = ach.id

    avatars = [
        # ========================================
        # DEFAULT AVATARS (Available to Everyone)
        # ========================================
        Avatar(
            name="Default Student",
            description="The starting avatar for all new students",
            image_url="/avatars/default_student.png",
            is_default=True,
            required_achievement_id=None,
            rarity="common",
            display_order=1
        ),
        Avatar(
            name="Tech Enthusiast",
            description="A tech-savvy learner ready to conquer CompTIA exams",
            image_url="/avatars/tech_enthusiast.png",
            is_default=True,
            required_achievement_id=None,
            rarity="common",
            display_order=2
        ),
        Avatar(
            name="Study Buddy",
            description="Your friendly study companion",
            image_url="/avatars/study_buddy.png",
            is_default=True,
            required_achievement_id=None,
            rarity="common",
            display_order=3
        ),

        # ========================================
        # ACHIEVEMENT-LOCKED AVATARS (Rare)
        # ========================================
        Avatar(
            name="Quiz Champion",
            description="Awarded for completing your first quiz",
            image_url="/avatars/quiz_champion.png",
            is_default=False,
            required_achievement_id=achievement_map.get("First Steps"),
            rarity="rare",
            display_order=10
        ),
        Avatar(
            name="Perfect Scholar",
            description="Awarded for achieving a perfect score",
            image_url="/avatars/perfect_scholar.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Perfect Score"),
            rarity="rare",
            display_order=11
        ),
        Avatar(
            name="Dedicated Learner",
            description="Awarded for maintaining a 7-day study streak",
            image_url="/avatars/dedicated_learner.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Week Warrior"),
            rarity="rare",
            display_order=12
        ),

        # ========================================
        # HIGH-TIER AVATARS (Epic)
        # ========================================
        Avatar(
            name="Accuracy Expert",
            description="Awarded for consistently high scores",
            image_url="/avatars/accuracy_expert.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Sharp Shooter"),
            rarity="epic",
            display_order=20
        ),
        Avatar(
            name="Knowledge Seeker",
            description="Awarded for answering 500 questions correctly",
            image_url="/avatars/knowledge_seeker.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Question Master"),
            rarity="epic",
            display_order=21
        ),
        Avatar(
            name="Streak Master",
            description="Awarded for maintaining a 14-day study streak",
            image_url="/avatars/streak_master.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Dedicated Student"),
            rarity="epic",
            display_order=22
        ),

        # ========================================
        # LEGENDARY AVATARS (Legendary)
        # ========================================
        Avatar(
            name="CompTIA Prodigy",
            description="Awarded for achieving Level 20",
            image_url="/avatars/comptia_prodigy.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Level 20"),
            rarity="legendary",
            display_order=30
        ),
        Avatar(
            name="Perfectionist Elite",
            description="Awarded for 10 perfect scores",
            image_url="/avatars/perfectionist_elite.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Flawless"),
            rarity="legendary",
            display_order=31
        ),
        Avatar(
            name="Quiz Legend",
            description="Awarded for answering 2500 questions correctly",
            image_url="/avatars/quiz_legend.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Quiz Legend"),
            rarity="legendary",
            display_order=32
        ),
        Avatar(
            name="Month Champion",
            description="Awarded for maintaining a 30-day study streak",
            image_url="/avatars/month_champion.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Month Master"),
            rarity="legendary",
            display_order=33
        ),

        # ========================================
        # EXAM-SPECIFIC AVATARS
        # ========================================
        Avatar(
            name="A+ Core 1 Master",
            description="Awarded for completing 50 A+ Core 1 quizzes",
            image_url="/avatars/aplus_core1_master.png",
            is_default=False,
            required_achievement_id=achievement_map.get("A+ Core 1 Expert"),
            rarity="epic",
            display_order=40
        ),
        Avatar(
            name="A+ Core 2 Master",
            description="Awarded for completing 50 A+ Core 2 quizzes",
            image_url="/avatars/aplus_core2_master.png",
            is_default=False,
            required_achievement_id=achievement_map.get("A+ Core 2 Expert"),
            rarity="epic",
            display_order=41
        ),
        Avatar(
            name="Network Ninja",
            description="Awarded for completing 50 Network+ quizzes",
            image_url="/avatars/network_ninja.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Network+ Pro"),
            rarity="epic",
            display_order=42
        ),
        Avatar(
            name="Security Sentinel",
            description="Awarded for completing 50 Security+ quizzes",
            image_url="/avatars/security_sentinel.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Security+ Specialist"),
            rarity="epic",
            display_order=43
        ),

        # ========================================
        # ULTIMATE AVATAR
        # ========================================
        Avatar(
            name="CompTIA Grandmaster",
            description="Awarded for reaching Level 50 - the ultimate achievement",
            image_url="/avatars/comptia_grandmaster.png",
            is_default=False,
            required_achievement_id=achievement_map.get("Level 50"),
            rarity="legendary",
            display_order=99
        ),
    ]

    # Check if avatars already exist
    existing_count = db.query(Avatar).count()
    if existing_count > 0:
        print(f"⚠️  Avatars already exist ({existing_count} found). Skipping seed.")
        return

    # Insert all avatars
    db.add_all(avatars)
    db.commit()

    print(f"✅ Successfully seeded {len(avatars)} avatars!")
    print("\nAvatar Categories:")
    print(f"  - Default (Common): 3 avatars")
    print(f"  - Achievement-Locked (Rare): 3 avatars")
    print(f"  - High-Tier (Epic): 7 avatars")
    print(f"  - Legendary: 5 avatars")
    print(f"\nTotal: {len(avatars)} avatars")
    print("\nRarity Distribution:")
    print(f"  - Common: 3")
    print(f"  - Rare: 3")
    print(f"  - Epic: 7")
    print(f"  - Legendary: 5")


if __name__ == "__main__":
    """Run seed when executed as a script"""
    db = SessionLocal()
    try:
        seed_avatars(db)
    except Exception as e:
        print(f"❌ Error seeding avatars: {e}")
        db.rollback()
    finally:
        db.close()
