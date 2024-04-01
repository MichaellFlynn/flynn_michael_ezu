from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .forms import InstructorForm, SectionForm, CourseForm, SemesterForm, StudentForm, RegistrationForm
from .models import (
    Instructor,
    Section,
    Course,
    Semester,
    Student,
    Registration
)
from .utils import ObjectCreateMixin


class InstructorList(View):
    page_kwarg = 'page'
    paginate_by = 25;  # 25 instructors per page
    template_name = 'courseinfo/instructor_list.html'

    def get(self, request):
        instructors = Instructor.objects.all()
        paginator = Paginator(
            instructors,
            self.paginate_by
        )
        page_number = request.GET.get(
            self.page_kwarg
        )
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(
                paginator.num_pages)
        if page.has_previous():
            prev_url = "?{pkw}={n}".format(
                pkw=self.page_kwarg,
                n=page.previous_page_number())
        else:
            prev_url = None
        if page.has_next():
            next_url = "?{pkw}={n}".format(
                pkw=self.page_kwarg,
                n=page.next_page_number())
        else:
            next_url = None
        context = {
            'is_paginated':
                page.has_other_pages(),
            'next_page_url': next_url,
            'paginator': paginator,
            'previous_page_url': prev_url,
            'instructor_list': page,
        }
        return render(
            request, self.template_name, context)


class InstructorDetail(View):
    def get(self, request, pk):
        instructor = get_object_or_404(
            Instructor,
            pk=pk
        )
        section_list = instructor.sections.all()
        return render(
            request,
            'courseinfo/instructor_detail.html',
            {'instructor': instructor, 'section_list': section_list}
        )


class InstructorCreate(ObjectCreateMixin, View):
    form_class = InstructorForm
    template_name = 'courseinfo/instructor_form.html'


class InstructorUpdate(View):
    form_class = InstructorForm
    model = Instructor
    template_name = 'courseinfo/instructor_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        instructor = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=instructor),
            'instructor': instructor,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        instructor = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=instructor)
        if bound_form.is_valid():
            new_instructor = bound_form.save()
            return redirect(new_instructor)
        else:
            context = {
                'form': bound_form,
                'instructor': instructor,
            }
            return render(
                request,
                self.template_name,
                context)


class InstructorDelete(View):

    def get(self, request, pk):
        instructor = self.get_object(pk)
        sections = instructor.sections.all()
        if sections.count() > 0:
            return render(
                request,
                'courseinfo/instructor_refuse_delete.html',
                {'instructor': instructor,
                 'sections': sections,
                 }
            )
        else:
            return render(
                request,
                'courseinfo/instructor_confirm_delete.html',
                {'instructor': instructor}
            )

    def get_object(self, pk):
        return get_object_or_404(
            Instructor,
            pk=pk)

    def post(self, request, pk):
        instructor = self.get_object(pk)
        instructor.delete()
        return redirect('courseinfo_instructor_list_urlpattern')


class SectionList(View):
    def get(self, request):
        return render(
            request,
            'courseinfo/section_list.html',
            {'section_list': Section.objects.all()}
        )


class SectionDetail(View):
    def get(self, request, pk):
        section = get_object_or_404(
            Section,
            pk=pk
        )
        semester = section.semester
        course = section.course
        instructor = section.instructor
        registration_list = section.registrations.all()
        return render(
            request,
            'courseinfo/section_detail.html',
            {'section': section,
             'semester': semester,
             'course': course,
             'instructor': instructor,
             'registration_list': registration_list}
            )


class SectionCreate(ObjectCreateMixin, View):
    form_class = SectionForm
    template_name = 'courseinfo/section_form.html'


class SectionUpdate(View):
    form_class = SectionForm
    model = Section
    template_name = 'courseinfo/section_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        section = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=section),
            'section': section,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        section = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=section)
        if bound_form.is_valid():
            new_section = bound_form.save()
            return redirect(new_section)
        else:
            context = {
                'form': bound_form,
                'section': section,
            }
            return render(
                request,
                self.template_name,
                context)


