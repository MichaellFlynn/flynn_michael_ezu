from django.test import TestCase
from courseinfo.models import Period, Year, Semester, Course, Instructor, Student, Section, Registration
from django.db import IntegrityError
from django.urls import reverse

# NOTE: Template Tests all required the additional 'name=' param in urls.py configuration for reverse() to work
# Credit to https://stackoverflow.com/questions/29590623/testing-for-links-in-a-page-content-in-django, Week 10 Tests


class ModelTests(TestCase):
    # Initialize to avoid "unresolved attribute reference" error
    year, period, semester, course, instructor, student, section = None, None, None, None, None, None, None

    @classmethod
    def setUpTestData(cls):
        cls.period = Period.objects.create(period_sequence=1, period_name="Spring")
        cls.year = Year.objects.create(year=2024)
        cls.semester = Semester.objects.create(year=cls.year, period=cls.period)
        cls.course = Course.objects.create(course_number="IS439",
                                           course_name="Web Development Using Application Frameworks")
        cls.instructor = Instructor.objects.create(first_name="Henry", last_name="Gerard", disambiguator="Harvard")
        cls.instructor_no_disambiguator = Instructor.objects.create(first_name="Mike", last_name="Ross")
        cls.student = Student.objects.create(first_name="Harvey", last_name="Specter", disambiguator="New York")
        cls.student_no_disambiguator = Student.objects.create(first_name="Jessica", last_name="Pearson")
        cls.section = Section.objects.create(section_name="AOG/AOU", semester=cls.semester,
                                             course=cls.course, instructor=cls.instructor)
        cls.registration = Registration.objects.create(student=cls.student, section=cls.section)

    def test_period(self):
        self.assertEqual(self.period.period_sequence, 1)
        self.assertEqual(self.period.period_name, "Spring")
        self.assertEqual(self.period.__str__(), "Spring")
        ordering = self.period._meta.ordering
        self.assertEqual(ordering, ["period_sequence"])

    def test_year(self):
        self.assertEqual(self.year.year, 2024)
        self.assertEqual(self.year.__str__(), "2024")
        ordering = self.year._meta.ordering
        self.assertEqual(ordering, ["year"])

    def test_semester(self):
        self.assertEqual(self.semester.year.year, 2024)
        self.assertEqual(self.semester.period.period_name, "Spring")
        self.assertEqual(self.semester.__str__(), "2024 - Spring")
        ordering = self.semester._meta.ordering
        self.assertEqual(ordering, ['year__year', 'period__period_sequence'])
        # Uniqueness constraint, can't have two of same Year/Period
        with self.assertRaises(IntegrityError):
            Semester.objects.create(year=self.year, period=self.period)
        # Incorrectly populating FK will produce ValueError
        with self.assertRaises(ValueError):
            Semester.objects.create(year="2024", period=self.period)
        with self.assertRaises(ValueError):
            Semester.objects.create(year=self.year, period="Fall")

    def test_course(self):
        self.assertEqual(self.course.course_number, "IS439")
        self.assertEqual(self.course.course_name, "Web Development Using Application Frameworks")
        self.assertEqual(self.course.__str__(), "IS439 - Web Development Using Application Frameworks")
        ordering = self.course._meta.ordering
        self.assertEqual(ordering, ["course_number", "course_name"])
        # Uniqueness constraint test
        with self.assertRaises(IntegrityError):
            Course.objects.create(course_number="IS439", course_name="Web Development Using Application Frameworks")

    def test_instructor(self):
        self.assertEqual(self.instructor.first_name, "Henry")
        self.assertEqual(self.instructor.last_name, "Gerard")
        self.assertEqual(self.instructor.disambiguator, "Harvard")
        self.assertEqual(self.instructor.__str__(), "Gerard, Henry (Harvard)")
        self.assertEqual(self.instructor_no_disambiguator.first_name, "Mike")
        self.assertEqual(self.instructor_no_disambiguator.last_name, "Ross")
        self.assertEqual(self.instructor_no_disambiguator.__str__(), "Ross, Mike")
        ordering = self.instructor._meta.ordering
        self.assertEqual(ordering, ['last_name', 'first_name', 'disambiguator'])
        # Uniqueness constraint test (error when all same, including disambiguator)
        with self.assertRaises(IntegrityError):
            Instructor.objects.create(first_name="Henry", last_name="Gerard", disambiguator="Harvard")

    def test_student(self):
        self.assertEqual(self.student.first_name, "Harvey")
        self.assertEqual(self.student.last_name, "Specter")
        self.assertEqual(self.student.disambiguator, "New York")
        self.assertEqual(self.student.__str__(), "Specter, Harvey (New York)")
        self.assertEqual(self.student_no_disambiguator.first_name, "Jessica")
        self.assertEqual(self.student_no_disambiguator.last_name, "Pearson")
        self.assertEqual(self.student_no_disambiguator.__str__(), "Pearson, Jessica")
        ordering = self.student._meta.ordering
        self.assertEqual(ordering, ['last_name', 'first_name', 'disambiguator'])
        # Uniqueness constraint test (error when all same, including disambiguator)
        with self.assertRaises(IntegrityError):
            Student.objects.create(first_name="Harvey", last_name="Specter", disambiguator="New York")

    def test_section(self):
        self.assertEqual(self.section.section_name, "AOG/AOU")
        self.assertEqual(self.section.semester.__str__(), "2024 - Spring")
        self.assertEqual(self.section.course.__str__(), "IS439 - Web Development Using Application Frameworks")
        self.assertEqual(self.section.instructor.__str__(), "Gerard, Henry (Harvard)")
        self.assertEqual(self.section.__str__(), "IS439 - AOG/AOU (2024 - Spring)")
        ordering = self.section._meta.ordering
        self.assertEqual(ordering, ['course', 'section_name', 'semester'])
        # Uniqueness constraint test
        with self.assertRaises(IntegrityError):
            Section.objects.create(section_name="AOG/AOU", semester=self.semester,
                                   course=self.course, instructor=self.instructor)

    def test_registration(self):
        self.assertEqual(self.registration.student.__str__(), "Specter, Harvey (New York)")
        self.assertEqual(self.registration.section.__str__(), "IS439 - AOG/AOU (2024 - Spring)")
        self.assertEqual(self.registration.__str__(), "IS439 - AOG/AOU (2024 - Spring) / Specter, Harvey (New York)")
        ordering = self.registration._meta.ordering
        self.assertEqual(ordering, ['section', 'student'])
        # Uniqueness constraint test
        with self.assertRaises(IntegrityError):
            Registration.objects.create(student=self.student, section=self.section)


