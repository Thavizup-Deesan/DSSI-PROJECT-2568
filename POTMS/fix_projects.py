"""
Script to fix project names in Firestore
Run this script once to update all projects that have invalid project_name field.

Usage: python fix_projects.py
"""

import os
import sys

# Add parent directory to path for Django settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from backend.firebase_config import db

def fix_project_names():
    """Update projects that have invalid project_name field"""
    print("Fetching projects from Firestore...")
    
    projects_ref = db.collection('projects')
    docs = list(projects_ref.stream())
    
    print(f"Found {len(docs)} projects\n")
    
    updated = 0
    for doc in docs:
        data = doc.to_dict()
        project_name = data.get('project_name', '')
        project_code = data.get('project_code', '')
        doc_id = doc.id
        
        print(f"ID: {doc_id}")
        print(f"  Current Name: '{project_name}'")
        print(f"  Current Code: '{project_code}'")
        
        # Check if project_name is missing, empty, or looks like an ID
        needs_update = False
        
        if not project_name:
            needs_update = True
            reason = "Empty name"
        elif project_name == doc_id:
            needs_update = True
            reason = "Name equals ID"
        elif len(project_name) > 15 and project_name.isalnum():
            # Looks like an auto-generated ID
            needs_update = True
            reason = "Name looks like an ID"
        
        if needs_update:
            # Generate a better name
            if project_code:
                new_name = f"โครงการ {project_code}"
            else:
                new_name = f"โครงการหมายเลข {doc_id[:8]}"
            
            print(f"  >>> Updating to: '{new_name}' (Reason: {reason})")
            doc.reference.update({'project_name': new_name})
            updated += 1
        else:
            print(f"  (OK - keeping current name)")
        
        print()
    
    print(f"Done! Updated {updated} projects.")

if __name__ == '__main__':
    fix_project_names()
