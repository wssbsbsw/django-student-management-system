from django import forms

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id',
            'name',
            'gender',
            'age',
            'class_name',
            'phone',
            'email',
            'address',
            'enrollment_date',
        ]
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class StudentSearchForm(forms.Form):
    student_id = forms.CharField(label='学号', max_length=20, required=False)
    name = forms.CharField(label='姓名', max_length=50, required=False)
    class_name = forms.CharField(label='班级', max_length=50, required=False)
