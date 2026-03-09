"""Backtranslation prompt templates"""

from jinja2 import Template


GENERATE_PROMPT = Template("""\
As an Operations Research Expert, considering the specified scenario.

Your task is to analyze the given mathematical optimization expression and LP data to generate a detailed natural language problem description specifically in the context of the following scenario:
{{scenario}}

IMPORTANT: The problem MUST be rewritten to fit the {{scenario}} context, even if the original data appears to be from a different domain.

Guidelines for Translation to {{scenario}} Domain:
* Reinterpret all variables and constraints to match {{scenario}} terminology
* Adapt relationships to make sense in the {{scenario}} context
* Ensure the problem structure maintains mathematical equivalence while using {{scenario}}-appropriate language

Follow these guidelines:
1. **Mathematical Analysis** (For your analysis only, do not include in output):
- Review decision variables, coefficients, and parameters
- Analyze objective function structure
- Examine constraints and their relationships

2. **Problem Description Generation**
Create a natural language description that:
- Incorporates all numerical values and coefficients naturally
- Includes all constraints and conditions logically
- Maintains mathematical accuracy while using natural language
- Avoids explicit mathematical formulations

---
Input Mathematical Expression:
{{mathematical_expression}}

---
Input LP Data:
{{lp_data}}

---
Reference Natural Language Optimization Problem Examples :
{%- for example in examples %}
Example {{loop.index}}:
- {{ example }}
{%- endfor %}

---
## Required Output:
Provide ONLY a clear, detailed natural language description of the optimization problem.
""")

CRITICIZE_PROMPT = Template("""\
As an Operations Research Expert, evaluate if the generated natural language description accurately matches the mathematical optimization problem defined in the LP data.

Input LP Data:
{{lp_data}}

Generated Problem Description:
{{problem_description}}

Required Output:
If the description perfectly matches the LP data:
Just output "Complete Instance", with no additional comments.

If there are any inconsistencies:
"Incomplete Instance:
[List specific discrepancies between LP data and description]"
""")

REFINEMENT_PROMPT = Template("""\
As an Operations Research Expert, analyze the criticism and refine the problem description if needed.

First, check the criticism result:
{{criticism}}

If the criticism shows "Complete Instance":
Output "Nothing need to refine" only without any additional text.

Otherwise, follow these steps to generate an improved description:

1. Review Input Materials:
Mathematical Expression:
{{mathematical_expression}}

LP Data:
{{lp_data}}

Initial Description:
{{initial_description}}

2. Task:
Based on the criticism feedback, LP data information, and initial description, generate a complete and accurate problem description.
""")


def get_prompts():
    """Return all prompt templates"""
    return {
        "generate": GENERATE_PROMPT,
        "criticize": CRITICIZE_PROMPT,
        "refinement": REFINEMENT_PROMPT,
    }
