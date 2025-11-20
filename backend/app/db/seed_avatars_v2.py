"""
Seed Avatars Data - Simplified V2

This script populates the avatars table with 15 avatars:
- 3 default avatars (unlocked immediately on signup)
- 12 achievement-locked avatars

Usage:
    python -m app.db.seed_avatars_v2

Note: Run this AFTER seeding achievements (seed_achievements_v2.py)
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.gamification import Avatar, Achievement


def seed_avatars_v2(db: Session):
    """Create simplified 15-avatar system (3 default + 12 achievement-locked)"""

    # ========================================
    # STEP 1: Query all achievements by name
    # ========================================
    achievements = {
        achievement.name: achievement.id
        for achievement in db.query(Achievement).all()
    }

    if not achievements:
        print("❌ No achievements found in database!")
        print("   Please run: python -m app.db.seed_achievements_v2")
        return

    # ========================================
    # STEP 2: Define avatar data
    # ========================================
    avatars = [
        # ========================================
        # DEFAULT AVATARS (3)
        # Unlocked immediately on signup
        # ========================================
        Avatar(
            name="Default Student",
            description="The classic learner - always ready to study",
            image_url="/avatars/default_student.svg",
            required_achievement_id=None,  # DEFAULT (no achievement needed)
        ),
        Avatar(
            name="Tech Enthusiast",
            description="Passionate about technology and learning",
            image_url="/avatars/tech_enthusiast.svg",
            required_achievement_id=None,  # DEFAULT (no achievement needed)
        ),
        Avatar(
            name="Study Buddy",
            description="Your friendly companion on the learning journey",
            image_url="/avatars/study_buddy.svg",
            required_achievement_id=None,  # DEFAULT (no achievement needed)
        ),

        # ========================================
        # ACHIEVEMENT-LOCKED AVATARS (12)
        # Unlocked by earning specific achievements
        # ========================================

        # Tier 1 Avatars
        Avatar(
            name="Verified Scholar",
            description="A verified member of the learning community",
            image_url="/avatars/verified_scholar.svg",
            required_achievement_id=achievements.get("Welcome Aboard"),
        ),
        Avatar(
            name="Quiz Starter",
            description="You've taken your first steps into quiz mastery",
            image_url="/avatars/quiz_starter.svg",
            required_achievement_id=achievements.get("First Steps"),
        ),

        # Tier 2 Avatars
        Avatar(
            name="Perfect Student",
            description="Achieved perfection on a quiz",
            image_url="/avatars/perfect_student.svg",
            required_achievement_id=achievements.get("Perfect Score"),
        ),
        Avatar(
            name="Domain Specialist",
            description="Focused expertise in a specific exam domain",
            image_url="/avatars/domain_specialist.svg",
            required_achievement_id=achievements.get("Domain Focus"),
        ),
        Avatar(
            name="Veteran Learner",
            description="Experienced quiz-taker with proven consistency",
            image_url="/avatars/veteran_learner.svg",
            required_achievement_id=achievements.get("Quiz Veteran"),
        ),
        Avatar(
            name="Accuracy Expert",
            description="Master of high-score performances",
            image_url="/avatars/accuracy_expert.svg",
            required_achievement_id=achievements.get("Accuracy Pro"),
        ),

        # Tier 3 Avatars
        Avatar(
            name="Quiz Master",
            description="True mastery of the quiz platform",
            image_url="/avatars/quiz_master.svg",
            required_achievement_id=achievements.get("Quiz Master"),
        ),
        Avatar(
            name="Flawless Performer",
            description="Consistently perfect scores demonstrate excellence",
            image_url="/avatars/flawless_performer.svg",
            required_achievement_id=achievements.get("Perfectionist"),
        ),
        Avatar(
            name="Knowledge Sage",
            description="A vast repository of correctly answered questions",
            image_url="/avatars/knowledge_sage.svg",
            required_achievement_id=achievements.get("Knowledge Bank"),
        ),
        Avatar(
            name="Renaissance Scholar",
            description="Expertise across multiple domains",
            image_url="/avatars/renaissance_scholar.svg",
            required_achievement_id=achievements.get("Multi-Domain Expert"),
        ),

        # Tier 4 Avatars (Elite)
        Avatar(
            name="Century Champion",
            description="An elite member of the Century Club",
            image_url="/avatars/century_champion.svg",
            required_achievement_id=achievements.get("Century Club"),
        ),
        Avatar(
            name="Legendary Master",
            description="The ultimate achievement - true legend status",
            image_url="/avatars/legendary_master.svg",
            required_achievement_id=achievements.get("Quiz Legend"),
        ),
    ]

    # ========================================
    # STEP 3: Check for existing avatars
    # ========================================
    existing_count = db.query(Avatar).count()
    if existing_count > 0:
        print(f"⚠️  Avatars already exist ({existing_count} found).")
        print("⚠️  To use the new system, you'll need to:")
        print("    1. Backup your database")
        print("    2. Run a migration to clear old avatars")
        print("    3. Re-run this seed script")
        return

    # ========================================
    # STEP 4: Verify all achievements were found
    # ========================================
    missing_achievements = []
    for avatar in avatars:
        if avatar.required_achievement_id is not None and avatar.required_achievement_id not in achievements.values():
            missing_achievements.append(avatar.name)

    if missing_achievements:
        print(f"❌ Warning: Some achievements not found in database:")
        for name in missing_achievements:
            print(f"   - {name}")
        print("   Proceeding anyway, but these avatars may not unlock correctly.")

    # ========================================
    # STEP 5: Insert all avatars
    # ========================================
    db.add_all(avatars)
    db.commit()

    # ========================================
    # STEP 6: Report results
    # ========================================
    default_count = len([a for a in avatars if a.required_achievement_id is None])
    achievement_locked_count = len([a for a in avatars if a.required_achievement_id is not None])

    print(f"✅ Successfully seeded {len(avatars)} avatars!")
    print("\n📊 Avatar Breakdown:")
    print(f"  - Default (unlocked on signup):    {default_count} avatars")
    print(f"  - Achievement-locked:              {achievement_locked_count} avatars")
    print(f"\n🎯 Total: {len(avatars)} avatars")
    print("\n💡 Avatar Features:")
    print("  ✓ No rarity tiers")
    print("  ✓ Simple default vs. locked status")
    print("  ✓ One avatar per major achievement")
    print("  ✓ Default avatars unlock automatically on signup")


if __name__ == "__main__":
    """Run seed when executed as a script"""
    db = SessionLocal()
    try:
        seed_avatars_v2(db)
    except Exception as e:
        print(f"❌ Error seeding avatars: {e}")
        db.rollback()
    finally:
        db.close()
