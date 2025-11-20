"""
Seed Achievements Data

This script populates the achievements table with initial achievements.
Run this once after creating the gamification tables.

Usage:
    python -m app.db.seed_achievements
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.gamification import Achievement


def seed_achievements(db: Session):
    """Create initial achievements for the gamification system"""

    achievements = [
        # ========================================
        # ACCOUNT SETUP ACHIEVEMENTS
        # ========================================
        Achievement(
            name="Welcome Aboard!",
            description="Verify your email address",
            icon="✉️",
            badge_icon_url="/badges/email_verified.svg",
            criteria_type="email_verified",
            criteria_value=1,
            xp_reward=25,
            unlocks_avatar_id=None,
            rarity="common",
            display_order=0,
            is_hidden=False
        ),

        # ========================================
        # GETTING STARTED ACHIEVEMENTS
        # ========================================
        Achievement(
            name="First Steps",
            description="Complete your first quiz",
            badge_icon_url="/badges/first_steps.svg",
            criteria_type="quiz_completed",
            criteria_value=1,
            xp_reward=50,
            unlocks_avatar_id=None,  # Will be set later when avatars are created
            display_order=1,
            is_hidden=False
        ),
        Achievement(
            name="Beginner",
            description="Complete 5 quizzes",
            badge_icon_url="/badges/beginner.svg",
            criteria_type="quiz_completed",
            criteria_value=5,
            xp_reward=100,
            unlocks_avatar_id=None,
            display_order=2,
            is_hidden=False
        ),
        Achievement(
            name="Quick Learner",
            description="Complete 10 quizzes",
            badge_icon_url="/badges/quick_learner.svg",
            criteria_type="quiz_completed",
            criteria_value=10,
            xp_reward=200,
            unlocks_avatar_id=None,
            display_order=3,
            is_hidden=False
        ),

        # ========================================
        # ACCURACY ACHIEVEMENTS
        # ========================================
        Achievement(
            name="Perfect Score",
            description="Get 100% on any quiz",
            badge_icon_url="/badges/perfect_score.svg",
            criteria_type="perfect_quiz",
            criteria_value=1,
            xp_reward=150,
            unlocks_avatar_id=None,
            display_order=10,
            is_hidden=False
        ),
        Achievement(
            name="Perfectionist",
            description="Get 100% on 5 quizzes",
            badge_icon_url="/badges/perfectionist.svg",
            criteria_type="perfect_quiz",
            criteria_value=5,
            xp_reward=500,
            unlocks_avatar_id=None,
            display_order=11,
            is_hidden=False
        ),
        Achievement(
            name="Flawless",
            description="Get 100% on 10 quizzes",
            badge_icon_url="/badges/flawless.svg",
            criteria_type="perfect_quiz",
            criteria_value=10,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=12,
            is_hidden=True  # Hidden until earned
        ),
        Achievement(
            name="Sharp Shooter",
            description="Score 90% or higher on 10 quizzes",
            badge_icon_url="/badges/sharp_shooter.svg",
            criteria_type="high_score_quiz",
            criteria_value=10,
            xp_reward=750,
            unlocks_avatar_id=None,
            display_order=13,
            is_hidden=False
        ),

        # ========================================
        # QUESTION MILESTONE ACHIEVEMENTS
        # ========================================
        Achievement(
            name="Question Rookie",
            description="Answer 100 questions correctly",
            badge_icon_url="/badges/question_rookie.svg",
            criteria_type="correct_answers",
            criteria_value=100,
            xp_reward=200,
            unlocks_avatar_id=None,
            display_order=20,
            is_hidden=False
        ),
        Achievement(
            name="Question Master",
            description="Answer 500 questions correctly",
            badge_icon_url="/badges/question_master.svg",
            criteria_type="correct_answers",
            criteria_value=500,
            xp_reward=750,
            unlocks_avatar_id=None,
            display_order=21,
            is_hidden=False
        ),
        Achievement(
            name="Quiz Veteran",
            description="Answer 1000 questions correctly",
            badge_icon_url="/badges/quiz_veteran.svg",
            criteria_type="correct_answers",
            criteria_value=1000,
            xp_reward=1500,
            unlocks_avatar_id=None,
            display_order=22,
            is_hidden=False
        ),
        Achievement(
            name="Quiz Legend",
            description="Answer 2500 questions correctly",
            badge_icon_url="/badges/quiz_legend.svg",
            criteria_type="correct_answers",
            criteria_value=2500,
            xp_reward=3000,
            unlocks_avatar_id=None,
            display_order=23,
            is_hidden=True  # Hidden until earned
        ),

        # ========================================
        # STREAK ACHIEVEMENTS
        # ========================================
        Achievement(
            name="Getting Started",
            description="Maintain a 3-day study streak",
            badge_icon_url="/badges/getting_started.svg",
            criteria_type="study_streak",
            criteria_value=3,
            xp_reward=150,
            unlocks_avatar_id=None,
            display_order=30,
            is_hidden=False
        ),
        Achievement(
            name="Week Warrior",
            description="Maintain a 7-day study streak",
            badge_icon_url="/badges/week_warrior.svg",
            criteria_type="study_streak",
            criteria_value=7,
            xp_reward=400,
            unlocks_avatar_id=None,
            display_order=31,
            is_hidden=False
        ),
        Achievement(
            name="Dedicated Student",
            description="Maintain a 14-day study streak",
            badge_icon_url="/badges/dedicated_student.svg",
            criteria_type="study_streak",
            criteria_value=14,
            xp_reward=800,
            unlocks_avatar_id=None,
            display_order=32,
            is_hidden=False
        ),
        Achievement(
            name="Month Master",
            description="Maintain a 30-day study streak",
            badge_icon_url="/badges/month_master.svg",
            criteria_type="study_streak",
            criteria_value=30,
            xp_reward=2000,
            unlocks_avatar_id=None,
            display_order=33,
            is_hidden=True  # Hidden until earned
        ),

        # ========================================
        # EXAM-SPECIFIC ACHIEVEMENTS (A+ Core 1)
        # ========================================
        Achievement(
            name="A+ Core 1 Beginner",
            description="Complete 10 A+ Core 1 quizzes",
            badge_icon_url="/badges/aplus_core1_beginner.svg",
            criteria_type="exam_specific",
            criteria_value=10,  # exam_type stored in extra metadata
            xp_reward=300,
            unlocks_avatar_id=None,
            display_order=40,
            is_hidden=False
        ),
        Achievement(
            name="A+ Core 1 Expert",
            description="Complete 50 A+ Core 1 quizzes",
            badge_icon_url="/badges/aplus_core1_expert.svg",
            criteria_type="exam_specific",
            criteria_value=50,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=41,
            is_hidden=False
        ),

        # ========================================
        # EXAM-SPECIFIC ACHIEVEMENTS (A+ Core 2)
        # ========================================
        Achievement(
            name="A+ Core 2 Beginner",
            description="Complete 10 A+ Core 2 quizzes",
            badge_icon_url="/badges/aplus_core2_beginner.svg",
            criteria_type="exam_specific",
            criteria_value=10,
            xp_reward=300,
            unlocks_avatar_id=None,
            display_order=50,
            is_hidden=False
        ),
        Achievement(
            name="A+ Core 2 Expert",
            description="Complete 50 A+ Core 2 quizzes",
            badge_icon_url="/badges/aplus_core2_expert.svg",
            criteria_type="exam_specific",
            criteria_value=50,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=51,
            is_hidden=False
        ),

        # ========================================
        # EXAM-SPECIFIC ACHIEVEMENTS (Network+)
        # ========================================
        Achievement(
            name="Network+ Beginner",
            description="Complete 10 Network+ quizzes",
            badge_icon_url="/badges/network_beginner.svg",
            criteria_type="exam_specific",
            criteria_value=10,
            xp_reward=300,
            unlocks_avatar_id=None,
            display_order=60,
            is_hidden=False
        ),
        Achievement(
            name="Network+ Pro",
            description="Complete 50 Network+ quizzes",
            badge_icon_url="/badges/network_pro.svg",
            criteria_type="exam_specific",
            criteria_value=50,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=61,
            is_hidden=False
        ),

        # ========================================
        # EXAM-SPECIFIC ACHIEVEMENTS (Security+)
        # ========================================
        Achievement(
            name="Security+ Beginner",
            description="Complete 10 Security+ quizzes",
            badge_icon_url="/badges/security_beginner.svg",
            criteria_type="exam_specific",
            criteria_value=10,
            xp_reward=300,
            unlocks_avatar_id=None,
            display_order=70,
            is_hidden=False
        ),
        Achievement(
            name="Security+ Specialist",
            description="Complete 50 Security+ quizzes",
            badge_icon_url="/badges/security_specialist.svg",
            criteria_type="exam_specific",
            criteria_value=50,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=71,
            is_hidden=False
        ),

        # ========================================
        # LEVEL ACHIEVEMENTS
        # ========================================
        Achievement(
            name="Level 5",
            description="Reach Level 5",
            badge_icon_url="/badges/level_5.svg",
            criteria_type="level_reached",
            criteria_value=5,
            xp_reward=250,
            unlocks_avatar_id=None,
            display_order=80,
            is_hidden=False
        ),
        Achievement(
            name="Level 10",
            description="Reach Level 10",
            badge_icon_url="/badges/level_10.svg",
            criteria_type="level_reached",
            criteria_value=10,
            xp_reward=500,
            unlocks_avatar_id=None,
            display_order=81,
            is_hidden=False
        ),
        Achievement(
            name="Level 20",
            description="Reach Level 20",
            badge_icon_url="/badges/level_20.svg",
            criteria_type="level_reached",
            criteria_value=20,
            xp_reward=1000,
            unlocks_avatar_id=None,
            display_order=82,
            is_hidden=True  # Hidden until earned
        ),
        Achievement(
            name="Level 50",
            description="Reach Level 50",
            badge_icon_url="/badges/level_50.svg",
            criteria_type="level_reached",
            criteria_value=50,
            xp_reward=5000,
            unlocks_avatar_id=None,
            display_order=83,
            is_hidden=True  # Hidden until earned
        ),
    ]

    # Check if achievements already exist
    existing_count = db.query(Achievement).count()
    if existing_count > 0:
        print(f"⚠️  Achievements already exist ({existing_count} found). Skipping seed.")
        return

    # Insert all achievements
    db.add_all(achievements)
    db.commit()

    print(f"✅ Successfully seeded {len(achievements)} achievements!")
    print("\nAchievement Categories:")
    print(f"  - Account Setup: 1 achievement")
    print(f"  - Getting Started: 3 achievements")
    print(f"  - Accuracy: 4 achievements")
    print(f"  - Question Milestones: 4 achievements")
    print(f"  - Study Streaks: 4 achievements")
    print(f"  - A+ Core 1: 2 achievements")
    print(f"  - A+ Core 2: 2 achievements")
    print(f"  - Network+: 2 achievements")
    print(f"  - Security+: 2 achievements")
    print(f"  - Levels: 4 achievements")
    print(f"\nTotal: {len(achievements)} achievements")


if __name__ == "__main__":
    """Run seed when executed as a script"""
    db = SessionLocal()
    try:
        seed_achievements(db)
    except Exception as e:
        print(f"❌ Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()
