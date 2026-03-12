from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'gender', 'age', 'class_name', 'phone', 'email')
    search_fields = ('student_id', 'name', 'class_name')
    list_filter = ('gender', 'class_name')
