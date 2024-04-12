import random
from datetime import date
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import UpdateAPIView, ListAPIView, \
    get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from xhtml2pdf import pisa

from dashboard.models import AddTailors, Customer, Item, Add_order
from .serializers import TailorLoginSerializer, \
    CompletedOrderSerializer, ItemSerializer, InProgressToCompletedSerializer, InProgressOrderSerializer, \
    UpdateToInProgressSerializer, AddOrderSerializer


# Create your views here.
def reception_indexpage(request):
    total_customers = Customer.objects.count()
    total_order = Add_order.objects.count()  # Assuming you have an Order model

    total_completed_works = AddTailors.objects.aggregate(Sum('completed_works'))['completed_works__sum']

    cus = Add_order.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    context = {'total_customers': total_customers, 'total_orders': total_order,
               'cus': cus,
               'total_completed_works': total_completed_works}

    return render(request, "reception_dashboard.html", context)


def search_mobile_recption(request):
    results = {'Customer': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']

        results['customer'] = Add_order.objects.filter(customer_id__mobile__icontains=query).exclude(customer_id__mobile__isnull=True).exclude(customer_id__mobile__exact='')

    return render(request, 'search_reception.html', {'results': results, 'query': query})


def customer_details_recption(request):
    cus = Customer.objects.all()
    return render(request, "Customer_details_reception.html", {"cus": cus})


def createcustomer_reception(request):
    tailor = AddTailors.objects.all()
    tailor_works = []
    for tailor in tailor:
        assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        pending_works = Add_order.objects.filter(tailor=tailor,status='in_progress').count()
        tailor_works.append({'tailor': tailor, 'assigned_works': assigned_works, 'pending_works': pending_works})

    context = {'tailor_works': tailor_works}
    return render(request, 'Create_customer_reception.html', context)


def check_tailor_works_recption(request):
    if request.method == 'GET':
        tailor_id = request.GET.get('tailor_id')
        delivery_date = request.GET.get('delivery_date')

        try:
            # Assuming you have a Customer model with a tailor field
            works = Add_order.objects.filter(tailor__id=tailor_id, delivery_date=delivery_date)

            # You may need to serialize the works data based on your requirements
            serialized_works = [{'name': work.name, 'other_field': work.other_field} for work in works]

            return JsonResponse({'works': serialized_works})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def fetch_tailor_options_recption(request):
    if request.method == 'GET' and 'delivery_date' in request.GET:
        delivery_date = request.GET.get('delivery_date')

        try:
            tailors = AddTailors.objects.all()
            tailor_options = []

            for tailor in tailors:
                try:
                    # Access the related set of Customer objects using customer_set
                    works_on_date = tailor.add_order_set.filter(delivery_date=delivery_date)

                    # Count assigned and pending works separately
                    assigned_works = works_on_date.filter(status='assigned').count()
                    pending_works = works_on_date.filter(status='pending').count()

                    tailor_options.append({
                        'id': tailor.id,
                        'name': tailor.tailor,
                        'assigned_works': assigned_works,
                        'pending_works': pending_works,
                    })
                except Exception as e:
                    print(f"Error processing tailor {tailor.id}: {str(e)}")

            return JsonResponse({'tailor_options': tailor_options})

        except Exception as e:
            # Print the error details to the console
            import traceback
            print(traceback.format_exc())

            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def savecustomer_recption(request):
    context = {}
    if request.method == "POST":
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')
        nc = request.POST.get('neck')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        ds = request.POST.get('other')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('Cloth')
        cs = request.POST.get('collar_size')
        sb = request.POST.get('sleeve_bottom')
        tp = request.POST.get('total')
        ap = request.POST.get('advance')
        bp = request.POST.get('balance')

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Customer.objects.filter(tailor=tailor_instance, delivery_date=dd).count()



        tailor_instance.assigned_works += 1
        tailor_instance.save()

        try:
            # Generate a unique bill_number sequentially
            last_bill_number = Add_order.objects.order_by('-bill_number').first()

            if last_bill_number:
                last_bill_chars = last_bill_number.bill_number[:1]  # Adjusted to extract only one character
                last_bill_digits = int(last_bill_number.bill_number[1:])  # Adjusted to start from index 1

                if last_bill_chars == 'Z' and last_bill_digits == 999:
                    raise ValueError("Cannot generate more bills")
                elif last_bill_digits == 999:
                    next_chars = string.ascii_uppercase[string.ascii_uppercase.index(last_bill_chars) + 1]
                    bill_number = f"{next_chars}A001"  # Reset to A001
                else:
                    bill_number = f"{last_bill_chars}{last_bill_digits + 1:03d}"  # Adjusted to pad with 3 digits
            else:
                bill_number = "A001"

            obj = Customer(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg, cuff_length=cl,
                           cuff_type=ct, sleeve_sada=sl, sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                           order_date=od, cloth=cloth, bill_number=bill_number,
                           delivery_date=dd, tailor=tailor_instance, button_type=bt,
                           collar=clr, description=ds,collar_size=cs,sleeve_bottom=sb)
            obj.save()

            add_order_obj = Add_order(customer_id=obj, length=ln, shoulder=sd, cloth=cloth, sleeve_sada=sl,
                                      sleeve_cuff=sll, neck=nc,  collar=clr, regal=rg, loose=lo,
                                       pocket=po, cuff_length=cl, bottom1=b1, seat=b2, button_type=bt,
                                      bill_number=bill_number,total_payment=tp,advance_payment=ap,balance_payment=bp,
                                      order_date=od, delivery_date=dd, tailor=tailor_instance, description=ds,collar_size=cs,sleeve_bottom=sb)
            add_order_obj.save()

            messages.success(request, "Successfully added customer" , {obj.name})
            return redirect(createcustomer_reception)

        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)

        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return redirect('customer_details_recption')


