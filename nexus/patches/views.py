from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from core.views import restrict_to_http_methods, restrict_to_groups

from users.models import (
    NexusUser,
    Positions,
    PositionChoices,
)

from core.models import (
    Semester,
    CourseSubject,
    Course,
    Faculty,
    Classes,
)

from payrolls.models import (
    Payroll,
    PayrollNotInHR,
    PayrollNotSigned,
    PayrollStatus,
)

from shifts.models import (
    get_weekend,
    Shift,
    ShiftKind,
    DropRequest,
)

from .forms import (
    loadUsersForm,
    loadPositionsForm,
    loadCoursesForm,
    loadFacultiesForm,
    loadClassesForm,
    loadTutorRoleForm,
)

from tutors.models import (
    TutorRoleInfo,
)

@login_required
@restrict_to_groups('Tech')
def load_users(request):
    if request.method == 'POST':
        form = loadUsersForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_users_response.html', context={'success': False})
        with open("temp/users.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        return render(request, 'load_users_response.html', context={'success': True})
    form = loadUsersForm()
    context = {'form': form}
    return render(request, 'load_users.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_user_from_line(request, line_number):
    with open("temp/users.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_user_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        if len(values) != 3:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                email = values[0].lower()
                first_name = values[1].title()
                if first_name[0] == '"':
                    first_name = first_name[1:-2]
                last_name = values[2].title()
                if last_name[0] == '"':
                    last_name = last_name[1:-2]
                user = NexusUser.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_unusable_password()
                user.save()
                content += f"<b>==User Added Successfully==</b>"
            except:
                content += f"<b>==Error Occoured On Line {line_number}, User Not Added==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_groups('Tech')
def load_positions(request):
    if request.method == 'POST':
        form = loadPositionsForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_positions_response.html', context={'success': False})
        with open("temp/positions.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        data = form.cleaned_data
        return render(request, 'load_positions_response.html', context={'success': True, 'position': data['position']})
    form = loadPositionsForm()
    context = {'form': form}
    return render(request, 'load_positions.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_position_from_line(request, line_number, position):
    with open("temp/positions.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_position_from_line', kwargs={'line_number': line_number+1, 'position': position})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        if len(values) != 2:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                email = values[0].lower()
                hourly_pay = float(values[1])
                user = NexusUser.objects.get(email=email)
                Positions.objects.create(
                    user=user,
                    semester=Semester.objects.get_active_semester(),
                    position=position,
                    hourly_pay=hourly_pay,
                )
                content += f"<b>==Position Added Successfully==</b>"
            except Exception as e:
                content += f"<b>==Error Occoured On Line {line_number}, Position Not Added: {e}==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_groups('Tech')
def load_courses(request):
    if request.method == 'POST':
        form = loadCoursesForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_courses_response.html', context={'success': False})
        with open("temp/courses.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        data = form.cleaned_data
        return render(request, 'load_courses_response.html', context={'success': True})
    form = loadCoursesForm()
    context = {'form': form}
    return render(request, 'load_courses.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_course_from_line(request, line_number):
    with open("temp/courses.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_course_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        if len(values) != 3:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                couse_subject_short_name = values[0].upper()
                number = values[1]
                course_name = values[2]
                course_subject = CourseSubject.objects.get(short_name=couse_subject_short_name)
                Course.objects.create(
                    subject=course_subject,
                    number=number,
                    name=course_name,
                    is_cross_listed=False,
                    main_course=None,
                )
                content += f"<b>==Position Added Successfully==</b>"
            except Exception as e:
                content += f"<b>==Error Occoured On Line {line_number}, Position Not Added: {e}==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)
    
@login_required
@restrict_to_groups('Tech')
def load_faculties(request):
    if request.method == 'POST':
        form = loadFacultiesForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_faculies_response.html', context={'success': False})
        with open("temp/faculties.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        return render(request, 'load_faculties_response.html', context={'success': True})
    form = loadFacultiesForm()
    context = {'form': form}
    return render(request, 'load_faculties.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_faculty_from_line(request, line_number):
    with open("temp/faculties.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_faculty_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        if len(values) != 3:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                first_name = values[0].title()
                last_name = values[1].title()
                email = values[2].lower()
                Faculty.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                content += f"<b>==User Added Successfully==</b>"
            except Exception as e:
                content += f"<b>==Error Occoured On Line {line_number}, Faculty Not Added: {e}==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_groups('Tech')
def load_classes(request):
    if request.method == 'POST':
        form = loadClassesForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_classes_response.html', context={'success': False})
        with open("temp/classes.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        return render(request, 'load_classes_response.html', context={'success': True})
    form = loadClassesForm()
    context = {'form': form}
    return render(request, 'load_classes.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_class_from_line(request, line_number):
    with open("temp/classes.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_class_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        if len(values) != 3:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                course_subject = values[0]
                number = values[1]
                email = values[2]
                course = Course.objects.get(subject__short_name=course_subject, number=number)
                faculty = Faculty.objects.get(email=email)
                sem = Semester.objects.get_active_semester()
                Classes.objects.create(
                    semester=sem,
                    course=course,
                    faculty=faculty,
                )
                content += f"<b>==Class Added Successfully==</b>"
            except Exception as e:
                content += f"<b>==Error Occoured On Line {line_number}, Class Not Added: {e}==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_groups('Tech')
@restrict_to_http_methods('GET', 'POST')
def fix_payroll(request):
    if request.method == 'POST':
        print("Starting....")
        attended_shifts = Shift.objects.filter(position__semester=Semester.objects.get_active_semester(), attendance_info__attended=True).all()
        not_attended_shifts = Shift.objects.filter(position__semester=Semester.objects.get_active_semester(), attendance_info__attended=False).all()
        
        all_payroll = Payroll.objects.all()
        for payroll in all_payroll:
            payroll.status = PayrollStatus.NOT_IN_HR
            if PayrollNotSigned.objects.filter(payroll=payroll).exists():
                payroll.not_signed.delete()
            if PayrollNotInHR.objects.filter(payroll=payroll).exists():
                payroll.not_in_hr.delete()
            PayrollNotSigned.objects.create(payroll=payroll)
            PayrollNotInHR.objects.create(payroll=payroll)
            payroll.save()
        print("done-1")
        
        for shift in not_attended_shifts:
            payroll = Payroll.objects.get(
                position=shift.position,
                week_end=get_weekend(shift.start.date()),
            )
            start_weekday = shift.start.weekday()
            payroll.not_signed.total_hours += shift.duration
            if start_weekday == 6:
                payroll.not_signed.sunday_hours += shift.duration
            elif start_weekday == 0:
                payroll.not_signed.monday_hours += shift.duration
            elif start_weekday == 1:
                payroll.not_signed.tuesday_hours += shift.duration
            elif start_weekday == 2:
                payroll.not_signed.wednesday_hours += shift.duration
            elif start_weekday == 3:
                payroll.not_signed.thursday_hours += shift.duration
            elif start_weekday == 4:
                payroll.not_signed.friday_hours += shift.duration
            elif start_weekday == 5:
                payroll.not_signed.saturday_hours += shift.duration
            payroll.not_signed.save()
            payroll.save()
        print("done-2")
        
        for shift in attended_shifts:
            payroll = Payroll.objects.get(
                position=shift.position,
                week_end=get_weekend(shift.start.date()),
            )
            start_weekday = shift.start.weekday()
            payroll.not_in_hr.total_hours += shift.duration
            if start_weekday == 6:
                payroll.not_in_hr.sunday_hours += shift.duration
            elif start_weekday == 0:
                payroll.not_in_hr.monday_hours += shift.duration
            elif start_weekday == 1:
                payroll.not_in_hr.tuesday_hours += shift.duration
            elif start_weekday == 2:
                payroll.not_in_hr.wednesday_hours += shift.duration
            elif start_weekday == 3:
                payroll.not_in_hr.thursday_hours += shift.duration
            elif start_weekday == 4:
                payroll.not_in_hr.friday_hours += shift.duration
            elif start_weekday == 5:
                payroll.not_in_hr.saturday_hours += shift.duration
            payroll.not_in_hr.save()
            payroll.save()
        print("done.")
        return HttpResponse("DONE!")
        
    return render(request, 'fix_payroll.html')

@login_required
@restrict_to_groups('Tech')
@restrict_to_http_methods('GET', 'POST')
def delete_class_shifts(request):
    if request.method == 'POST':
        print("Starting....")
        shifts = Shift.objects.filter(position__semester=Semester.objects.get_active_semester(), kind=ShiftKind.CLASS).all()
        for shift in shifts:
            try:
                shift.delete()
            except:
                shift.force_delete_from_not_in_hr()
        print("done.")
        return HttpResponse("DONE!")
    return render(request, 'delete_class_shift.html')

@login_required
@restrict_to_groups('Tech')
@restrict_to_http_methods('GET', 'POST')
def load_tutor_roles(request):
    if request.method == 'POST':
        form = loadTutorRoleForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_tutor_roles_response.html', context={'success': False})
        with open("temp/tutor_roles.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        return render(request, 'load_tutor_roles_response.html', context={'success': True})
    form = loadTutorRoleForm()
    context = {'form': form}
    return render(request, 'load_tutor_roles.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_tutor_role_from_line(request, line_number):
    with open("temp/tutor_roles.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_tutor_role_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        if to_read[-1] == '\n':
            to_read = to_read[:-1]
        values = to_read.split(',')
        err_course = None
        try:
            first_name = values[0]
            last_name = values[1]
            courses = values[2:]
            sem = Semester.objects.get_active_semester()
            position = Positions.objects.get(
                user__first_name=first_name, 
                user__last_name=last_name, 
                semester=sem,
                position=PositionChoices.TUTOR,
            )
            role = TutorRoleInfo.objects.get_or_create(
                position=position,
            )[0]
            role.assigned_courses.clear()
            for course in courses:
                if course == '':
                    continue
                err_course = course
                info = course.split('-')
                subject = '-'.join(info[:-1])
                number = info[-1]
                course = Course.objects.get(subject__short_name=subject, number=number)
                role.assigned_courses.add(course)
            role.save()
            content += f"<b>==Tutor Role Added Successfully==</b>"
        except Exception as e:
            content += f"<b>==Error Occoured On Line {line_number}, Tutor Role Not Added: {e}=={err_course}</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Tech')
def delete_error_drop_req(request):
    dr = DropRequest.objects.get(id=1)
    dr.delete()
    return HttpResponse("DONE!")