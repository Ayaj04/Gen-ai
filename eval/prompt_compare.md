
# Day 06 - Prompt Comparison

## Objective

Compare two FastAPIGuide task prompts using the same
10 user questions from Day 05.

## Setup

- Provider: Groq
- Model: openai/gpt-oss-20b
- System prompt: prompts/system.txt
- Prompt V1: prompts/task_v1.txt
- Prompt V2: prompts/task_v2.txt
- Dataset: data/records.json

## Evaluation Criteria

1. Accuracy: Is the information supported by the documentation?
2. Clarity: Can a beginner understand the answer?
3. Code: Is the example relevant and runnable?
4. Source: Is the official documentation referenced?
5. Honesty: Does the model admit missing information?

Rating: Pass / Partial / Fail

## Results

| Question | V1 Rating | V2 Rating | Better Version |
|---|---|---|---|
| Q1 - What is FastAPI? | Not tested | Not tested | TBD |
| Q2 - Create an API | Not tested | Not tested | TBD |
| Q3 - Requests and responses | Not tested | Not tested | TBD |
| Q4 - Path parameters | Not tested | Not tested | TBD |
| Q5 - Pydantic validation | Not tested | Not tested | TBD |
| Q6 - AWS ECS deployment | Not tested | Not tested | TBD |
| Q7 - Query validation | Not tested | Not tested | TBD |
| Q8 - Return HTTP 404 | Not tested | Not tested | TBD |
| Q9 - Response status codes | Not tested | Not tested | TBD |
| Q10 - Response models | Not tested | Not tested | TBD |

## Important Test: Q6

Q6 asks about AWS ECS deployment using Terraform and CI/CD.

This topic is outside the current FastAPIGuide dataset.

V1 observation:
[Write what the model actually returned]

V2 observation:
[Write what the model actually returned]

Which response handled the limitation better?
[Your observation]

## Example Comparison

Question:
[Select a question]

V1 Answer:
[Paste or summarize the actual response]

V2 Answer:
[Paste or summarize the actual response]

Analysis:
[Explain which response is clearer, more accurate,
and better supported by official documentation]

## Conclusion

V1 strengths:
[Fill after testing]

V2 strengths:
[Fill after testing]

Which prompt performed better overall?
[Your conclusion supported by the results]
