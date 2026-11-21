import django.db
from core.models import Employee, Course

print("=" * 60)
print("TASK 4.3: N+1 problem")
print("=" * 60)

# Unoptimized (N+1)
django.db.reset_queries()
employees = Employee.objects.all()
for emp in employees:
    print(f"Employee: {emp.first_name}, Department: {emp.department.name}")

print(f"Total Queries Executed (Unoptimized): {len(django.db.connection.queries)}")

# Solution 1: select_related (ForeignKey)
django.db.reset_queries()
optimized_employees = Employee.objects.select_related('department').all()
for emp in optimized_employees:
    print(f"Employee: {emp.first_name}, Department: {emp.department.name}")

print(f"Total Queries with select_related: {len(django.db.connection.queries)}")

# Solution 2: prefetch_related (ManyToMany)
django.db.reset_queries()
courses = Course.objects.prefetch_related('attendees').all()
for course in courses:
    attendee_names = [emp.first_name for emp in course.attendees.all()]
    print(f"Course: {course.code}, Attendees: {', '.join(attendee_names)}")

print(f"Total Queries with prefetch_related: {len(django.db.connection.queries)}")