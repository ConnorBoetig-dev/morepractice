#!/usr/bin/env python3
"""
Comprehensive test fixer script
Fixes all model field names and API contracts to match actual implementation
"""

import re
import sys

def fix_quiz_tests(content):
    """Fix quiz test model fields"""
    # Fix QuizAttempt model fields
    content = re.sub(r'score=(\d+)', r'correct_answers=\1, score_percentage=(\1/total_questions*100)', content)
    content = re.sub(r'time_taken=(\d+)', r'time_taken_seconds=\1', content)
    
    # Fix quiz submission requests
    content = content.replace('"time_taken":', '"time_taken_seconds":')
    content = content.replace('{"question_id":', '{"question_id":')
    content = content.replace('"selected_answer":', '"user_answer":')
    
    # Add required fields for quiz submission
    content = re.sub(
        r'"exam_type": "(\w+)",\s+"answers": \[(.*?)\],',
        r'"exam_type": "\1", "total_questions": len(questions), "answers": [\2],',
        content,
        flags=re.DOTALL
    )
    
    return content

def fix_question_tests(content):
    """Fix question test model fields - use JSON options"""
    # Replace option_a, option_b, etc with options JSON
    pattern = r'option_a="([^"]+)",\s+option_b="([^"]+)",\s+option_c="([^"]+)",\s+option_d="([^"]+)",'
    
    def replace_options(match):
        a, b, c, d = match.groups()
        return f'''options={{
                "A": {{"text": "{a}", "explanation": "Option A"}},
                "B": {{"text": "{b}", "explanation": "Option B"}},
                "C": {{"text": "{c}", "explanation": "Option C"}},
                "D": {{"text": "{d}", "explanation": "Option D"}}
            }},'''
    
    content = re.sub(pattern, replace_options, content)
    
    # Remove difficulty and explanation fields that don't exist
    content = re.sub(r',\s+difficulty="[^"]*"', '', content)
    content = re.sub(r',\s+explanation="[^"]*"', '', content)
    
    return content

print("Test fixer created. Apply manually to each test file.")
print("Key fixes needed:")
print("1. Quiz: time_taken -> time_taken_seconds, score -> score_percentage")
print("2. Question: option_a/b/c/d -> options JSON")
print("3. Admin: Check endpoint paths and methods")
