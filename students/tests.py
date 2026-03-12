from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Student


class StudentModelTests(TestCase):
    def test_student_id_must_be_unique(self):
        Student.objects.create(
            student_id="2026001",
            name="张三",
            gender=Student.Gender.MALE,
            age=20,
            class_name="软件工程1班",
            enrollment_date=date(2024, 9, 1),
        )
        duplicate = Student(
            student_id="2026001",
            name="李四",
            gender=Student.Gender.FEMALE,
            age=19,
            class_name="软件工程2班",
            enrollment_date=date(2024, 9, 1),
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_invalid_age_is_rejected(self):
        student = Student(
            student_id="2026002",
            name="张三",
            gender=Student.Gender.MALE,
            age=0,
            class_name="软件工程1班",
            enrollment_date=date(2024, 9, 1),
        )

        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_optional_fields_can_be_blank(self):
        student = Student(
            student_id="2026003",
            name="王五",
            gender=Student.Gender.FEMALE,
            age=18,
            class_name="软件工程3班",
            phone="",
            email="",
            address="",
            enrollment_date=date(2024, 9, 1),
        )

        student.full_clean()


class StudentViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin", password="admin12345"
        )
        self.student = Student.objects.create(
            student_id="2026001",
            name="张三",
            gender=Student.Gender.MALE,
            age=20,
            class_name="软件工程1班",
            phone="13800000000",
            email="zhangsan@example.com",
            address="上海市浦东新区",
            enrollment_date=date(2024, 9, 1),
        )
        for index in range(20, 32):
            Student.objects.create(
                student_id=f"2026{index:03d}",
                name=f"学生{index}",
                gender=Student.Gender.MALE if index % 2 else Student.Gender.FEMALE,
                age=18 + (index % 5),
                class_name=f"软件工程{(index % 3) + 1}班",
                phone=f"1380000{index:04d}",
                email=f"student{index}@example.com",
                address=f"测试地址{index}",
                enrollment_date=date(2024, 9, (index % 9) + 1),
            )

    def test_login_required_for_student_list(self):
        response = self.client.get(reverse("student_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_signup_page_is_available(self):
        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "管理员注册")

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newadmin",
                "password1": "ComplexPass12345",
                "password2": "ComplexPass12345",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(get_user_model().objects.filter(username="newadmin").exists())
        dashboard_response = self.client.get(reverse("dashboard"))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_dashboard_and_list_available_after_login(self):
        self.client.login(username="admin", password="admin12345")

        dashboard_response = self.client.get(reverse("dashboard"))
        list_response = self.client.get(reverse("student_list"))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "张三")

    def test_student_search_by_class_name(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.get(
            reverse("student_list"), {"class_name": "软件工程1班"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "张三")

    def test_student_list_supports_pagination(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.get(reverse("student_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(response.context["students"]), 10)

    def test_student_list_supports_sorting(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.get(reverse("student_list"), {"sort": "-age"})

        self.assertEqual(response.status_code, 200)
        students = list(response.context["students"])
        self.assertGreaterEqual(students[0].age, students[1].age)
        self.assertEqual(response.context["current_sort"], "-age")

    def test_dashboard_contains_class_summary_chart_context(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("class_summary", response.context)
        self.assertIsNotNone(response.context["top_class"])
        self.assertContains(response, "Top Class")

    def test_create_student(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.post(
            reverse("student_create"),
            {
                "student_id": "2026002",
                "name": "李四",
                "gender": Student.Gender.FEMALE,
                "age": 19,
                "class_name": "软件工程2班",
                "phone": "13900000000",
                "email": "lisi@example.com",
                "address": "北京市海淀区",
                "enrollment_date": "2024-09-01",
            },
        )

        self.assertRedirects(response, reverse("student_list"))
        self.assertTrue(Student.objects.filter(student_id="2026002").exists())

    def test_update_student(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.post(
            reverse("student_update", args=[self.student.pk]),
            {
                "student_id": self.student.student_id,
                "name": "张三丰",
                "gender": Student.Gender.MALE,
                "age": 21,
                "class_name": "软件工程1班",
                "phone": "13800000000",
                "email": "zhangsanfeng@example.com",
                "address": "杭州市西湖区",
                "enrollment_date": "2024-09-01",
            },
        )

        self.assertRedirects(response, reverse("student_list"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, "张三丰")

    def test_delete_student(self):
        self.client.login(username="admin", password="admin12345")

        response = self.client.post(reverse("student_delete", args=[self.student.pk]))

        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())
