"""CSV parser for bulk student import."""
import io
import csv
from typing import List, Dict, Any

REQUIRED_COLUMNS = ["email", "full_name", "enrollment_number", "department_code", "semester", "batch_year"]

def parse_students_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV content and validate required columns."""
    text = file_content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    
    if not reader.fieldnames:
        raise ValueError("CSV file is empty or corrupted")
        
    missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
        
    records = []
    for row_idx, row in enumerate(reader, start=2):
        clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
        try:
            sem = int(clean_row["semester"])
            batch = int(clean_row["batch_year"])
            if not 1 <= sem <= 8:
                raise ValueError("Semester must be between 1 and 8")
        except ValueError as e:
            raise ValueError(f"Row {row_idx}: {str(e)}")
            
        records.append({
            "email": clean_row["email"].lower(),
            "full_name": clean_row["full_name"],
            "enrollment_number": clean_row["enrollment_number"],
            "department_code": clean_row["department_code"].upper(),
            "semester": sem,
            "batch_year": batch,
            "section": clean_row.get("section", "A"),
            "phone": clean_row.get("phone", None)
        })
    return records
