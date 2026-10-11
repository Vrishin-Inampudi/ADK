"""Snippet: using ADK ToolContext session state to drive a quiz.

Not a runnable agent yet - `quiz` is a placeholder list of (question, answer) pairs.
"""
from typing import Any, Dict

from google.adk.tools import ToolContext

quiz = [("What is 2 + 2?", "4")]


def start_quiz(tool_context: ToolContext) -> Dict[str, Any]:
    state = tool_context.state
    # Initialize quiz state
    state["quiz_started"] = True
    state["current_question_index"] = 0
    state["correct_answers"] = 0
    state["total_answered"] = 0
    state["score_percentage"] = 0
    if quiz:
        return {
            "status": "started",
            "first_question": quiz[0][0],
            "question_number": 1,
            "total_questions": len(quiz),
        }
    return {"status": "error", "error_message": "No questions available"}
