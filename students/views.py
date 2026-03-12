from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import StudentForm, StudentSearchForm
from .models import Student


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "注册成功，已自动登录。")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "注册失败，请检查用户名和密码。")
        return super().form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "students/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_count = Student.objects.count()
        raw_class_summary = list(
            Student.objects.values("class_name")
            .annotate(total=Count("id"))
            .order_by("-total", "class_name")
        )
        top_total = raw_class_summary[0]["total"] if raw_class_summary else 0

        class_summary = []
        for item in raw_class_summary:
            total = item["total"]
            item["percent"] = (
                round((total / student_count) * 100, 1) if student_count else 0
            )
            item["bar_width"] = round((total / top_total) * 100, 1) if top_total else 0
            class_summary.append(item)

        context["student_count"] = student_count
        context["class_count"] = len(raw_class_summary)
        context["recent_students"] = Student.objects.order_by("-created_at")[:5]
        context["class_summary"] = class_summary
        context["top_class"] = class_summary[0] if class_summary else None
        return context


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 10

    sort_options = {
        "student_id": "student_id",
        "-student_id": "-student_id",
        "name": "name",
        "-name": "-name",
        "class_name": "class_name",
        "-class_name": "-class_name",
        "age": "age",
        "-age": "-age",
        "enrollment_date": "enrollment_date",
        "-enrollment_date": "-enrollment_date",
        "created_at": "-created_at",
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_form = StudentSearchForm(self.request.GET)
        sort = self.request.GET.get("sort", "student_id")
        self.current_sort = sort if sort in self.sort_options else "student_id"

        if self.search_form.is_valid():
            student_id = self.search_form.cleaned_data["student_id"]
            name = self.search_form.cleaned_data["name"]
            class_name = self.search_form.cleaned_data["class_name"]
            if student_id:
                queryset = queryset.filter(student_id__icontains=student_id)
            if name:
                queryset = queryset.filter(name__icontains=name)
            if class_name:
                queryset = queryset.filter(class_name__icontains=class_name)
        return queryset.order_by(self.sort_options[self.current_sort])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_without_page = self.request.GET.copy()
        query_without_page.pop("page", None)
        preserved_query = query_without_page.urlencode()

        context["search_form"] = getattr(self, "search_form", StudentSearchForm())
        context["student_count"] = Student.objects.count()
        context["class_count"] = Student.objects.values("class_name").distinct().count()
        context["current_sort"] = self.current_sort
        context["preserved_query"] = preserved_query
        context["filtered_count"] = context["page_obj"].paginator.count
        context["sort_choices"] = [
            ("student_id", "学号升序"),
            ("-student_id", "学号降序"),
            ("name", "姓名升序"),
            ("-name", "姓名降序"),
            ("class_name", "班级升序"),
            ("-class_name", "班级降序"),
            ("age", "年龄升序"),
            ("-age", "年龄降序"),
            ("enrollment_date", "入学日期升序"),
            ("-enrollment_date", "入学日期降序"),
            ("created_at", "最新录入优先"),
        ]
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    context_object_name = "student"


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        messages.success(self.request, "学生信息创建成功。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "学生信息创建失败，请检查输入内容。")
        return super().form_invalid(form)


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        messages.success(self.request, "学生信息更新成功。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "学生信息更新失败，请检查输入内容。")
        return super().form_invalid(form)


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = reverse_lazy("student_list")
    context_object_name = "student"

    def form_valid(self, form):
        messages.success(self.request, "学生信息删除成功。")
        return super().form_valid(form)
