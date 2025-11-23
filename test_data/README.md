# Test Data Files

## housing_data.csv
Sample dataset for predicting house prices based on:
- **age**: Age of the buyer
- **salary**: Annual salary
- **rooms**: Number of rooms
- **price**: House price (target variable)

### Example usage:
- **Model name**: `linear`
- **Features**: `["age", "salary", "rooms"]`
- **Label**: `price`

### Test prediction:
```json
{
  "age": 35,
  "salary": 70000,
  "rooms": 3
}
```

---

## salary_prediction.csv
Sample dataset for predicting salary based on:
- **years_experience**: Years of work experience
- **education_level**: Education level (1=High School, 2=Bachelor, 3=Master, 4=PhD)
- **age**: Age of the person
- **salary**: Annual salary (target variable)

### Example usage:
- **Model name**: `salary_model`
- **Features**: `["years_experience", "education_level", "age"]`
- **Label**: `salary`

### Test prediction:
```json
{
  "years_experience": 8,
  "education_level": 3,
  "age": 30
}
```

---

## customer_churn.csv
Sample dataset for predicting customer churn (classification) based on:
- **age**: Customer age
- **income**: Annual income
- **months_subscribed**: Duration of subscription in months
- **support_calls**: Number of support calls made
- **satisfaction_score**: Customer satisfaction score (1-5)
- **churn**: Whether customer churned (0=No, 1=Yes) - target variable

### Example usage:
- **Model name**: `churn_model`
- **Model type**: `logistic_regression` or `random_forest_classifier`
- **Features**: `["age", "income", "months_subscribed", "support_calls", "satisfaction_score"]`
- **Label**: `churn`

### Test prediction:
```json
{
  "age": 30,
  "income": 55000,
  "months_subscribed": 12,
  "support_calls": 3,
  "satisfaction_score": 3.5
}
```
