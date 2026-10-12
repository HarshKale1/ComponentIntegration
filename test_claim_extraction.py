
from services.llm_service import analyze_news

title = "Company reports a 20% increase in quarterly revenue"

content = """
Example Financial News reports that ABC Ltd revenue rose by 20%
in the latest quarter compared with the same quarter last year.
The company attributed the increase to higher product sales.
Management expects revenue growth to continue next quarter.
"""

result = analyze_news(title=title, content=content)

print("Event:", result.event)
print("Claims:")
for claim in result.claims:
    print("-", claim)
