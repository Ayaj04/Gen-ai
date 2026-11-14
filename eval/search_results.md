# Day 07 - Semantic Search Results

Embedding model: all-MiniLM-L6-v2

Higher cosine similarity means closer vectors.
Similarity is not proof of factual relevance.

| Q | Rank | Document Title | Page | Score | Source |
|---|---|---|---|---|---|
| Q1 | 1 | Form Data | request-forms | 0.6499 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/request-forms.md) |
| Q1 | 2 | Tutorial - User Guide - FastAPI | tutorial | 0.6390 | [Source](https://fastapi.tiangolo.com/tutorial/) |
| Q1 | 3 | Tutorial - User Guide - FastAPI | tutorial | 0.5922 | [Source](https://fastapi.tiangolo.com/tutorial/) |
| Q2 | 1 | Tutorial - User Guide - FastAPI | tutorial | 0.7591 | [Source](https://fastapi.tiangolo.com/tutorial/) |
| Q2 | 2 | First Steps | first-steps | 0.7444 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/first-steps.md) |
| Q2 | 3 | First Steps | first-steps | 0.6825 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/first-steps.md) |
| Q3 | 1 | Response Status Code | response-status-code | 0.6671 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-status-code.md) |
| Q3 | 2 | Form Data | request-forms | 0.6571 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/request-forms.md) |
| Q3 | 3 | Query Parameters and String Validations | query-params-str-validations | 0.6304 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/query-params-str-validations.md) |
| Q4 | 1 | Path Parameters | path-params | 0.7260 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/path-params.md) |
| Q4 | 2 | Request Body | body | 0.6850 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/body.md) |
| Q4 | 3 | Path Parameters and Numeric Validations | path-params-numeric-validations | 0.6684 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/path-params-numeric-validations.md) |
| Q5 | 1 | Body - Nested Models | body-nested-models | 0.7011 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/body-nested-models.md) |
| Q5 | 2 | Request Body | body | 0.6752 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/body.md) |
| Q5 | 3 | Body - Nested Models | body-nested-models | 0.6610 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/body-nested-models.md) |
| Q6 | 1 | First Steps | first-steps | 0.4876 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/first-steps.md) |
| Q6 | 2 | First Steps | first-steps | 0.4510 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/first-steps.md) |
| Q6 | 3 | First Steps | first-steps | 0.4292 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/first-steps.md) |
| Q7 | 1 | Query Parameters and String Validations | query-params-str-validations | 0.7459 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/query-params-str-validations.md) |
| Q7 | 2 | Query Parameters and String Validations | query-params-str-validations | 0.7383 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/query-params-str-validations.md) |
| Q7 | 3 | Query Parameters and String Validations | query-params-str-validations | 0.7070 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/query-params-str-validations.md) |
| Q8 | 1 | Handling Errors | handling-errors | 0.5040 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/handling-errors.md) |
| Q8 | 2 | Handling Errors | handling-errors | 0.4560 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/handling-errors.md) |
| Q8 | 3 | Handling Errors | handling-errors | 0.4511 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/handling-errors.md) |
| Q9 | 1 | Response Status Code | response-status-code | 0.7557 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-status-code.md) |
| Q9 | 2 | Response Status Code | response-status-code | 0.7452 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-status-code.md) |
| Q9 | 3 | Response Status Code | response-status-code | 0.7177 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-status-code.md) |
| Q10 | 1 | Response Model - Return Type | response-model | 0.5954 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-model.md) |
| Q10 | 2 | Response Model - Return Type | response-model | 0.5641 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-model.md) |
| Q10 | 3 | Response Model - Return Type | response-model | 0.5420 | [Source](https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/response-model.md) |

## Manual Evaluation

Review whether the retrieved chunks actually answer
each question, not just whether they are similar.

### Q6 - Known Dataset Limitation

The current records do not cover the full AWS ECS,
Terraform and CI/CD deployment workflow.
Any returned chunks must be checked for relevance.

## Observations

- Best successful retrieval: [fill in]
- Weakest retrieval: [fill in]
- Irrelevant results: [fill in]
- Improvements needed: [fill in]