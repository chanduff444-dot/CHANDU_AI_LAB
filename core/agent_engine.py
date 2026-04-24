# ============================================
# 🤖 Agent Engine (Chandu AI Lab)
# ============================================

from core.router import generate_response


class AgentEngine:

    def __init__(self, orchestrator, model="deepseek-coder:6.7b"):
        self.orchestrator = orchestrator
        self.model = model

    # ----------------------------------------
    # 🧠 MAIN AGENT LOOP
    # ----------------------------------------
    def run(self, user_input, max_steps=3, retries=1):

        steps = []
        current_input = user_input
        final_output = ""

        for step in range(1, max_steps + 1):

            # -----------------------------
            # Step Type
            # -----------------------------
            if step == 1:
                step_type = "plan"
                prompt = f"""
Understand the task and plan solution.

Task:
{current_input}

Explain briefly what you will build.
"""
            else:
                step_type = "build"
                prompt = f"""
You are an expert frontend developer.

STRICT RULES:
- Output ONLY a complete HTML file
- No explanation
- No markdown
- Must start with <!DOCTYPE html>
- Must include CSS + JavaScript
- Must be interactive

TASK:
{current_input}
"""

            # -----------------------------
            # Generate Response
            # -----------------------------
            try:
                # 🧹 Clean prompt (VERY IMPORTANT)
                clean_prompt = " ".join(prompt.split())

                print("\n=== DEBUG ===")
                print("MODEL:", self.model)
                print("PROMPT LENGTH:", len(clean_prompt))
                print("=============\n")

                output = generate_response(clean_prompt, model=self.model)

                # 🧹 Clean markdown
                output = output.replace("```html", "").replace("```", "").strip()

            except Exception as e:
                output = f"Error: {str(e)}"

            # -----------------------------
            # Log Step
            # -----------------------------
            steps.append({
                "step": step,
                "type": step_type,
                "input": prompt.strip(),
                "output": output.strip()
            })

            # -----------------------------
            # Check if HTML built
            # -----------------------------
            if "<html>" in output.lower():
                final_output = output
                break

            # -----------------------------
            # Improve input
            # -----------------------------
            current_input = f"""
Improve and complete this:

{output}

Original task:
{user_input}
"""

        # ----------------------------------------
        # 🔁 Retry Logic
        # ----------------------------------------
        if "<html>" not in final_output.lower() and retries > 0:

            retry_prompt = f"""
Build a COMPLETE working HTML app.

STRICT:
- Only HTML
- No explanation
- Must be functional

Task:
{user_input}
"""

            try:
                # 🧹 Clean retry prompt
                clean_retry = " ".join(retry_prompt.split())

                final_output = generate_response(clean_retry, model=self.model)

                # 🧹 Clean markdown
                final_output = final_output.replace("```html", "").replace("```", "").strip()

            except Exception as e:
                final_output = f"Error: {str(e)}"

            steps.append({
                "step": "retry",
                "type": "retry",
                "input": retry_prompt.strip(),
                "output": final_output.strip()
            })

        return {
            "final": final_output,
            "steps": steps
        }