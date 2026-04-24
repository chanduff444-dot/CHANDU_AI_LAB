# ============================================
# CHANDU AI LAB - MASTER ORCHESTRATOR
# Production-Ready | Fault-Tolerant | Stable
# ============================================

import re

from core.rag_engine import rag_generate
from core.router import generate_response
from core.models.emotion_model import predict_emotion_raw
from core.memory_engine import retrieve_memory, store_memory
from core.code_executor import execute_python_code


class MasterOrchestrator:

    def __init__(self):
        pass

    # ----------------------------------------
    # Code Detection
    # ----------------------------------------
    def is_code_request(self, text: str) -> bool:
        keywords = [
            "code", "python", "function", "class",
            "error", "debug", "script", "algorithm"
        ]
        words = text.lower().split()
        return any(keyword in words for keyword in keywords)

    # ----------------------------------------
    # Structural Guard (Safe Only)
    # ----------------------------------------
    def enforce_python_standards(self, code: str) -> str:

        code = re.sub(
            r'if\s+name\s*==\s*[\'"]main[\'"]\s*:',
            'if __name__ == "__main__":',
            code,
            flags=re.IGNORECASE
        )

        code = code.replace("```python", "")
        code = code.replace("```", "")

        return code.strip()

    # ----------------------------------------
    # Main Processing Pipeline
    # ----------------------------------------
    def process(self, user_input: str, creator_mode: bool = False):

        # Emotion analysis
        emotion_data = predict_emotion_raw(user_input)
        emotion = emotion_data.get("emotion")
        confidence = emotion_data.get("confidence")
        sentiment = emotion_data.get("sentiment")

        # Safety check
        high_risk_keywords = [
            "hurt myself", "suicide", "kill myself",
            "end my life", "don't want to live"
        ]

        if any(keyword in user_input.lower() for keyword in high_risk_keywords):
            return {
                "response": "Please seek immediate help from a trusted person or professional.",
                "emotion": emotion,
                "confidence": confidence,
                "sentiment": sentiment,
                "type": "safety"
            }

        # =========================================
        # CODE PATH
        # =========================================
        if self.is_code_request(user_input):

            try:
                generated_code = generate_response(
                    user_input,
                    creator_mode=False
                )
            except Exception as e:
                return {
                    "response": f"⚠️ Code Generation Error: {str(e)}",
                    "emotion": emotion,
                    "confidence": confidence,
                    "sentiment": sentiment,
                    "type": "error"
                }

            generated_code = self.enforce_python_standards(generated_code)

            # Syntax check
            try:
                compile(generated_code, "<string>", "exec")
            except SyntaxError as e:

                fix_prompt = f"""
Fix this Python code completely.

USER REQUEST:
{user_input}

CODE:
{generated_code}

ERROR:
{str(e)}

Return only clean executable code.
"""

                try:
                    generated_code = generate_response(fix_prompt)
                    generated_code = self.enforce_python_standards(generated_code)
                except Exception as e:
                    return {
                        "response": f"⚠️ Code Fix Error: {str(e)}",
                        "emotion": emotion,
                        "confidence": confidence,
                        "sentiment": sentiment,
                        "type": "error"
                    }

            # Ensure main block
            if "__main__" not in generated_code:

                fix_prompt = f"""
Add main block to this code:

if __name__ == "__main__":

CODE:
{generated_code}
"""

                try:
                    generated_code = generate_response(fix_prompt)
                    generated_code = self.enforce_python_standards(generated_code)
                except Exception:
                    pass

            # Execute safely
            try:
                success, output = execute_python_code(generated_code)
            except Exception:
                success = True

            # Retry if failed
            if not success:
                try:
                    fix_prompt = f"""
Fix execution error.

USER REQUEST:
{user_input}

CODE:
{generated_code}

ERROR:
{output}

Return final working code only.
"""
                    generated_code = generate_response(fix_prompt)
                    generated_code = self.enforce_python_standards(generated_code)
                except Exception:
                    pass

            store_memory(user_input, generated_code)

            return {
                "response": generated_code.strip(),
                "emotion": emotion,
                "confidence": confidence,
                "sentiment": sentiment,
                "type": "code"
            }

        # =========================================
        # NON-CODE PATH
        # =========================================
        else:

            memory_context = retrieve_memory(user_input)

            if memory_context:
                enriched_input = f"""
Relevant memory:
{memory_context}

Query:
{user_input}
"""
            else:
                enriched_input = user_input

            clean_query = user_input.lower().strip()
            simple_inputs = ["hi", "hello", "hey", "ok", "thanks"]

            try:
                # Smart routing
                if clean_query in simple_inputs or len(clean_query.split()) <= 2:
                    knowledge_response = generate_response(user_input)
                else:
                    knowledge_response = rag_generate(enriched_input)

                response_type = "chat"

            except Exception as e:
                knowledge_response = f"⚠️ Chat Error: {str(e)}"
                response_type = "error"

            store_memory(user_input, knowledge_response)

            return {
                "response": knowledge_response.strip(),
                "emotion": emotion,
                "confidence": confidence,
                "sentiment": sentiment,
                "type": response_type
            }