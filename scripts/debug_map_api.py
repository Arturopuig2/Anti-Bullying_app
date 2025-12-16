
import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.routers.dashboard import get_schools_geojson
import json

def check_api():
    db = SessionLocal()
    try:
        response = get_schools_geojson(db)
        # response is a JSONResponse, needs .body
        content = json.loads(response.body)
        
        print(f"Type: {content.get('type')}")
        features = content.get('features', [])
        print(f"Count: {len(features)}")
        if len(features) > 0:
            print("First Feature Properties:", features[0]['properties'])
            statuses = set(f['properties'].get('status') for f in features)
            print("Found Statuses:", statuses)
        else:
            print("No features found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_api()
