import django.db
from decimal import Decimal
from django.db.models import Q, F
from core.models import Employee, Course

print("=" * 60)
print("TASK 4.1: Q objects")
print("=" * 60)

# Query 1: IT department OR salary > 70000
query_or = Employee.objects.filter(
    Q(department__code="IT") | Q(salary__gt=70000)
)
print("OR Query Results:", list(query_or))
print("SQL:", query_or.query)

# Query 2: first name contains John AND NOT in HR
query_not = Employee.objects.filter(
    Q(first_name__icontains="John") & ~Q(department__code="HR")
)
print("AND NOT Query Results:", list(query_not))
print("SQL:", query_not.query)

print()
print("=" * 60)
print("TASK 4.2: F expressions")
print("=" * 60)

print("Before update:")
for emp in Employee.objects.filter(department__code="IT"):
    print(f"  {emp.first_name} Salary: {emp.salary}")

# 10% raise done inside the database (one UPDATE statement)
Employee.objects.filter(department__code="IT").update(salary=F('salary') * Decimal('1.10'))

print("After update:")
for emp in Employee.objects.filter(department__code="IT"):
    print(f"  {emp.first_name} New Salary: {emp.salary}")

print()
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