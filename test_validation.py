"""
Test the validation logic locally
"""
import re
from datetime import datetime

def test_validation():
    # Test cases that might cause the error you're seeing
    test_cases = [
        {
            'recipient_name': '',  # Empty name
            'course_name': 'Python Course',
            'completion_date': '2024-10-04',
            'organization': 'Certificate Authority'
        },
        {
            'recipient_name': 'John Doe',
            'course_name': '',  # Empty course
            'completion_date': '2024-10-04', 
            'organization': 'Certificate Authority'
        },
        {
            'recipient_name': 'John Doe',
            'course_name': 'Python Course',
            'completion_date': '',  # Empty date
            'organization': 'Certificate Authority'
        },
        {
            'recipient_name': 'John@#$%',  # Invalid characters
            'course_name': 'Python Course',
            'completion_date': '2024-10-04',
            'organization': 'Certificate Authority'
        },
        {
            'recipient_name': 'John Doe',
            'course_name': 'Python Course',
            'completion_date': 'invalid-date',  # Invalid date format
            'organization': 'Certificate Authority'
        },
        {
            'recipient_name': 'John Doe',
            'course_name': 'Python Course',
            'completion_date': '2024-10-04',
            'organization': ''  # Empty organization (should get default)
        }
    ]
    
    for i, data in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Data: {data}")
        
        # Simulate the validation logic
        recipient_name = data.get('recipient_name', '').strip()
        event_name = data.get('course_name', '').strip()
        event_date = data.get('completion_date', '').strip()
        organization = data.get('organization', '').strip()
        
        # Set default organization if empty
        if not organization:
            organization = 'Certificate Authority'
            print(f"Set default organization: {organization}")
        
        # Validation - only require essential fields
        if not all([recipient_name, event_name, event_date]):
            missing_fields = []
            if not recipient_name: missing_fields.append('Recipient Name')
            if not event_name: missing_fields.append('Course Name')
            if not event_date: missing_fields.append('Completion Date')
            error_msg = f'Please fill in all required fields: {", ".join(missing_fields)}'
            print(f"❌ Validation Error: {error_msg}")
            continue
        
        # Validate date format
        try:
            datetime.strptime(event_date, '%Y-%m-%d')
            print("✅ Date format valid")
        except ValueError:
            error_msg = 'Invalid date format. Please use the date picker or ensure date is in YYYY-MM-DD format.'
            print(f"❌ Date Error: {error_msg}")
            continue
        
        # Basic name validation
        name_pattern = r"^[a-zA-Z\s'\-\.]+$"
        if not re.match(name_pattern, recipient_name):
            error_msg = 'Recipient name contains invalid characters. Please use only letters, spaces, apostrophes, hyphens, and periods.'
            print(f"❌ Name Error: {error_msg}")
            continue
        
        print("✅ All validations passed!")

if __name__ == "__main__":
    test_validation()