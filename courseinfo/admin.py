from django.contrib import admin

from .models import Course, Instructor, Period, Registration, Section, Semester, Student, Year

admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Period)
admin.site.register(Registration)
admin.site.register(Section)
admin.site.register(Semester)
admin.site.register(Student)
admin.site.register(Year)
