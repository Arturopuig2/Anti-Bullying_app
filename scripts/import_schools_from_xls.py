
import sys
import os
import pandas as pd
import math

sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models import School

def import_data():
    file_path = os.path.join("documents", "valencia.xls")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Reading {file_path}...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    session = SessionLocal()
    
    count_new = 0
    count_updated = 0
    
    print(f"Processing {len(df)} rows...")
    
    for index, row in df.iterrows():
        try:
            code = str(row.get('Codigo', '')).strip()
            # If code matches the format, use it. Some might be floats like 4600123.0
            if code.endswith('.0'):
                code = code[:-2]
                
            if not code or code.lower() == 'nan':
                continue

            name = str(row.get('Denominacion', '')).strip()
            
            # Construct address
            via = str(row.get('Tipo_Via', '')).strip()
            direccion = str(row.get('Direccion', '')).strip()
            num = str(row.get('Num', '')).strip()
            cp = str(row.get('Codigo_postal', '')).strip()
            loc = str(row.get('Localidad', '')).strip()
            
            # Handle float conversions for strings
            if num.endswith('.0'): num = num[:-2]
            if cp.endswith('.0'): cp = cp[:-2]
            
            if via == 'nan': via = ''
            if num == 'nan': num = ''
            
            address = f"{via} {direccion} {num}, {cp} {loc}".strip().replace("  ", " ")
            
            phone_raw = row.get('Telefono', '')
            phone = None
            if isinstance(phone_raw, (int, float)) and not math.isnan(phone_raw):
                phone = str(int(phone_raw))
            elif isinstance(phone_raw, str):
                phone = phone_raw

            lat = row.get('lat')
            lon = row.get('long') # based on inspection
            
            if lat and math.isnan(lat): lat = None
            if lon and math.isnan(lon): lon = None

            # Upsert
            school = session.query(School).filter(School.center_code == code).first()
            if not school:
                school = School(center_code=code)
                session.add(school)
                count_new += 1
            else:
                count_updated += 1
            
            school.name = name
            school.address = address
            school.phone = phone
            # Only update coords if valid
            if lat is not None: school.latitude = float(lat)
            if lon is not None: school.longitude = float(lon)
            
            # Default email if not present
            if not school.contact_email:
                school.contact_email = f"info@{code}.es".lower()

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue

    session.commit()
    session.close()
    print(f"Import Complete. New: {count_new}, Updated: {count_updated}")

if __name__ == "__main__":
    import_data()
