# scripts/import_questions.py

import csv
import os
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.question import Question

# Path where your exam CSVs live
# Use relative path from backend/ directory
CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "questions")

# Map filenames → exam_type saved in DB
EXAMS = {
    "security.csv": "security",
    "network.csv": "network",
    "a1101.csv": "a1101",
    "a1102.csv": "a1102",
}

def import_csv_file(db: Session, filename: str, exam_type: str):
    path = os.path.join(CSV_DIR, filename)
    print(f"📥 Importing {filename} as exam_type={exam_type} ...")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")  # <-- CSV is comma-separated

        for row in reader:
            # Skip empty lines
            if not row or row["question-id"].strip() == "":
                continue

            # Build options JSON structure
            options = {
                "A": {
                    "text": row["option-a"].strip(),
                    "explanation": row["explanation-a"].strip(),
                },
                "B": {
                    "text": row["option-b"].strip(),
                    "explanation": row["explanation-b"].strip(),
                },
                "C": {
                    "text": row["option-c"].strip(),
                    "explanation": row["explanation-c"].strip(),
                },
                "D": {
                    "text": row["option-d"].strip(),
                    "explanation": row["explanation-d"].strip(),
                },
            }

            # Create SQLAlchemy model
            q = Question(
                question_id=row["question-id"].strip(),
                exam_type=exam_type,
                domain=row["domain"].strip(),
                question_text=row["question-text"].strip(),
                correct_answer=row["correct answer"].strip(),  # <-- SPACE IN HEADER
                options=options,
            )

            db.add(q)

    db.commit()
    print(f"✅ Finished importing {filename}.\n")


def main():
    db = SessionLocal()

    for filename, exam_type in EXAMS.items():
        import_csv_file(db, filename, exam_type)

    db.close()
    print("🎉 All CSV files imported successfully!")


if __name__ == "__main__":
    main()
