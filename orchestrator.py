from agents.research_agent import research_agent
from agents.insight_agent import insight_agent
from agents.copywriting_agent import copywriting_agent
from agents.judge_agent import judge_agent


def run_pipeline(product_name, category):
    THRESHOLD = 3.8

    print("Running research...")
    research = research_agent(product_name, category)

    print("Extracting insights...")
    insights = insight_agent({
        "summary": research["summary"],
        "category": category
    })

    print("Generating content...")
    content = copywriting_agent(insights, product_name)
    initial_content = content

    print("Evaluating content...")
    evaluation = judge_agent(content)

    # --- INITIAL SCORE ---
    score_data = evaluation.get("scores", {})
    scores = [v["score"] for v in score_data.values()] if score_data else []
    overall_score = sum(scores) / len(scores) if scores else 0
    initial_score = overall_score
    final_score = initial_score

    print(f"Initial Score: {round(overall_score, 2)}")

    # --- IMPROVEMENT LOOP ---
    if overall_score < THRESHOLD:
        feedback = evaluation.get("overall_feedback", "")

        # Skip useless improvement
        if not feedback or len(feedback.strip()) < 10:
            print("⚠️ Skipping improvement (weak or empty feedback)")
        else:
            print("⚠️ Low score detected. Improving content...")

            improved_content = copywriting_agent(
                insights=insights,
                user_input=product_name,
                feedback=feedback
            )

            improved_evaluation = judge_agent(improved_content)

            # --- RE-CALCULATE SCORE ---
            improved_scores = improved_evaluation.get("scores", {})
            improved_values = [v["score"] for v in improved_scores.values()] if improved_scores else []
            improved_overall = sum(improved_values) / len(improved_values) if improved_values else 0

            print(f"Improved Score: {round(improved_overall, 2)}")

            # --- ACCEPT ONLY IF BETTER ---
            if improved_overall > overall_score:
                final_score = improved_overall
                print("✅ Improvement accepted")
                content = improved_content
                evaluation = improved_evaluation
            else:
                print("❌ Improvement rejected (no real gain)")
        
    return {
    "research": research,
    "insights": insights,
    "initial_content": initial_content,
    "improved_content": content,
    "evaluation": evaluation,
    "initial_score": initial_score,
    "final_score": final_score
}