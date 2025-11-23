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