def all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})


def single_customer_reception(request, customer_id):
    single = Customer.objects.filter(id=customer_id)
    view_add_order = Add_order.objects.filter(customer_id=customer_id)
    itms = Item.objects.filter(customer_id=customer_id)
    return render(request, "single_customer_reception.html", {'single': single, 'itms': itms, 'view': view_add_order})


def tailor_details_recption(request):
    tailors = AddTailors.objects.all()

    for tailor in tailors:
        # Calculate assigned, pending, upcoming, and completed works
        tailor.assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        tailor.pending_works = Add_order.objects.filter(tailor=tailor, status='in_progress').count()
        tailor.upcoming_works = Add_order.objects.filter(tailor=tailor, delivery_date__gt=date.today()).count()
        tailor.completed_works = Add_order.objects.filter(tailor=tailor, status='completed').count()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor_reception.html', context)


# def additems_reception(request, dataid):
#     customers = Customer.objects.get(id=dataid)
#     return render(request, "Add_Items_reception.html", {"customers": customers})


def order_add_item(request, dataid):
    order = Add_order.objects.get(id=dataid)
    return render(request, "Add_Items_reception.html", {'order': order})


def save_items_recption(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderid')

        customer = request.POST.get('customerid')
        item_names = request.POST.getlist('itemName[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('price[]')

        order_instance = Add_order.objects.get(id=order_id)
        customer_instance = Customer.objects.get(id=customer)

        for i in range(len(item_names)):
            if i < len(quantities) and i < len(prices):
                item = Item(
                    order_id=order_instance,
                    customer=customer_instance,
                    item_name=item_names[i],
                    item_quantity=int(quantities[i]),
                    item_price=float(prices[i])
                )
                item.save()
            else:
                print(f"Skipping item at index {i} due to incomplete data.")

        return redirect('customer_details_recption')


def order_details_reception(request):
    cus = Add_order.objects.all().order_by('-id')
    if request.method == "POST":
        from_date_str = request.POST.get('textfield')
        to_date_str = request.POST.get('textfield2')

        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            data = Add_order.objects.filter(delivery_date__range=[from_date, to_date]).order_by('-id')
        else:
            data = Add_order.objects.all().order_by('-id')

        return render(request, "Order_Details_reception.html", {'cus': data})
    return render(request, "Order_Details_reception.html", {"cus": cus})


def deliver_order_reception(request, order_id):
    if request.method == 'POST':
        order = Add_order.objects.get(pk=order_id)
        order.pending_or_delivered = 'delivered'
        order.save()
        return redirect('reception_indexpage')

def add_order_recption(request, dataid):
    add = Customer.objects.get(id=dataid)
    return render(request, "Add_order_reception.html", {"add": add})


def edit_order_reception(request, dataid):
    add = Add_order.objects.get(id=dataid)
    return render(request, "edit_order_reception.html", {"add": add})


def update_add_order_reception(request, dataid):
    if request.method == "POST":
        # Your existing form processing logic
        id = request.POST.get('id')
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')
        nc = request.POST.get('neck')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('cloth')
        other = request.POST.get('other')
        cs = request.POST.get('collar_size')
        sb = request.POST.get('sleeve_bottom')
        tp = request.POST.get('total')
        ap = request.POST.get('advance')
        bp = request.POST.get('balance')

        # Get the existing customer
        customer = Add_order.objects.get(id=dataid)

        # Get the old tailor before updating
        old_tailor = customer.tailor

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()


        new_tailor = AddTailors.objects.get(id=tailor_id)

        # Update assigned_works for the old tailor and new tailor
        if old_tailor != new_tailor:
            old_tailor.assigned_works -= 1
            old_tailor.save()
            new_tailor.assigned_works += 1
            new_tailor.save()

        Add_order.objects.filter(id=dataid).update(length=ln, shoulder=sd, loose=lo, neck=nc,
                                                   regal=rg, cuff_length=cl, cuff_type=ct, sleeve_sada=sl,
                                                   sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                                                   cloth=cloth,total_payment=tp,advance_payment=ap,balance_payment=bp,
                                                   order_date=od, delivery_date=dd, tailor=new_tailor,
                                                   button_type=bt,collar_size=cs,sleeve_bottom=sb,
                                                    collar=clr, description=other)
        messages.success(request, "Customer Details Updated Successfully...!")
        return redirect(order_details_reception)


def save_add_order_recption(request):
    if request.method == "POST":
        id = request.POST.get('id')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')
        nc = request.POST.get('neck')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('cloth')
        other = request.POST.get('other')
        cs = request.POST.get('collar_size')
        sb = request.POST.get('sleeve_bottom')
        tp = request.POST.get('total')
        ap = request.POST.get('advance')
        bp = request.POST.get('balance')


        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        tailor_instance.assigned_works += 1
        tailor_instance.save()

        # Get or create the tailor instance
        customer_instance = Customer.objects.get(id=id)
        try:
            # Generate a unique bill_number sequentially
            last_bill_number = Add_order.objects.order_by('-bill_number').first()

            if last_bill_number:
                last_bill_chars = last_bill_number.bill_number[:1]  # Adjusted to extract only one character
                last_bill_digits = int(last_bill_number.bill_number[1:])  # Adjusted to start from index 1

                if last_bill_chars == 'Z' and last_bill_digits == 999:
                    raise ValueError("Cannot generate more bills")
                elif last_bill_digits == 999:
                    next_chars = string.ascii_uppercase[string.ascii_uppercase.index(last_bill_chars) + 1]
                    bill_number = f"{next_chars}A001"  # Reset to A001
                else:
                    bill_number = f"{last_bill_chars}{last_bill_digits + 1:03d}"  # Adjusted to pad with 3 digits
            else:
                bill_number = "A001"

            # Create the customer instance
            obj = Add_order(customer_id=customer_instance, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg,
                            cuff_length=cl, bill_number=bill_number,
                            cuff_type=ct, sleeve_sada=sl, sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                            order_date=od, cloth=cloth,total_payment=tp,advance_payment=ap,balance_payment=bp,
                            delivery_date=dd, tailor=tailor_instance, button_type=bt,
                            description=other, collar=clr,collar_size=cs,sleeve_bottom=sb)

            obj.save()

            messages.success(request, f"Successfully Added New Order {obj.customer_id.name}")

            return redirect('order_details_reception')
        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return redirect('order_details_reception')


def edit_customer_recption(request, dataid):
    ed = AddTailors.objects.all()
    cus = Customer.objects.get(id=dataid)
    return render(request, "edit_customer_reception.html", {"cus": cus, "ed": ed})


def update_customer_recption(request, dataid):
    if request.method == "POST":
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')
        nc = request.POST.get('neck')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        cloth = request.POST.get('cloth')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        other = request.POST.get('other')
        cs = request.POST.get('collar_size')
        sb = request.POST.get('sleeve_bottom')

        # Get the existing customer
        customer = Customer.objects.get(id=dataid)

        # Update the customer instance
        Customer.objects.filter(id=dataid).update(
            name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc,
            regal=rg, cuff_length=cl, cuff_type=ct, sleeve_sada=sl,
            sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2, cloth=cloth, button_type=bt,
             collar=clr, description=other,collar_size=cs,sleeve_bottom=sb
        )
        # Add_order.objects.filter(customer_id=dataid).update(length=ln, shoulder=sd, loose=lo, neck=nc,
        #                                                     regal=rg, cuff_length=cl, cuff_type=ct, sleeve_type=sl,
        #                                                     sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
        #                                                     cloth=cloth,
        #                                                     order_date=od, delivery_date=dd, tailor=new_tailor,
        #                                                     button_type=bt,
        #                                                     neck_round=ncr, wrist=wr, collar=clr, description=other)
        messages.success(request, "Customer Details Updated Successfully...! ")

    return redirect('customer_details_recption')


def customerdlt_recption(request, dlt):
    delt = Customer.objects.filter(id=dlt)
    delt.delete()
    return redirect(customer_details_recption)


def orderdlt_reception(request, dlt):
    delt = Add_order.objects.filter(id=dlt)
    id = Add_order.objects.get(id=dlt)
    id_dlt = id.tailor.id
    delt.delete()
    tailor_instance = AddTailors.objects.get(id=id_dlt)
    tailor_instance.assigned_works -= 1
    tailor_instance.save()
    return redirect(order_details_reception)


def tailor_work_details_recption(request):
    # Retrieve start_date and end_date from the POST request
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')

    # Convert start_date_str and end_date_str to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Get all tailors
    tailors = AddTailors.objects.all()

    # Initialize list to store tailor data
    tailor_data = []

    # Iterate through each tailor
    for tailor in tailors:
        # Filter customer orders for the tailor within the date range
        tailor_orders = Add_order.objects.filter(
            tailor=tailor,
            # order_date__gte=start_date,
            delivery_date__lte=end_date,
        )

        # Count the number of orders in each status for the tailor within the date range
        assigned_works = tailor_orders.filter(status='assigned').count()
        pending_works = tailor_orders.filter(status='in_progress').count()
        completed_works = tailor_orders.filter(status='completed').count()

        # Append tailor data to the list
        tailor_data.append({
            'tailor': tailor,
            'assigned_works': assigned_works,
            'pending_works': pending_works,
            'completed_works': completed_works,
        })

    # Pass the results to the template
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'tailor_data': tailor_data,
    }

    return render(request, 'tailor_details_reception.html', context)

    return render(request, 'tailor_work_reception.html')


def select_dates_recption(request):
    return render(request, "tailor_work_reception.html")


def customer_bill_reception(request, customer_id):
    order = Add_order.objects.filter(id=customer_id)
    item = Item.objects.filter(order_id=customer_id)

    return render(request, 'Print_measurements_r.html', {'order': order, 'item': item})


def print_measurement_reception(request, customer_id):
    customer = Add_order.objects.get(id=customer_id)

    context = {'customer': customer}

    template_path = 'Print_measurements_r.html'
    template = get_template(template_path)
    html = template.render(context)

    # Debugging: Print HcuTML to console
    print(html)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=measurement_{customer_id}.pdf'

    # Create PDF from HTML content
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response


# API


class TailorLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TailorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        print(f"Attempting to authenticate user: {username}")

        user = authenticate(request, username=username, password=password)

        try:
            user = AddTailors.objects.get(username=username, password=password)
        except AddTailors.DoesNotExist:
            user = None

        if user:
            print(f"Authentication successful for user: {username}")
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            response_data = {
                'message': 'Authentication successful',
                'status': True,
                'token': token,
                'user_id': user.id,
                'username': user.username,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print(f"Authentication failed for user: {username}")
            response_data = {
                'error': 'Invalid credentials',
                'status': False,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class TailorAssignedWorksAPIView(ListAPIView):
    serializer_class = AddOrderSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        return Add_order.objects.filter(tailor_id=tailor_id, status='assigned')


class AssignedToInProgressAPIView(UpdateAPIView):
    serializer_class = UpdateToInProgressSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        order_id = self.kwargs['id']
        return Add_order.objects.filter(tailor_id=tailor_id, id=order_id, status='assigned')

    def perform_update(self, serializer):
        # Retrieve the Add_order instance
        tailor_id = self.kwargs['tailor_id']
        order_id = self.kwargs['id']
        add_order_instance = get_object_or_404(Add_order, tailor_id=tailor_id, id=order_id, status='assigned')

        # Update the status to "in_progress"
        add_order_instance.status = 'in_progress'
        add_order_instance.save()

        # Update other related data or perform additional actions if needed

        # Update the pending works count for the tailor
        tailor_instance = get_object_or_404(AddTailors, id=tailor_id)

        # Decrease the pending works count, but ensure it doesn't go below 0
        if tailor_instance.pending_works > 0:
            tailor_instance.pending_works -= 1
        else:
            # If the pending works count is already 0, do not decrease it further
            tailor_instance.pending_works = 0

        tailor_instance.save()

        # Serialize the updated instance and return the response
        serialized_data = UpdateToInProgressSerializer(add_order_instance).data
        return Response(serialized_data, status=status.HTTP_200_OK)


class InProgressWorksAPIView(ListAPIView):
    serializer_class = InProgressOrderSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        return Add_order.objects.filter(tailor_id=tailor_id, status='in_progress')


class InProgressToCompletedAPIView(UpdateAPIView):
    serializer_class = InProgressToCompletedSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        order_id = self.kwargs['id']
        return Add_order.objects.filter(tailor_id=tailor_id, id=order_id, status='in_progress')

    def perform_update(self, serializer):
        # Retrieve the Add_order instance
        tailor_id = self.kwargs['tailor_id']
        order_id = self.kwargs['id']
        add_order_instance = get_object_or_404(Add_order, tailor_id=tailor_id, id=order_id, status='in_progress')

        # Update the status to "completed"
        add_order_instance.status = 'completed'
        add_order_instance.save()

        # Update other related data or perform additional actions if needed

        # Update the pending and completed works count for the tailor
        tailor_instance = get_object_or_404(AddTailors, id=tailor_id)

        # Check for negative values and handle them
        if tailor_instance.pending_works > 0:
            tailor_instance.pending_works -= 1
        else:
            tailor_instance.pending_works = 0

        tailor_instance.completed_works += 1
        tailor_instance.save()

        # Serialize the updated instance and return the response
        serialized_data = InProgressToCompletedSerializer(add_order_instance).data
        return Response(serialized_data, status=status.HTTP_200_OK)


class CompletedOrderListAPIView(ListAPIView):
    serializer_class = CompletedOrderSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        return Add_order.objects.filter(tailor_id=tailor_id, status='completed')


class ItemListAPIView(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return Item.objects.filter(order_id=order_id)
