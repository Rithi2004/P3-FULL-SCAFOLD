from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Department, Student
from schemas import StudentCreate, StudentOut


router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)) -> list[StudentOut]:
    students = db.scalars(
        select(Student)
        .options(joinedload(Student.department))
        .order_by(Student.student_id)
    ).all()
    return [
        StudentOut(
            student_id=student.student_id,
            student_name=student.student_name,
            department_id=student.department_id,
            department_name=student.department.department_name,
        )
        for student in students
    ]


@router.post(
    "/",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentOut:
    department = db.get(Department, student.department_id)
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    db_student = Student(
        student_name=student.student_name,
        department_id=student.department_id,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return StudentOut(
        student_id=db_student.student_id,
        student_name=db_student.student_name,
        department_id=db_student.department_id,
        department_name=department.department_name,
    )
