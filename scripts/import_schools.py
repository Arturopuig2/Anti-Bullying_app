import pandas as pd
import sys
import os

# Add parent dir to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import School
from sqlalchemy.orm import Session

def import_schools():
    file_path = "c:/Users/Alvaro/Documents/GitHub/Anti-Bullyng_app/documents/valencia.xls"
    
    print(f"Reading file: {file_path}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    db = SessionLocal()
    
    # Ensure tables exist (quick fix for schema changes)
    Base.metadata.create_all(bind=engine)

    count_added = 0
    count_skipped = 0

    for index, row in df.iterrows():
        try:
            # Clean data (Use exact column names from check_columns.py)
            center_code = str(row['Codigo']).strip()
            raw_name = str(row['Denominacion']).strip()
            # Append code to make name unique (many schools share names like 'CEIP CERVANTES')
            name = f"{raw_name} ({center_code})"
            
            # Check existance
            existing = db.query(School).filter(School.center_code == center_code).first()
            if existing:
                # print(f"Skipping {center_code} - Already exists")
                count_skipped += 1
                continue

            # Construct Address
            tipo_via = str(row.get('Tipo_Via', '')).replace('nan', '')
            direccion = str(row.get('Direccion', '')).replace('nan', '')
            num = str(row.get('Num', '')).replace('nan', '')
            cp = str(row.get('Codigo_postal', '')).replace('nan', '')
            localidad = str(row.get('Localidad', '')).replace('nan', '')
            provincia = str(row.get('Provincia', '')).replace('nan', '')
            
            full_address = f"{tipo_via} {direccion} {num}, {cp} {localidad}, {provincia}".strip()
            
            # Coordinates (handle commas/dots)
            try:
                longitude = float(str(row['long']).replace(',', '.'))
            except:
                longitude = None
                
            try:
                latitude = float(str(row['lat']).replace(',', '.'))
            except:
                latitude = None

            phone = str(row.get('Telefono', '')).replace('nan', '')

            new_school = School(
                center_code=center_code,
                name=name,
                address=full_address,
                phone=phone,
                longitude=longitude,
                latitude=latitude,
                contact_email="" # No email in excel
            )
            
            db.add(new_school)
            count_added += 1
            
        except Exception as e:
            print(f"Error processing row {index}: {e}")

    try:
        db.commit()
        print(f"Import Complete. Added: {count_added}, Skipped: {count_skipped}")
    except Exception as e:
        db.rollback()
        print(f"Error committing to DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_schools()
