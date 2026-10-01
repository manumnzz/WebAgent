from validation.validator import validate_website


validation_result = validate_website()

print("\n--- VALIDATION TEST ---")
print(validation_result.model_dump_json(indent=2))