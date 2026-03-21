from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
import math

app = FastAPI()

# Home Route
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


# Doctors Data
doctors = [
    {"id": 1, "name": "Dr. Sharma", "specialization": "Cardiologist", "fee": 500, "experience_years": 10, "is_available": True},
    {"id": 2, "name": "Dr. Mehta", "specialization": "Dermatologist", "fee": 300, "experience_years": 7, "is_available": True},
    {"id": 3, "name": "Dr. Rao", "specialization": "Pediatrician", "fee": 400, "experience_years": 8, "is_available": False},
    {"id": 4, "name": "Dr. Patel", "specialization": "General", "fee": 200, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Singh", "specialization": "Cardiologist", "fee": 600, "experience_years": 12, "is_available": True},
    {"id": 6, "name": "Dr. Khan", "specialization": "Dermatologist", "fee": 350, "experience_years": 6, "is_available": False}
]


# Appointments
appointments = []
appt_counter = 1


# Helper Functions
def find_doctor(doctor_id):
    for d in doctors:
        if d["id"] == doctor_id:
            return d
    return None

def calculate_fee(base_fee, appointment_type, senior=False):
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    if senior:
        fee *= 0.85

    return round(fee, 2)

# GET Doctors
@app.get("/doctors")
def get_doctors():
    available = len([d for d in doctors if d["is_available"]])
    return {
        "doctors": doctors,
        "total": len(doctors),
        "available_count": available
    }


# Summary (IMPORTANT above ID route)
@app.get("/doctors/summary")
def doctors_summary():
    most_exp = max(doctors, key=lambda x: x["experience_years"])
    cheapest = min(doctors, key=lambda x: x["fee"])

    spec_count = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1

    return {
        "total": len(doctors),
        "available": len([d for d in doctors if d["is_available"]]),
        "most_experienced": most_exp["name"],
        "cheapest_fee": cheapest["fee"],
        "specializations": spec_count
    }


# Filter Doctors
@app.get("/doctors/filter")
def filter_doctors(
    specialization: str = None,
    max_fee: int = None,
    min_experience: int = None,
    is_available: bool = None
):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"] == specialization]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]

    return {"results": result, "count": len(result)}


# Search Doctors
@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not result:
        return {"message": "No doctors found"}

    return {"results": result, "total_found": len(result)}


# Sort Doctors
@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    valid = ["fee", "name", "experience_years"]

    if sort_by not in valid:
        raise HTTPException(400, "Invalid sort field")

    reverse = True if order == "desc" else False
    sorted_data = sorted(doctors, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "data": sorted_data}


# Pagination
@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    total_pages = math.ceil(len(doctors) / limit)

    return {
        "page": page,
        "limit": limit,
        "total": len(doctors),
        "total_pages": total_pages,
        "data": doctors[start:start+limit]
    }


# Browse
@app.get("/doctors/browse")
def browse_doctors(
    keyword: str = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    data = doctors

    if keyword:
        data = [d for d in data if keyword.lower() in d["name"].lower()]

    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    total_pages = math.ceil(len(data) / limit)

    return {
        "total": len(data),
        "page": page,
        "total_pages": total_pages,
        "results": data[start:start+limit]
    }


# Get Doctor by ID (AFTER fixed routes)
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")
    return doc


# Appointment Model
class AppointmentRequest(BaseModel):
    patient_name: str = Field(min_length=2)
    doctor_id: int = Field(gt=0)
    date: str = Field(min_length=8)
    reason: str = Field(min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False



# GET Appointments
@app.get("/appointments")
def get_appointments():
    return {"appointments": appointments, "total": len(appointments)}


# Book Appointment
@app.post("/appointments")
def book_appointment(req: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(req.doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")

    if not doctor["is_available"]:
        raise HTTPException(400, "Doctor not available")

    original_fee = doctor["fee"]
    final_fee = calculate_fee(original_fee, req.appointment_type, req.senior_citizen)

    appt = {
        "appointment_id": appt_counter,
        "patient": req.patient_name,
        "doctor": doctor["name"],
        "date": req.date,
        "type": req.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appt)
    appt_counter += 1

    return appt


# Confirm Appointment
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "confirmed"
            return a
    raise HTTPException(404, "Appointment not found")


# Cancel Appointment
@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "cancelled"
            return a
    raise HTTPException(404, "Appointment not found")


# Complete Appointment
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "completed"
            return a
    raise HTTPException(404, "Appointment not found")


# Active Appointments
@app.get("/appointments/active")
def active_appointments():
    result = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {"active": result}


# By Doctor
@app.get("/appointments/by-doctor/{doctor_id}")
def by_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    result = [a for a in appointments if a["doctor"] == doc["name"]]
    return result


# Search Appointments
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    result = [a for a in appointments if patient_name.lower() in a["patient"].lower()]
    return {"results": result}


# Sort Appointments
@app.get("/appointments/sort")
def sort_appointments():
    return sorted(appointments, key=lambda x: x["final_fee"])


# Pagination
@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return appointments[start:start+limit]


# Add Doctor
class NewDoctor(BaseModel):
    name: str = Field(min_length=2)
    specialization: str
    fee: int = Field(gt=0)
    experience_years: int = Field(gt=0)
    is_available: bool = True

@app.post("/doctors", status_code=201)
def add_doctor(doc: NewDoctor):
    for d in doctors:
        if d["name"].lower() == doc.name.lower():
            raise HTTPException(400, "Doctor already exists")

    new_doc = doc.dict()
    new_doc["id"] = len(doctors) + 1
    doctors.append(new_doc)

    return new_doc


# Update Doctor
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: int = None, is_available: bool = None):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    if fee is not None:
        doc["fee"] = fee

    if is_available is not None:
        doc["is_available"] = is_available

    return doc


# Delete Doctor
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    for a in appointments:
        if a["doctor"] == doc["name"] and a["status"] == "scheduled":
            raise HTTPException(400, "Doctor has active appointments")

    doctors.remove(doc)
    return {"message": "Doctor deleted successfully"}