class SectionDelete(View):

    def get(self, request, pk):
        section = self.get_object(pk)
        registrations = section.registrations.all()
        if registrations.count() > 0:
            return render(
                request,
                'courseinfo/section_refuse_delete.html',
                {'section': section,
                 'registrations': registrations,
                 }
            )
        else:
            return render(
                request,
                'courseinfo/section_confirm_delete.html',
                {'section': section}
            )

    def get_object(self, pk):
        return get_object_or_404(
            Section,
            pk=pk)

    def post(self, request, pk):
        section = self.get_object(pk)
        section.delete()
        return redirect('courseinfo_section_list_urlpattern')


class CourseList(View):
    def get(self, request):
        return render(
            request,
            'courseinfo/course_list.html',
            {'course_list': Course.objects.all()}
        )


class CourseDetail(View):
    def get(self, request, pk):
        course = get_object_or_404(
            Course,
            pk=pk
        )
        section_list = course.sections.all()
        return render(
            request,
            'courseinfo/course_detail.html',
            {'course': course, 'section_list': section_list}
        )


class CourseCreate(ObjectCreateMixin, View):
    form_class = CourseForm
    template_name = 'courseinfo/course_form.html'


class CourseUpdate(View):
    form_class = CourseForm
    model = Course
    template_name = 'courseinfo/course_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        course = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=course),
            'course': course,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        course = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=course)
        if bound_form.is_valid():
            new_course = bound_form.save()
            return redirect(new_course)
        else:
            context = {
                'form': bound_form,
                'course': course,
            }
            return render(
                request,
                self.template_name,
                context)


class CourseDelete(View):

    def get(self, request, pk):
        course = self.get_object(pk)
        sections = course.sections.all()
        if sections.count() > 0:
            return render(
                request,
                'courseinfo/course_refuse_delete.html',
                {'course': course,
                 'sections': sections,
                 }
            )
        else:
            return render(
                request,
                'courseinfo/course_confirm_delete.html',
                {'course': course}
            )

    def get_object(self, pk):
        course = get_object_or_404(
            Course,
            pk=pk
        )
        return course

    def post(self, request, pk):
        course = self.get_object(pk)
        course.delete()
        return redirect('courseinfo_course_list_urlpattern')


class SemesterList(View):
    def get(self, request):
        return render(
            request,
            'courseinfo/semester_list.html',
            {'semester_list': Semester.objects.all()}
        )


class SemesterDetail(View):
    def get(self, request, pk):
        semester = get_object_or_404(
            Semester,
            pk=pk
        )
        section_list = semester.sections.all()
        return render(
            request,
            'courseinfo/semester_detail.html',
            {'semester': semester, 'section_list': section_list}
        )


class SemesterCreate(ObjectCreateMixin, View):
    form_class = SemesterForm
    template_name = 'courseinfo/semester_form.html'


class SemesterUpdate(View):
    form_class = SemesterForm
    model = Semester
    template_name = 'courseinfo/semester_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        semester = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=semester),
            'semester': semester,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        semester = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=semester)
        if bound_form.is_valid():
            new_semester = bound_form.save()
            return redirect(new_semester)
        else:
            context = {
                'form': bound_form,
                'semester': semester,
            }
            return render(
                request,
                self.template_name,
                context)


class SemesterDelete(View):

    def get(self, request, pk):
        semester = self.get_object(pk)
        sections = semester.sections.all()
        if sections.count() > 0:
            return render(
                request,
                'courseinfo/semester_refuse_delete.html',
                {'semester': semester,
                 'sections': sections,
                 }
            )
        else:
            return render(
                request,
                'courseinfo/semester_confirm_delete.html',
                {'semester': semester}
            )

    def get_object(self, pk):
        semester = get_object_or_404(
            Semester,
            pk=pk
        )
        return semester

    def post(self, request, pk):
        semester = self.get_object(pk)
        semester.delete()
        return redirect('courseinfo_semester_list_urlpattern')


