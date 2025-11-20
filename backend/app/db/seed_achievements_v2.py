"""
Seed Achievements Data - Simplified V2

This script populates the achievements table with 15 carefully designed achievements
organized into 4 progression tiers.

Usage:
    python -m app.db.seed_achievements_v2
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.gamification import Achievement


def seed_achievements_v2(db: Session):
    """Create simplified 15-achievement system organized into 4 tiers"""

    achievements = [
        # ========================================
        # TIER 1: GETTING STARTED (4 achievements)
        # Easy wins to get users engaged
        # ========================================
        Achievement(
            name="Welcome Aboard",
            description="Verify your email address",
            icon="✉️",
            criteria_type="email_verified",
            criteria_value=1,
            xp_reward=50,
        ),
        Achievement(
            name="First Steps",
            description="Complete your first quiz",
            icon="🎯",
            criteria_type="quiz_completed",
            criteria_value=1,
            xp_reward=100,
        ),
        Achievement(
            name="Building Momentum",
            description="Complete 3 quizzes in any domain",
            icon="🚀",
            criteria_type="quiz_completed",
            criteria_value=3,
            xp_reward=200,
        ),
        Achievement(
            name="Quiz Regular",
            description="Complete 5 quizzes",
            icon="📚",
            criteria_type="quiz_completed",
            criteria_value=5,
            xp_reward=300,
        ),

        # ========================================
        # TIER 2: COMPETENCE (5 achievements)
        # Showing skill and consistency
        # ========================================
        Achievement(
            name="Perfect Score",
            description="Get 100% on any quiz",
            icon="💯",
            criteria_type="perfect_quiz",
            criteria_value=1,
            xp_reward=500,
        ),
        Achievement(
            name="Domain Focus",
            description="Complete 10 quizzes in one specific exam type",
            icon="🎓",
            criteria_type="exam_specific",
            criteria_value=10,
            criteria_exam_type=None,  # Will match any exam type with 10+ quizzes
            xp_reward=600,
        ),
        Achievement(
            name="Quiz Veteran",
            description="Complete 25 total quizzes",
            icon="⭐",
            criteria_type="quiz_completed",
            criteria_value=25,
            xp_reward=800,
        ),
        Achievement(
            name="Accuracy Pro",
            description="Get 90% or higher on 5 different quizzes",
            icon="🎯",
            criteria_type="high_score_quiz",
            criteria_value=5,
            xp_reward=700,
        ),
        Achievement(
            name="Correct Streak",
            description="Answer 100 questions correctly over your lifetime",
            icon="✅",
            criteria_type="correct_answers",
            criteria_value=100,
            xp_reward=400,
        ),

        # ========================================
        # TIER 3: MASTERY (4 achievements)
        # Deep commitment and expertise
        # ========================================
        Achievement(
            name="Quiz Master",
            description="Complete 50 total quizzes",
            icon="👑",
            criteria_type="quiz_completed",
            criteria_value=50,
            xp_reward=1500,
        ),
        Achievement(
            name="Perfectionist",
            description="Get 100% on 5 different quizzes",
            icon="💎",
            criteria_type="perfect_quiz",
            criteria_value=5,
            xp_reward=1200,
        ),
        Achievement(
            name="Knowledge Bank",
            description="Answer 500 questions correctly over your lifetime",
            icon="🧠",
            criteria_type="correct_answers",
            criteria_value=500,
            xp_reward=1000,
        ),
        Achievement(
            name="Multi-Domain Expert",
            description="Complete 10 quizzes in at least 2 different exam types",
            icon="🌐",
            criteria_type="multi_domain",  # New criteria type
            criteria_value=10,  # 10 quizzes minimum per domain
            xp_reward=1500,
        ),

        # ========================================
        # TIER 4: ELITE (2 achievements)
        # Ultimate endgame goals
        # ========================================
        Achievement(
            name="Century Club",
            description="Complete 100 total quizzes",
            icon="💪",
            criteria_type="quiz_completed",
            criteria_value=100,
            xp_reward=3000,
        ),
        Achievement(
            name="Quiz Legend",
            description="Reach Level 50",
            icon="🏆",
            criteria_type="level_reached",
            criteria_value=50,
            xp_reward=5000,
        ),
    ]

    # Check if achievements already exist (avoid duplicates)
    existing_count = db.query(Achievement).count()
    if existing_count > 0:
        print(f"⚠️  Achievements already exist ({existing_count} found).")
        print("⚠️  To use the new system, you'll need to:")
        print("    1. Backup your database")
        print("    2. Run a migration to clear old achievements")
        print("    3. Re-run this seed script")
        return

    # Insert all achievements
    db.add_all(achievements)
    db.commit()

    print(f"✅ Successfully seeded {len(achievements)} achievements!")
    print("\n📊 Achievement Breakdown by Tier:")
    print("  - Tier 1 (Getting Started):  4 achievements")
    print("  - Tier 2 (Competence):       5 achievements")
    print("  - Tier 3 (Mastery):          4 achievements")
    print("  - Tier 4 (Elite):            2 achievements")
    print(f"\n🎯 Total: {len(achievements)} achievements")
    print("\n💡 Achievement Features:")
    print("  ✓ No rarity tiers")
    print("  ✓ No hidden achievements")
    print("  ✓ Natural progression curve")
    print("  ✓ Clear tier-based difficulty")


if __name__ == "__main__":
    """Run seed when executed as a script"""
    db = SessionLocal()
    try:
        seed_achievements_v2(db)
    except Exception as e:
        print(f"❌ Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()
