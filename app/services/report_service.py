
from datetime import date
from sqlalchemy import func
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.queue_entry import QueueEntry

class ReportService:
    def doctor_workload(self,db):
        doctors=db.query(Doctor).order_by(Doctor.id).all(); result=[]
        for doctor in doctors:
            appointments=db.query(Appointment).filter(Appointment.doctor_id==doctor.id).all()
            result.append({"doctor_id":doctor.id,"doctor_name":f"{doctor.first_name} {doctor.last_name}","total_appointments":len(appointments),
                "completed_appointments":sum(a.status=="COMPLETED" for a in appointments),"cancelled_appointments":sum(a.status=="CANCELLED" for a in appointments)})
        return result

    def today_care_flow(self,db):
        today=date.today()
        appointments=db.query(Appointment).filter(Appointment.appointment_date==today).all()
        queues=db.query(QueueEntry).filter(func.date(QueueEntry.arrival_time)==today).all()
        return {"date":str(today),"total_appointments":len(appointments),
            "scheduled":sum(a.status=="SCHEDULED" for a in appointments),"checked_in":sum(a.status=="CHECKED_IN" for a in appointments),
            "in_queue":sum(a.status=="IN_QUEUE" for a in appointments),"in_consultation":sum(a.status=="IN_CONSULTATION" for a in appointments),
            "completed":sum(a.status=="COMPLETED" for a in appointments),"cancelled":sum(a.status=="CANCELLED" for a in appointments),
            "waiting_queue":sum(q.status=="WAITING" for q in queues),"called":sum(q.status=="CALLED" for q in queues),
            "queue_completed":sum(q.status=="COMPLETED" for q in queues)}
