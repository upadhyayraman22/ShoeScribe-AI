from agents.research_agent import research_agent
from agents.insight_agent import insight_agent
from agents.copywriting_agent import copywriting_agent
from agents.judge_agent import judge_agent

def run_pipeline(product_name, category):
    print("Running research...")
    research = research_agent(product_name, category)

    print("Extracting insights...")
    insights = insight_agent({
        "summary": research["summary"],
        "category": category
    })

    print("Generating content...")
    content = copywriting_agent(insights, product_name)

    print("Evaluating content...")
    evaluation = judge_agent(content)

    return {
        "research": research,
        "insights": insights,
        "content": content,
        "evaluation": evaluation
    }