class EmptyTemplateTests(TestCase):
    # Test response with no registrations
    def test_registration_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/registration_list.html')
        self.assertContains(response, "There are currently no registrations available.")

    # Test response with no sections
    def test_section_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_section_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/section_list.html')
        self.assertContains(response, "There are currently no sections available.")

    # Test response with no instructors
    def test_instructor_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/instructor_list.html')
        self.assertContains(response, "There are currently no instructors available.")

    # Test response with no students
    def test_student_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_student_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/student_list.html')
        self.assertContains(response, "There are currently no students available.")

    # Test response with no semester
    def test_semester_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_semester_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/semester_list.html')
        self.assertContains(response, "There are currently no semesters available.")

    # Test response with no courses
    def test_course_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_course_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/course_list.html")
        self.assertContains(response, "There are currently no courses available.")


# PopulatedTemplateTests have been updated for Week 10 Submission (testing Linked Pages)
class PopulatedTemplateTests(TestCase):
    # Initialize to avoid "unresolved attribute reference" error
    year, period, semester, course, instructor, student, section = None, None, None, None, None, None, None

    # Populate our database for these template tests
    @classmethod
    def setUpTestData(cls):
        cls.instructor = Instructor.objects.create(first_name="Henry", last_name="Gerard", disambiguator="Harvard")
        cls.student = Student.objects.create(first_name="Harvey", last_name="Specter", disambiguator="New York")
        cls.year = Year.objects.create(year=2024)
        cls.period = Period.objects.create(period_sequence=1, period_name="Spring")
        cls.semester = Semester.objects.create(year=cls.year, period=cls.period)
        cls.course = Course.objects.create(course_number="IS439",
                                           course_name="Web Development Using Application Frameworks")
        cls.section = Section.objects.create(section_name="AOG/AOU",
                                             semester=cls.semester,
                                             course=cls.course,
                                             instructor=cls.instructor)
        cls.registration = Registration.objects.create(student=cls.student,
                                                       section=cls.section)

    # Test response that has an instructor
    def test_instructor_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/instructor_list.html')
        self.assertContains(response, 'Gerard, Henry (Harvard)')
        self.assertNotContains(response, "There are currently no instructors available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.instructor.__str__()}</a>'
                            % reverse('courseinfo_instructor_detail_urlpattern',
                                      kwargs={'pk': self.instructor.pk}), html=True)

    # Test response that has a student
    def test_student_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_student_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/student_list.html')
        self.assertContains(response, "Specter, Harvey (New York)")
        self.assertNotContains(response, "There are currently no students available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.student.__str__()}</a>'
                            % reverse('courseinfo_student_detail_urlpattern',
                                      kwargs={'pk': self.student.pk}), html=True)

    # Test response with a semester
    def test_semester_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_semester_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/semester_list.html')
        self.assertContains(response, "2024 - Spring")
        self.assertNotContains(response, "There are currently no semesters available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.semester.__str__()}</a>'
                            % reverse('courseinfo_semester_detail_urlpattern',
                                      kwargs={'pk': self.semester.pk}), html=True)

    # Test response with a course
    def test_course_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_course_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/course_list.html')
        self.assertContains(response, "IS439 - Web Development Using Application Frameworks")
        self.assertNotContains(response, "There are currently no courses available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.course.__str__()}</a>'
                            % reverse('courseinfo_course_detail_urlpattern',
                                      kwargs={'pk': self.course.pk}), html=True)

    # Test response that has a section
    def test_section_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_section_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/section_list.html")
        self.assertContains(response, "IS439 - AOG/AOU (2024 - Spring)")
        self.assertNotContains(response, "There are currently no sections available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_section_detail_urlpattern',
                                      kwargs={'pk': self.section.pk}), html=True)

    # Test response with a registration
    def test_registration_list_view_populated(self):
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/registration_list.html')
        self.assertContains(response, "IS439 - AOG/AOU (2024 - Spring) / Specter, Harvey (New York)")
        self.assertNotContains(response, "There are currently no registrations available.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.registration.__str__()}</a>'
                            % reverse('courseinfo_registration_detail_urlpattern',
                                      kwargs={'pk': self.registration.pk}), html=True)


