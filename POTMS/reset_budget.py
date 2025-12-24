import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
try:
    firebase_admin.get_app()
except:
    cred = credentials.Certificate('backend/firebase-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Reset budget_reserved for project
project_id = 'vLWPgJnn6KwwLzS0lUmQ'
db.collection('projects').document(project_id).update({
    'budget_reserved': 0
})

# Get updated budget info
project = db.collection('projects').document(project_id).get().to_dict()
print('=' * 50)
print('Reset budget_reserved to 0 successfully!')
print('=' * 50)
print(f"Budget Total: {project.get('budget_total', 0):,.2f}")
print(f"Budget Reserved: {project.get('budget_reserved', 0):,.2f}")
print(f"Budget Remaining: {project.get('budget_total', 0) - project.get('budget_reserved', 0) - project.get('budget_spent', 0):,.2f}")
print('=' * 50)
