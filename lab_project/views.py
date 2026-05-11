from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from patients.models import Patient
from orders.models import LabOrder, OrderLine
from labtests.models import LabTest, SampleCollection, TestCategory
from results.models import ResultEntry
from accounts.models import CustomUser


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponse("Access Denied: You do not have the required role.")
        return wrapper
    return decorator


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "This account is currently disabled.")
                return render(request, 'login.html')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('/dashboard/')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


@login_required
def dashboard_view(request):
    total_patients = Patient.objects.count()
    total_orders = LabOrder.objects.count()
    completed_reports = LabOrder.objects.filter(status=4).count()
    pending_collections = LabOrder.objects.filter(status=1).count()
    pending_in_lab = LabOrder.objects.filter(status=2).count()
    recent_patients = Patient.objects.order_by('-id')[:5]

    context = {
        'total_patients': total_patients,
        'total_orders': total_orders,
        'completed_reports': completed_reports,
        'pending_collections': pending_collections,
        'pending_in_lab': pending_in_lab,
        'recent_patients': recent_patients,
    }

    return render(request, 'dashboard.html', context)


@login_required
@role_required(['nurse', 'admin'])
def patient_register_view(request):
    if request.method == 'POST':
        from datetime import datetime, date
        mrn = request.POST.get('mrn')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth_str = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if not mrn or not first_name or not last_name or not phone_number or not date_of_birth_str or not address:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'patient_register.html')

        if Patient.objects.filter(mrn=mrn).exists():
            messages.error(request, f"Patient with MRN '{mrn}' already exists.")
            return render(request, 'patient_register.html')

        try:
            dob = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 0 or age > 150:
                messages.error(request, f"Calculated age ({age} years) is invalid. Must be between 0 and 150.")
                return render(request, 'patient_register.html')
        except ValueError:
            messages.error(request, "Invalid Date of Birth format.")
            return render(request, 'patient_register.html')

        Patient.objects.create(
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            phone_number=phone_number,
            date_of_birth=dob,
            address=address
        )

        messages.success(request, "Patient registered successfully!")
        return redirect('/patients/')

    return render(request, 'patient_register.html')


@login_required
@role_required(['nurse', 'physician', 'admin'])
def patient_list_view(request):
    patients_list = Patient.objects.all()
    paginator = Paginator(patients_list, 10)
    page_number = request.GET.get('page')
    patients = paginator.get_page(page_number)
    context = {
        'patients': patients
    }
    return render(request, 'patient_list.html', context)


@login_required
@role_required(['physician', 'admin', 'nurse'])
def order_entry_view(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        physician_id = request.POST.get('physician')
        priority = request.POST.get('priority')
        test_ids = request.POST.getlist('tests')
        clinical_notes = request.POST.get('clinical_notes')

        if not patient_id or not physician_id or not test_ids:
            messages.error(request, "Please fill in all required fields including tests.")
            return redirect('/orders/')

        patient = Patient.objects.get(id=patient_id)
        physician = CustomUser.objects.get(id=physician_id)

        order = LabOrder.objects.create(
            patient=patient,
            physician=physician,
            priority=priority,
            status=1,
            clinical_notes=clinical_notes
        )
        for test_id in test_ids:
            OrderLine.objects.create(order=order, assay_id=test_id)
        order.save()

        messages.success(request, "Lab order created successfully!")
        return redirect('/orders/')

    orders = LabOrder.objects.all()
    patients = Patient.objects.all()
    physicians = CustomUser.objects.filter(role='physician')
    tests = LabTest.objects.filter(status='active')

    context = {
        'orders': orders,
        'patients': patients,
        'physicians': physicians,
        'tests': tests,
    }

    return render(request, 'order_entry.html', context)

@login_required
@role_required(['phlebotomist', 'admin'])
def phlebotomist_worklist_view(request):
    if request.method == 'POST':
        order_id = request.POST.get('order')
        collected_by_id = request.POST.get('collected_by')
        condition = request.POST.get('condition')

        if not order_id or not collected_by_id or not condition:
            messages.error(request, "Please fill in all fields.")
            return redirect('/phlebotomist-worklist/')

        order = LabOrder.objects.get(id=order_id)
        collected_by = CustomUser.objects.get(id=collected_by_id)

        if order.status != 1:
            messages.error(request, f"Error: Order status is '{order.get_status_display()}'. You can only collect samples for 'Ordered' orders.")
            return redirect('/phlebotomist-worklist/')

        if SampleCollection.objects.filter(order=order).exists():
            messages.error(request, "Sample already collected for this order.")
            return redirect('/phlebotomist-worklist/')

        SampleCollection.objects.create(
            sample_id=f"SMP-{order.id}",
            order=order,
            collected_by=collected_by,
            sample_condition=condition,
            status='collected'
        )

        order.status = 2
        order.save()

        messages.success(request, "Sample collected successfully!")
        return redirect('/phlebotomist-worklist/')
    search_query = request.GET.get('search', '')
    status_query = request.GET.get('status', '')
    date_query = request.GET.get('date', '')

    orders = LabOrder.objects.filter(status=1).exclude(sample__isnull=False)
    samples = SampleCollection.objects.all()

    if search_query:
        orders = orders.filter(Q(patient__mrn__icontains=search_query) | Q(patient__first_name__icontains=search_query) | Q(patient__last_name__icontains=search_query))
        samples = samples.filter(Q(order__patient__mrn__icontains=search_query) | Q(order__patient__first_name__icontains=search_query) | Q(order__patient__last_name__icontains=search_query))

    if status_query:
        samples = samples.filter(status=status_query)

    if date_query:
        samples = samples.filter(collection_date__date=date_query)

    phlebotomists = CustomUser.objects.filter(role='phlebotomist')

    paginator = Paginator(samples, 10)
    page_number = request.GET.get('page')
    samples_page = paginator.get_page(page_number)

    context = {
        'orders': orders,
        'samples': samples_page,
        'phlebotomists': phlebotomists
    }

    return render(request, 'phlebotomist_worklist.html', context)


@login_required
@role_required(['technician', 'admin'])
def technician_worklist_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')

        if action == 'mark_in_lab':
            order = LabOrder.objects.get(id=order_id)
            if order.status != 2:
                messages.error(request, f"Error: Order status is '{order.get_status_display()}'. Can only mark 'In-Lab' if sample has been collected.")
                return redirect('/technician-worklist/')
            order.status = 3
            order.save()
            messages.success(request, f"Order #{order_id} successfully received In-Lab for processing.")
            return redirect('/technician-worklist/')

        elif action == 'enter_results':
            order = LabOrder.objects.get(id=order_id)
            if order.status != 3:
                messages.error(request, f"Error: Order status is '{order.get_status_display()}'. Can only enter results for 'In-Lab' orders.")
                return redirect('/technician-worklist/')

            for test in order.tests.all():
                val = request.POST.get(f'result_value_{test.id}')
                flag = request.POST.get(f'flag_{test.id}')
                remarks = request.POST.get(f'remarks_{test.id}')

                if val:
                    ResultEntry.objects.update_or_create(
                        order=order,
                        test=test,
                        defaults={
                            'entered_by': request.user,
                            'result_value': val,
                            'flag': flag,
                            'remarks': remarks,
                            'status': 'completed'
                        }
                    )

            order.status = 4
            order.save()
            messages.success(request, f"All results saved & order #{order_id} completed successfully.")
            return redirect('/technician-worklist/')

    collected_orders = LabOrder.objects.filter(status=2)
    processing_orders = LabOrder.objects.filter(status=3)
    results_list = ResultEntry.objects.filter(status='completed')

    paginator = Paginator(results_list, 10)
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)

    context = {
        'collected_orders': collected_orders,
        'processing_orders': processing_orders,
        'results': results
    }

    return render(request, 'technician_worklist.html', context)