class StudentList(View):
    page_kwarg = 'page'
    paginate_by = 25;  # 25 students per page
    template_name = 'courseinfo/student_list.html'

    def get(self, request):
        students = Student.objects.all()
        paginator = Paginator(
            students,
            self.paginate_by
        )
        page_number = request.GET.get(
            self.page_kwarg
        )
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(
                paginator.num_pages)
        if page.has_previous():
            prev_url = "?{pkw}={n}".format(
                pkw=self.page_kwarg,
                n=page.previous_page_number())
        else:
            prev_url = None
        if page.has_next():
            next_url = "?{pkw}={n}".format(
                pkw=self.page_kwarg,
                n=page.next_page_number())
        else:
            next_url = None
        context = {
            'is_paginated':
                page.has_other_pages(),
            'next_page_url': next_url,
            'paginator': paginator,
            'previous_page_url': prev_url,
            'student_list': page,
        }
        return render(
            request, self.template_name, context)


class StudentDetail(View):
    def get(self, request, pk):
        student = get_object_or_404(
            Student,
            pk=pk
        )
        registration_list = student.registrations.all()
        return render(
            request,
            'courseinfo/student_detail.html',
            {'student': student, 'registration_list': registration_list}
        )


class StudentCreate(ObjectCreateMixin, View):
    form_class = StudentForm
    template_name = 'courseinfo/student_form.html'


class StudentUpdate(View):
    form_class = StudentForm
    model = Student
    template_name = 'courseinfo/student_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        student = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=student),
            'student': student,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        student = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=student)
        if bound_form.is_valid():
            new_student = bound_form.save()
            return redirect(new_student)
        else:
            context = {
                'form': bound_form,
                'student': student,
            }
            return render(
                request,
                self.template_name,
                context)


class StudentDelete(View):

    def get(self, request, pk):
        student = self.get_object(pk)
        registrations = student.registrations.all()
        if registrations.count() > 0:
            return render(
                request,
                'courseinfo/student_refuse_delete.html',
                {'student': student,
                 'registrations': registrations,
                 }
            )
        else:
            return render(
                request,
                'courseinfo/student_confirm_delete.html',
                {'student': student}
            )

    def get_object(self, pk):
        student = get_object_or_404(
            Student,
            pk=pk
        )
        return student

    def post(self, request, pk):
        student = self.get_object(pk)
        student.delete()
        return redirect('courseinfo_student_list_urlpattern')


class RegistrationList(View):
    def get(self, request):
        return render(
            request,
            'courseinfo/registration_list.html',
            {'registration_list': Registration.objects.all()}
        )


class RegistrationDetail(View):
    def get(self, request, pk):
        registration = get_object_or_404(
            Registration,
            pk=pk
        )
        return render(
            request,
            'courseinfo/registration_detail.html',
            {'registration': registration, 'student': registration.student, 'section': registration.section}
        )


class RegistrationCreate(ObjectCreateMixin, View):
    form_class = RegistrationForm
    template_name = 'courseinfo/registration_form.html'


class RegistrationUpdate(View):
    form_class = RegistrationForm
    model = Student
    template_name = 'courseinfo/registration_form_update.html'

    def get_object(self, pk):
        return get_object_or_404(
            self.model,
            pk=pk)

    def get(self, request, pk):
        registration = self.get_object(pk)
        context = {
            'form': self.form_class(
                instance=registration),
            'registration': registration,
        }
        return render(
            request, self.template_name, context)

    def post(self, request, pk):
        registration = self.get_object(pk)
        bound_form = self.form_class(
            request.POST, instance=registration)
        if bound_form.is_valid():
            new_registration = bound_form.save()
            return redirect(new_registration)
        else:
            context = {
                'form': bound_form,
                'registration': registration,
            }
            return render(
                request,
                self.template_name,
                context)


class RegistrationDelete(View):

    def get(self, request, pk):
        registration = self.get_object(pk)
        return render(
            request,
            'courseinfo/registration_confirm_delete.html',
            {'registration': registration}
        )

    def get_object(self, pk):
        registration = get_object_or_404(
            Registration,
            pk=pk
        )
        return registration

    def post(self, request, pk):
        registration = self.get_object(pk)
        registration.delete()
        return redirect('courseinfo_registration_list_urlpattern')
