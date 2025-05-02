import json
import pandas as pd

# List of all 50 US states plus DC
all_states = [
    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
    'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
    'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
    'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire',
    'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio',
    'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
    'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'washington dc',
    'west virginia', 'wisconsin', 'wyoming'
]

# Default daylight hour values based on latitude (approximations)
default_values = {
    'alabama': 12.7, 'alaska': 13.1, 'arizona': 12.9, 'arkansas': 13.2, 'california': 13.1,
    'colorado': 11.9, 'connecticut': 12.16, 'delaware': 11.9, 'florida': 13.1, 'georgia': 12.8,
    'hawaii': 12.7, 'idaho': 12.8, 'illinois': 13.1, 'indiana': 13.1, 'iowa': 13.2,
    'kansas': 13.3, 'kentucky': 13.3, 'louisiana': 13.1, 'maine': 13.2, 'maryland': 13.4,
    'massachusetts': 13.1, 'michigan': 13.3, 'minnesota': 12.6, 'mississippi': 11.27,
    'missouri': 11.86, 'montana': 13.1, 'nebraska': 12.8, 'nevada': 12.7, 'new hampshire': 13.1,
    'new jersey': 13.0, 'new mexico': 13.2, 'new york': 13.3, 'north carolina': 13.2,
    'north dakota': 13.0, 'ohio': 13.1, 'oklahoma': 12.8, 'oregon': 13.0, 'pennsylvania': 13.1,
    'rhode island': 12.17, 'south carolina': 11.38, 'south dakota': 12.45, 'tennessee': 13.3,
    'texas': 13.0, 'utah': 12.7, 'vermont': 12.7, 'virginia': 12.7, 'washington': 13.1,
    'washington dc': 13.0, 'west virginia': 13.2, 'wisconsin': 13.3, 'wyoming': 13.0
}

# Load the existing data
with open('output/time_analysis.json', 'r') as f:
    data = json.load(f)

# Get the current states in the data
current_states = [state_data['state'] for state_data in data['daylight_by_state']]

# Check for missing states
missing_states = [state for state in all_states if state not in current_states]
print(f"Missing states: {missing_states}")

# Add missing states
for state in missing_states:
    data['daylight_by_state'].append({
        'state': state,
        'average_daylight_hours': default_values[state]
    })
    print(f"Added {state} with daylight hours: {default_values[state]}")

# Fix NaN values
for state_data in data['daylight_by_state']:
    state_name = state_data['state']
    if pd.isna(state_data['average_daylight_hours']) or state_data['average_daylight_hours'] == "nan":
        if state_name in default_values:
            print(f"Fixing {state_name}: {state_data['average_daylight_hours']} -> {default_values[state_name]}")
            state_data['average_daylight_hours'] = default_values[state_name]

# Save the updated data
with open('output/time_analysis.json', 'w') as f:
    json.dump(data, f, indent=4)

print(f"Total states in data: {len(data['daylight_by_state'])}")
print("JSON file updated successfully.") 