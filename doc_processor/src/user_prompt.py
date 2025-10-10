"""Terminal user interaction for collecting context."""

from typing import Dict, List


class UserPrompt:
    """Handles interactive terminal questions to collect user context."""
    
    def __init__(self, questions: List[str]):
        """
        Initialize with list of questions.
        
        Args:
            questions: List of question strings
        """
        self.questions = questions
    
    def ask_questions(self) -> Dict[str, str]:
        """
        Present questions to user in terminal and collect answers.
        
        Returns:
            Dict mapping question index to answer
        """
        print("\n" + "="*60)
        print("📝 Additional Context Needed")
        print("="*60)
        print("(Press Enter to skip optional questions)\n")
        
        answers = {}
        total = len(self.questions)
        
        for i, question in enumerate(self.questions, 1):
            # Display question with progress
            print(f"Question {i}/{total}:")
            print(f"  {question}")
            
            # Get user input
            try:
                answer = input("> ").strip()
                
                # Store answer (even if empty)
                answers[f"question_{i}"] = {
                    "question": question,
                    "answer": answer if answer else "N/A"
                }
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Input interrupted. Skipping remaining questions.")
                break
            except Exception as e:
                print(f"⚠️  Error reading input: {e}")
                answers[f"question_{i}"] = {
                    "question": question,
                    "answer": "N/A"
                }
        
        print("="*60)
        print("✅ Context collection complete\n")
        
        return answers
    
    def format_for_json(self, answers: Dict) -> Dict[str, str]:
        """
        Format answers for JSON output structure.
        
        Args:
            answers: Raw answers dict from ask_questions()
            
        Returns:
            Cleaned dict for user_context section
        """
        formatted = {}
        
        for key, value in answers.items():
            # Create simple key from question
            question_text = value["question"]
            answer_text = value["answer"]
            
            # Use simplified key
            clean_key = question_text.split("?")[0].lower().replace(" ", "_")[:30]
            formatted[clean_key] = answer_text
        
        return formatted
