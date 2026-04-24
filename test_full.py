from orchestrator import run_pipeline

result = run_pipeline("running shoes", "sports shoes")

print("\n--- FINAL OUTPUT ---\n")

print("\nINSIGHTS:\n", result["insights"])
print("\nCONTENT:\n", result["content"])
print("\nEVALUATION:\n", result["evaluation"])