# DetailedTemplateTests have been updated for Week 10 Submission (testing Linked Pages)
class DetailedTemplatedTests(TestCase):
    # Test Cases after Week 7, submit for Week 8 Assignment
    # Initialize to avoid "unresolved attribute reference" error
    (year, period, semester, course, instructor, student, section,
     current_year, next_year) = None, None, None, None, None, None, None, None, None

    @classmethod
    # Modified version of prior test data setup to include object_no_object to test multiple scenarios of HTML templates
    def setUpTestData(cls):
        cls.instructor = Instructor.objects.create(first_name="Henry", last_name="Gerard", disambiguator="Harvard")
        cls.instructor_no_section = Instructor.objects.create(first_name="Ms", last_name="Puff")  # New for W7
        cls.student = Student.objects.create(first_name="Harvey", last_name="Specter", disambiguator="New York")
        cls.student_no_registration = Student.objects.create(first_name="Louis", last_name="Litt")  # New for W7
        cls.current_year = Year.objects.create(year=2024)
        cls.next_year = Year.objects.create(year=2025)
        cls.period = Period.objects.create(period_sequence=1, period_name="Spring")
        cls.semester = Semester.objects.create(year=cls.current_year, period=cls.period)
        cls.semester_no_sections = Semester.objects.create(year=cls.next_year, period=cls.period)  # New for W7
        cls.course = Course.objects.create(course_number="IS439",
                                           course_name="Web Development Using Application Frameworks")
        cls.course_no_sections = Course.objects.create(course_number="CS225",
                                                       course_name="Data Structures and Algorithms")  # New for W7
        cls.section = Section.objects.create(section_name="AOG/AOU",
                                             semester=cls.semester,
                                             course=cls.course,
                                             instructor=cls.instructor)
        cls.section_no_students = Section.objects.create(section_name="ABC",
                                                         semester=cls.semester,
                                                         course=cls.course,
                                                         instructor=cls.instructor)  # New for W7
        cls.registration = Registration.objects.create(student=cls.student,
                                                       section=cls.section)

    def test_detailed_instructor_view(self):
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern',
                                           kwargs={'pk': self.instructor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/instructor_detail.html')
        self.assertContains(response, f"Instructor - {self.instructor.__str__()}")
        self.assertContains(response, self.section.__str__())  # Check related section
        self.assertNotContains(response, "There are currently no sections for this instructor.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_section_detail_urlpattern',
                                      kwargs={'pk': self.section.pk}), html=True)

    def test_detailed_instructor_view_no_section(self):
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern',
                                           kwargs={'pk': self.instructor_no_section.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/instructor_detail.html')
        self.assertContains(response, f"Instructor - {self.instructor_no_section.__str__()}")
        self.assertContains(response, "There are currently no sections for this instructor.")

    def test_detailed_section_view(self):
        response = self.client.get(reverse('courseinfo_section_detail_urlpattern',
                                           kwargs={'pk': self.section.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/section_detail.html')
        self.assertContains(response, f"Section - {self.section.__str__()}")
        self.assertContains(response, self.student.__str__())  # Check related student
        self.assertNotContains(response, "There are currently no students registered for this section.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.course.__str__()}</a>'
                            % reverse('courseinfo_course_detail_urlpattern',
                                      kwargs={'pk': self.course.pk}), html=True)
        self.assertContains(response, f'<a href="%s">{self.semester.__str__()}</a>'
                            % reverse('courseinfo_semester_detail_urlpattern',
                                      kwargs={'pk': self.semester.pk}), html=True)
        self.assertContains(response, f'<a href="%s">{self.instructor.__str__()}</a>'
                            % reverse('courseinfo_instructor_detail_urlpattern',
                                      kwargs={'pk': self.instructor.pk}), html=True)
        self.assertContains(response, f'<a href="%s">{self.student.__str__()}</a>'
                            % reverse('courseinfo_registration_detail_urlpattern',
                                      kwargs={'pk': self.registration.pk}), html=True)  # Note the anchor is student

    def test_detailed_section_view_no_students(self):
        response = self.client.get(reverse('courseinfo_section_detail_urlpattern',
                                           kwargs={'pk': self.section_no_students.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/section_detail.html')
        self.assertContains(response, f"Section - {self.section_no_students.__str__()}")
        self.assertContains(response, "There are currently no students registered for this section.")

    def test_detailed_semester_view(self):
        response = self.client.get(reverse('courseinfo_semester_detail_urlpattern',
                                           kwargs={'pk': self.semester.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/semester_detail.html")
        self.assertContains(response, f"Semester - {self.semester.__str__()}")
        self.assertContains(response, self.section.__str__())  # Check related section
        self.assertNotContains(response, "There are currently no sections for this semester.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_section_detail_urlpattern',
                                      kwargs={'pk': self.section.pk}), html=True)

    def test_detailed_semester_view_no_sections(self):
        response = self.client.get(reverse('courseinfo_semester_detail_urlpattern',
                                           kwargs={'pk': self.semester_no_sections.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/semester_detail.html")
        self.assertContains(response, f"Semester - {self.semester_no_sections.__str__()}")
        self.assertContains(response, "There are currently no sections for this semester.")

    def test_detailed_student_view(self):
        response = self.client.get(reverse('courseinfo_student_detail_urlpattern',
                                           kwargs={'pk': self.student.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/student_detail.html")
        self.assertContains(response, f"Student - {self.student.__str__()}")
        self.assertContains(response, self.registration.section.__str__())  # Check related registration
        self.assertNotContains(response, "This student is not currently registered for any sections.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_registration_detail_urlpattern',
                                      kwargs={'pk': self.registration.pk}), html=True)  # Note the anchor is section

    def test_detailed_student_view_no_registrations(self):
        response = self.client.get(reverse('courseinfo_student_detail_urlpattern',
                                           kwargs={'pk': self.student_no_registration.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courseinfo/student_detail.html")
        self.assertContains(response, f"Student - {self.student_no_registration.__str__()}")
        self.assertContains(response, "This student is not currently registered for any sections.")

    def test_detailed_course_view(self):
        response = self.client.get(reverse('courseinfo_course_detail_urlpattern',
                                           kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/course_detail.html')
        self.assertContains(response, f"Course - {self.course.__str__()}")
        self.assertContains(response, self.section.__str__())  # Check related section
        self.assertNotContains(response, "There are currently no sections for this course.")
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_section_detail_urlpattern',
                                      kwargs={'pk': self.section.pk}), html=True)

    def test_detailed_course_view_no_sections(self):
        response = self.client.get(reverse('courseinfo_course_detail_urlpattern',
                                           kwargs={'pk': self.course_no_sections.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/course_detail.html')
        self.assertContains(response, f"Course - {self.course_no_sections.__str__()}")
        self.assertContains(response, "There are currently no sections for this course.")

    def test_detailed_registration_view(self):
        response = self.client.get(reverse('courseinfo_registration_detail_urlpattern',
                                           kwargs={'pk': self.registration.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/registration_detail.html')
        self.assertContains(response, f"Registration - {self.registration.__str__()}")
        # Contains information about related objects
        self.assertContains(response, self.registration.student.__str__())
        self.assertContains(response, self.registration.section.__str__())
        # Test inclusion of proper linked pages (new for Week 10 Assignment submission)
        self.assertContains(response, f'<a href="%s">{self.student.__str__()}</a>'
                            % reverse('courseinfo_student_detail_urlpattern',
                                      kwargs={'pk': self.student.pk}), html=True)
        self.assertContains(response, f'<a href="%s">{self.section.__str__()}</a>'
                            % reverse('courseinfo_section_detail_urlpattern',
                                      kwargs={'pk': self.section.pk}), html=True)


# In addition to modification of classes above, these test cases are new for Week 10 submission.
class HomePageTests(TestCase):
    def test_home_page_redirects(self):
        # Home page should redirect to Section List page. This is an HTTP Code 302 (Not 200).
        response = self.client.get('')
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('courseinfo_section_list_urlpattern'))

    def test_redirected_page_contains_linked_pages(self):
        # Defining all the anchor texts and respective [template]_list names
        header_linked_pages = {
            'Instructors': 'instructor',
            'Sections': 'section',
            'Courses': 'course',
            'Semesters': 'semester',
            'Students': 'student',
            'Registrations': 'registration'
        }
        response = self.client.get('', follow=True)  # Use follow=True parameter to follow the redirection
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'courseinfo/section_list.html')  # Should be section list page
        for anchor, template in header_linked_pages.items():
            self.assertContains(response, f'<a href="%s">{anchor}</a>'
                                % reverse(f'courseinfo_{template}_list_urlpattern'), html=True)


# For Week 11 (testing Week 10: Forms Assignment) CRUD Behavior
class FormCRUDTests(TestCase):
    # TODO: Figure out how to implement tests for dependent objects (e.g., section, registration, semester)
    def test_instructor_crud(self):
        # [C] Begin by Creating an Instructor
        instructor_count = Instructor.objects.count()
        get_create_instructor = self.client.get(reverse("courseinfo_instructor_create_urlpattern"))
        self.assertEqual(get_create_instructor.status_code, 200)
        self.assertTemplateUsed(get_create_instructor, 'courseinfo/instructor_form.html')
        post_create_instructor = self.client.post(reverse('courseinfo_instructor_create_urlpattern'),
                                                  data={'first_name': 'Henry', 'last_name': 'Gerard'})
        self.assertEqual(post_create_instructor.status_code, 302)
        instructor = Instructor.objects.first()
        self.assertRedirects(post_create_instructor, reverse('courseinfo_instructor_detail_urlpattern',
                                                             kwargs={'pk': instructor.pk}))
        self.assertEqual(Instructor.objects.count(), instructor_count + 1)

        # [R] Check that the created Instructor exists (list page)
        read_instructor_list = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(read_instructor_list.status_code, 200)
        self.assertContains(read_instructor_list, f'<a href="%s">{instructor.__str__()}</a>'
                            % reverse('courseinfo_instructor_detail_urlpattern',
                                      kwargs={'pk': instructor.pk}), html=True)

        # [U/D] Check that update and delete exists on detailed page
        read_instructor_detailed = self.client.get(reverse("courseinfo_instructor_detail_urlpattern",
                                                           kwargs={'pk': instructor.pk}))
        self.assertEqual(read_instructor_detailed.status_code, 200)
        self.assertContains(read_instructor_detailed,
                            f'<a href="{instructor.get_update_url()}">Edit Instructor</a>')
        self.assertContains(read_instructor_detailed,
                            f'<a href="{instructor.get_delete_url()}">Delete Instructor</a>')

        # [U] Update the instructor information
        self.assertEqual(instructor.disambiguator, "")
        get_update_instructor = self.client.get(reverse("courseinfo_instructor_update_urlpattern",
                                                        kwargs={'pk': instructor.pk}))
        self.assertEqual(get_update_instructor.status_code, 200)
        self.assertTemplateUsed(get_update_instructor, 'courseinfo/instructor_form_update.html')
        post_update_instructor = self.client.post(reverse('courseinfo_instructor_update_urlpattern',
                                                          kwargs={'pk': instructor.pk}),
                                                  data={"first_name": "Henry",
                                                        "last_name": "Gerard",
                                                        "disambiguator": "Harvard"})
        self.assertEqual(post_update_instructor.status_code, 302)
        self.assertRedirects(post_update_instructor, reverse('courseinfo_instructor_detail_urlpattern',
                                                             kwargs={'pk': instructor.pk}))
        instructor.refresh_from_db()
        self.assertEqual(instructor.disambiguator, "Harvard")

        # [C] Trying to duplicate instructor (expect error message)
        post_duplicate = self.client.post(reverse('courseinfo_instructor_create_urlpattern'),
                                          data={'first_name': 'Henry',
                                                'last_name': 'Gerard',
                                                'disambiguator': 'Harvard'})
        self.assertEqual(post_duplicate.status_code, 200)  # No redirect because it cannot be created
        self.assertTemplateUsed(post_duplicate, 'courseinfo/instructor_form.html')
        self.assertContains(post_duplicate,
                            "<li>Instructor with this Last name, First name and Disambiguator already exists.</li>",
                            html=True)

        # [D] Delete the instructor
        get_delete_instructor = self.client.get(reverse('courseinfo_instructor_delete_urlpattern',
                                                        kwargs={'pk': instructor.pk}))
        self.assertEqual(get_delete_instructor.status_code, 200)
        self.assertTemplateUsed(get_delete_instructor, 'courseinfo/instructor_confirm_delete.html')
        post_delete_instructor = self.client.post(reverse('courseinfo_instructor_delete_urlpattern',
                                                          kwargs={'pk': instructor.pk}))
        self.assertEqual(post_delete_instructor.status_code, 302)
        self.assertRedirects(post_delete_instructor, reverse('courseinfo_instructor_list_urlpattern'))