from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r'^[0-9+\-\s]{6,20}$',
    message='请输入有效的电话号码。',
)


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', '男'
        FEMALE = 'F', '女'

    student_id = models.CharField('学号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=Gender.choices)
    age = models.PositiveSmallIntegerField(
        '年龄',
        validators=[MinValueValidator(1), MaxValueValidator(150)],
    )
    class_name = models.CharField('班级', max_length=50)
    phone = models.CharField('电话', max_length=20, blank=True, validators=[phone_validator])
    email = models.EmailField('邮箱', blank=True)
    address = models.TextField('地址', blank=True)
    enrollment_date = models.DateField('入学日期')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['student_id']
        verbose_name = '学生'
        verbose_name_plural = '学生'

    def __str__(self):
        return f'{self.student_id} - {self.name}'