@login_required
@role_required(['physician', 'nurse', 'admin'])
def lab_report_view(request):
    search_query = request.GET.get('search', '')
    orders = LabOrder.objects.filter(status=4)

    if search_query:
        orders = orders.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__mrn__icontains=search_query)
        ).distinct()

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    context = {
        'orders': orders_page
    }

    return render(request, 'lab_report.html', context)


@login_required
@role_required(['admin'])
def admin_tests_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_category':
            name = request.POST.get('name')
            if name:
                TestCategory.objects.get_or_create(name=name)
                messages.success(request, "Category created successfully.")

        elif action == 'create_assay':
            test_name = request.POST.get('test_name')
            test_code = request.POST.get('test_code')
            category_id = request.POST.get('category_id')
            sample_type = request.POST.get('sample_type')
            price = request.POST.get('price')
            turnaround_time = request.POST.get('turnaround_time')
            description = request.POST.get('description')

            if LabTest.objects.filter(test_code=test_code).exists():
                messages.error(request, f"Assay code '{test_code}' already exists.")
            else:
                cat = TestCategory.objects.get(id=category_id)
                LabTest.objects.create(
                    category=cat,
                    test_name=test_name,
                    test_code=test_code,
                    sample_type=sample_type,
                    price=price,
                    turnaround_time=turnaround_time,
                    description=description,
                    status='active'
                )
                messages.success(request, f"Assay '{test_name}' saved successfully.")

        elif action == 'toggle_assay':
            test_id = request.POST.get('test_id')
            test = LabTest.objects.get(id=test_id)
            test.status = 'inactive' if test.status == 'active' else 'active'
            test.save()
            messages.success(request, f"Status toggled successfully for {test.test_name}.")

        elif action == 'delete_assay':
            test_id = request.POST.get('test_id')
            LabTest.objects.filter(id=test_id).delete()
            messages.success(request, "Assay deleted successfully.")

        return redirect('/admin-tests/')

    search_query = request.GET.get('search', '')
    tests = LabTest.objects.all()
    if search_query:
        tests = tests.filter(Q(test_name__icontains=search_query) | Q(test_code__icontains=search_query))

    categories = TestCategory.objects.all()

    paginator = Paginator(tests, 10)
    page_number = request.GET.get('page')
    tests_page = paginator.get_page(page_number)

    context = {
        'tests': tests_page,
        'categories': categories
    }

    return render(request, 'admin_tests.html', context)


@login_required
@role_required(['admin'])
def admin_users_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_user':
            username = request.POST.get('username')
            password = request.POST.get('password')
            role = request.POST.get('role')
            phone = request.POST.get('phone_number')

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    phone_number=phone
                )
                messages.success(request, f"User '{username}' registered successfully.")

        elif action == 'toggle_user':
            staff_id = request.POST.get('staff_id')
            user = CustomUser.objects.get(id=staff_id)
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f"Account status toggled successfully for {user.username}.")

        return redirect('/admin-users/')

    users_list = CustomUser.objects.all().order_by('role')
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'users': users
    }

    return render(request, 'admin_users.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')