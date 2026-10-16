# Data dictionary

The included CSV has 1,000 fictional responses and a fixed default random seed
of 42. It covers January–March 2025. All records are illustrative and must not
be described as real survey results.

| Column | Type | Required | Meaning |
|---|---|---:|---|
| `Response_ID` | Text | Yes | Unique identifier assigned to a response |
| `Timestamp` | Date/time | No | Time the fictional response was recorded |
| `Age_Group` | Category | No | Broad, fictional age band |
| `Gender` | Category | No | Fictional response category; descriptive breakdown only |
| `Region` | Category | No | Fictional region label |
| `Question` | Text | Yes | Poll question associated with the selected option |
| `Selected_Option` | Text/category | Yes | Option selected for that question |
| `Satisfaction_Rating` | Integer, 1–5 | No | Optional satisfaction score; out-of-range/non-numeric values become missing |
| `Feedback` | Text | No | Optional fictional free-text comment |

For user-uploaded files, the three required columns must be present. Optional
columns can be omitted; the corresponding analyses are then not shown.
Percentages use valid responses to each question as their denominator.
