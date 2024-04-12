# from tailors.models import AddCustomer
import logging
import random
from datetime import date
import string
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from xhtml2pdf import pisa

from reception.views import reception_indexpage
from .models import AddTailors
from .models import Customer, Item, reception_login, admin_login, Add_order
from .serializers import TailorLoginSerializer, \
    CompletedOrderSerializer, ItemSerializer, InProgressToCompletedSerializer, InProgressOrderSerializer, \
    UpdateToInProgressSerializer, AddOrderSerializer


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


def indexpage(request):
    return render(request, "dashboard.html")


def createcustomer(request):
    tailor = AddTailors.objects.all()
    tailor_works = []
    for tailor in tailor:
        assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        pending_works = Add_order.objects.filter(tailor=tailor,status='in_progress').count()
        tailor_works.append({'tailor': tailor, 'assigned_works': assigned_works, 'pending_works': pending_works})

    context = {'tailor_works': tailor_works}
    return render(request, 'Create_customer.html', context)


def addtailors(request):
    return render(request, "Add_tailor.html")


def save_tailor(request):
    if request.method == "POST":
        tn = request.POST.get('tname')
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        mob = request.POST.get('mobile')

        # Check if a tailor with the given mobile number already exists
        if AddTailors.objects.filter(mobile_number=mob).exists():
            messages.error(request, "Mobile number already exists")
        else:
            try:
                obj = AddTailors(tailor=tn, username=un, password=pwd, mobile_number=mob)
                obj.save()
                messages.success(request, "Tailor Added Successfully")
            except IntegrityError:
                messages.error(request, "An error occurred while saving the tailor")

    return redirect('addtailors')


# def view_tailors(request):
#     return render(request, "View_Tailor.html")


def tailor_details(request):
    tailors = AddTailors.objects.all()

    for tailor in tailors:
        # Calculate assigned, pending, upcoming, and completed works
        tailor.assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        tailor.pending_works = Add_order.objects.filter(tailor=tailor, status='in_progress').count()
        tailor.upcoming_works = Add_order.objects.filter(tailor=tailor, delivery_date__gt=date.today()).count()
        tailor.completed_works = Add_order.objects.filter(tailor=tailor, status='completed').count()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor.html', context)


def additems(request, dataid):
    order = Add_order.objects.get(id=dataid)
    return render(request, "Add_items_admin.html", {"customers": order})


def additem(request, dataid):
    order = Add_order.objects.get(id=dataid)
    return render(request, "Add_Items.html", {'order': order})


def save_items(request):
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

        return redirect('customer_details')


def customer_details(request):
    cus = Customer.objects.all()
    return render(request, "Customer_details.html", {"cus": cus})


def order_details(request):
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

        return render(request, "Order_Details.html", {'cus': data})
    return render(request, "Order_Details.html", {"cus": cus})

def deliver_order(request, order_id):
    if request.method == 'POST':
        order = Add_order.objects.get(pk=order_id)
        order.pending_or_delivered = 'delivered'
        order.save()
        return redirect('order_details')


def upcoming_deliveries(request):
    cus = Customer.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    return render(request, 'dashboard.html', {'cus': cus})


def check_tailor_works(request):
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


def fetch_tailor_options(request):
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


def savecustomer(request):
    context = {}

    if request.method == "POST":
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')        
        center_sleeve = request.POST.get('center_sleeve')        
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        ds = request.POST.get('other')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('Cloth')
        sb = request.POST.get('sleeve_bottom')
        tp = request.POST.get('total')
        ap = request.POST.get('advance')
        bp = request.POST.get('balance')
        collar_type = request.POST.get('collar-type')
        cuff_type = request.POST.get('cuff-type')
        cuff_measurment = request.POST.get('cuff-measurements')
        collar_measurment = request.POST.get('collar-measurements')
        

        if collar_type == 'collar1':
            collar_image_url = 'images/collarcuff/collor 1.png'
        elif collar_type == 'collar2':
            collar_image_url = 'images/collarcuff/collor 2.png'
        elif collar_type == 'collar3':
            collar_image_url = 'images/collarcuff/collor 3.png'
        elif collar_type == 'collar4':
            collar_image_url = 'images/collarcuff/collor 4.png'
        else:
            collar_image_url = None 

        if cuff_type == 'cuff1':
            cuff_image_url = 'images/collarcuff/cuff 1.png'
        elif cuff_type == 'cuff2':
            cuff_image_url = 'images/collarcuff/cuff 2.png'
        elif cuff_type == 'cuff3':
            cuff_image_url = 'images/collarcuff/cuff 3.png'
        elif cuff_type == 'cuff4':
            cuff_image_url = 'images/collarcuff/cuff 4.png'
        elif cuff_type == 'cuff5':
            cuff_image_url = 'images/collarcuff/cuff 5.png'
        else:
            cuff_image_url = None 

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()


        tailor_instance.assigned_works += 1
        tailor_instance.save()

        try:
            # Generate a unique bill_number sequentially
            last_bill_number = Add_order.objects.order_by('-bill_number').first()

            if last_bill_number:
                last_bill_chars = last_bill_number.bill_number[:1]  # Extract the first character
                last_bill_digits = int(last_bill_number.bill_number[1:])  # Extract the digits

                if last_bill_chars == 'Z' and last_bill_digits == 999:
                    raise ValueError("Cannot generate more bills")
                elif last_bill_digits == 999:
                    next_chars = chr(ord(last_bill_chars) + 1)  # Increment the character
                    if next_chars > 'Z':  # Check if the next character exceeds 'Z'
                        raise ValueError("Cannot generate more bills")
                    bill_number = f"{next_chars}001"  # Reset digits to "001"
                else:
                    bill_number = f"{last_bill_chars}{last_bill_digits + 1:03d}"  # Increment digits
            else:
                bill_number = "A001"


            obj = Customer(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, regal=rg, collar_measurements=collar_measurment,
                           cuff_type_image_url=cuff_image_url, sleeve_sada=sl, sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                           order_date=od, cloth=cloth, delivery_date=dd, tailor=tailor_instance, button_type=bt,collar_type=collar_type,
                           cuff_type=cuff_type,collar_type_image_url=collar_image_url, description=ds, bill_number=bill_number,
                           cuff_measurements=cuff_measurment,sleeve_bottom=sb,center_sleeve=center_sleeve)
            obj.save()

            add_order_obj = Add_order(customer_id=obj, length=ln, shoulder=sd, loose=lo,regal=rg,
                                      cuff_measurements=cuff_measurment,collar_type_image_url=collar_image_url,
                                      cuff_type_image_url=cuff_image_url, collar_measurements=collar_measurment,
                                      collar_type=collar_type,cuff_type=cuff_type,center_sleeve=center_sleeve,
                                      sleeve_sada=sl, sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                                      order_date=od, cloth=cloth, delivery_date=dd, tailor=tailor_instance,
                                      button_type=bt,total_payment=tp,advance_payment=ap,balance_payment=bp,
                                      description=ds, bill_number=bill_number,sleeve_bottom=sb)
            add_order_obj.save()

            messages.success(request, "Successfully added customer")
            return redirect(createcustomer)
        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)


@api_view(['POST'])
def accept_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)

    # Update the pending works count
    tailor.pending_works += 1
    tailor.save()

    return Response({'status': 'Pending works updated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def complete_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)

    # Update the pending and completed works counts
    if tailor.pending_works > 0:
        tailor.pending_works -= 1
        tailor.completed_works += 1
        tailor.save()
        return Response({'status': 'Work completed successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'No pending works to complete'}, status=status.HTTP_400_BAD_REQUEST)


def customerdlt(request, dlt):
    delt = Customer.objects.filter(id=dlt)
    delt.delete()
    return redirect(customer_details)


def orderdlt(request, dlt):
    delt = Add_order.objects.filter(id=dlt)
    id = Add_order.objects.get(id=dlt)
    id_dlt = id.tailor.id
    delt.delete()
    tailor_instance = AddTailors.objects.get(id=id_dlt)
    tailor_instance.assigned_works -= 1
    tailor_instance.save()
    return redirect(order_details)


def dashboard(request):
    total_customers = Customer.objects.count()
    total_order = Add_order.objects.count()  # Assuming you have an Order model

    total_completed_works = AddTailors.objects.aggregate(Sum('completed_works'))['completed_works__sum']

    cus = Add_order.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    context = {'total_customers': total_customers, 'total_orders': total_order,
               'cus': cus,
               'total_completed_works': total_completed_works}

    return render(request, 'dashboard.html', context)


logger = logging.getLogger(__name__)


def customer_bill(request, customer_id):
    order = Add_order.objects.filter(id=customer_id)
    item = Item.objects.filter(order_id=customer_id)

    return render(request, 'Print_measurements.html', {'order': order, 'item': item})


def print_measurement(request, customer_id):
    customer = Add_order.objects.get(id=customer_id)

    context = {'customer': customer}

    template_path = 'Print_measurements.html'
    template = get_template(template_path)
    html = template.render(context)

    # Debugging: Print HTML to console
    print(html)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=measurement_{customer_id}.pdf'

    # Create PDF from HTML content
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response


# def tailor_details(request):
#     # tailors = AddTailors.objects.all()
#
#     context = {'tailors': tailors}
#     return render(request, 'View_Tailor.html', context)


def all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})


def edit_tailor(request, dataid):
    tail = AddTailors.objects.get(id=dataid)
    return render(request, "edit_tailor.html", {"tail": tail})


def updatetailor(request, dataid):
    if request.method == "POST":
        tn = request.POST.get('tname')
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        mob = request.POST.get('mobile')
        AddTailors.objects.filter(id=dataid).update(tailor=tn, username=un, password=pwd, mobile_number=mob)
        messages.success(request, "Tailor Details Updated Successfully...!")
    return redirect(tailor_details)


def delete_tailor(request, dataid):
    tailor = get_object_or_404(AddTailors, pk=dataid)

    # Add your logic for deleting tailor here
    tailor.delete()

    return redirect('view_tailors')


def edit_customer(request, dataid):
    ed = Customer.objects.all()
    cus = Customer.objects.get(id=dataid)
    return render(request, "edit_customer.html", {"cus": cus, "ed": ed})


def update_customer(request, dataid):
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
        messages.success(request, "Customer Details Updated Successfully...!")

    return redirect('customer_details')


def search_mobile(request):
    results = {'Customer': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']

        results['customer'] = Add_order.objects.filter(customer_id__mobile__icontains=query).exclude(customer_id__mobile__isnull=True).exclude(customer_id__mobile__exact='')

    return render(request, 'search.html', {'results': results, 'query': query})


def single_customer(request, customer_id):
    single = Customer.objects.filter(id=customer_id)
    view_add_order = Add_order.objects.filter(customer_id=customer_id)
    itms = Item.objects.filter(customer_id=customer_id)
    return render(request, "single_customer.html", {'single': single, 'itms': itms, 'view': view_add_order})


def add_order(request, dataid):
    add = Customer.objects.get(id=dataid)
    return render(request, "Add_order.html", {"add": add})


def edit_order(request, dataid):
    add = Add_order.objects.get(id=dataid)
    return render(request, "edit_order.html", {"add": add})


def update_add_order(request, dataid):
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
        #
        # if works_on_delivery_date >= 6:
        #     error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
        #     if request.is_ajax():
        #         return JsonResponse({'error': error_message}, status=400)
        #     else:
        #         messages.error(request, error_message)
        #         return redirect(order_details)
        #         Get or create the new tailor instance
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
                                                   button_type=bt,
                                                    collar=clr, description=other,sleeve_bottom=sb,collar_size=cs)

    messages.success(request, "Customer Details Updated Successfully...!")
    return redirect(order_details)


def save_add_order(request):
    if request.method == "POST":
        # Your existing form processing logic
        id = request.POST.get('id')
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve_sada')
        sll = request.POST.get('sleeve_cuff')
        center_sleeve = request.POST.get('center_sleeve')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('seat')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('cloth')
        other = request.POST.get('other')
        sb = request.POST.get('sleeve_bottom')
        tp = request.POST.get('total')
        ap = request.POST.get('advance')
        bp = request.POST.get('balance')
        collar_type = request.POST.get('collar-type')
        cuff_type = request.POST.get('cuff-type')
        cuff_measurment = request.POST.get('cuff-measurements')
        collar_measurment = request.POST.get('collar-measurements')
        

        if collar_type == 'collar1':
            collar_image_url = 'images/collarcuff/collor 1.png'
        elif collar_type == 'collar2':
            collar_image_url = 'images/collarcuff/collor 2.png'
        elif collar_type == 'collar3':
            collar_image_url = 'images/collarcuff/collor 3.png'
        elif collar_type == 'collar4':
            collar_image_url = 'images/collarcuff/collor 4.png'
        else:
            collar_image_url = None 

        if cuff_type == 'cuff1':
            cuff_image_url = 'images/collarcuff/cuff 1.png'
        elif cuff_type == 'cuff2':
            cuff_image_url = 'images/collarcuff/cuff 2.png'
        elif cuff_type == 'cuff3':
            cuff_image_url = 'images/collarcuff/cuff 3.png'
        elif cuff_type == 'cuff4':
            cuff_image_url = 'images/collarcuff/cuff 4.png'
        elif cuff_type == 'cuff5':
            cuff_image_url = 'images/collarcuff/cuff 5.png'
        else:
            cuff_image_url = None 


        # Get or create the tailor instance
        tailor_instance = AddTailors.objects.get(id=tailor_id)
        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        # if works_on_delivery_date >= 6:
        #     error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
        #     if request.is_ajax():
        #         return JsonResponse({'error': error_message}, status=400)
        #     else:
        #         messages.error(request, error_message)
        #         return redirect('createcustomer')

        tailor_instance.assigned_works += 1
        tailor_instance.save()

        # Get or create the tailor instance
        customer_instance = Customer.objects.get(id=id)
        try:
            # Get the last bill number from the database
            last_bill_number = Add_order.objects.order_by('-bill_number').first()
            # Generate the next bill number
            last_bill_chars = last_bill_number[:1]  # Extract the first character
            last_bill_digits = int(last_bill_number[-3:])  # Extract the digits
            print(last_bill_digits)
            if last_bill_chars == 'Z' and last_bill_digits == 999:
                next_chars = 'AA'  # Reset to 'AA'
                next_digits = '001'  # Reset to "001"
            elif last_bill_digits == 999:
                next_chars = chr(ord(last_bill_chars) + 1)  # Increment the character
                next_digits = '001'  # Reset to "001"
            else:
                next_chars = last_bill_chars
                next_digits = last_bill_digits + 1

            bill_number = f"{next_chars}{next_digits:03d}"  # Format the next bill number


tailor_management_system



            # Create the customer instance
            obj = Add_order(customer_id=customer_instance, length=ln, shoulder=sd, loose=lo, regal=rg,
                            bill_number=bill_number,
                            cuff_measurements=cuff_measurment,collar_type_image_url=collar_image_url,
                            cuff_type_image_url=cuff_image_url, collar_measurements=collar_measurment,
                            collar_type=collar_type,cuff_type=cuff_type,center_sleeve=center_sleeve,
                            sleeve_sada=sl, sleeve_cuff=sll, pocket=po, bottom1=b1, seat=b2,
                            order_date=od, cloth=cloth,total_payment=tp,advance_payment=ap,balance_payment=bp,
                            delivery_date=dd, tailor=tailor_instance, button_type=bt,
                            description=other,sleeve_bottom=sb)

            obj.save()

            messages.success(request, f"Successfully added new order: {obj.customer_id.name}")
            return redirect('add_order', dataid=obj.customer_id.id)

        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return redirect(order_details)


def search_tailor(request):
    results = {'tailors': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']
        results['tailors'] = AddTailors.objects.filter(mobile_number__icontains=query)

    return render(request, 'search_tailor.html', {'results': results, 'query': query})


def tailor_work_details(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        tailors = AddTailors.objects.all()

        tailor_data = []
        for tailor in tailors:
            assigned_works = Add_order.objects.filter(
                tailor=tailor, status='assigned', order_date__range=[start_date, end_date]
            ).count()

            pending_works = Add_order.objects.filter(
                tailor=tailor, status='in_progress', order_date__range=[start_date, end_date]
            ).count()

            completed_works = Add_order.objects.filter(
                tailor=tailor, status='completed', order_date__range=[start_date, end_date]
            ).count()

            tailor_info = {
                'tailor': tailor,
                'assigned_works': assigned_works,
                'pending_works': pending_works,
                'completed_works': completed_works
            }

            tailor_data.append(tailor_info)

        context = {
            'tailor_data': tailor_data,
            'start_date': start_date,
            'end_date': end_date,
        }

        return render(request, 'tailor_details.html', context)

    return render(request, 'tailor_work.html')


def select_dates(request):
    return render(request, "tailor_work.html")


from datetime import datetime


def tailor_appointments(request):
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

    return render(request, 'tailor_details.html', context)


def login(request):
    return render(request, "login.html")


def savelogin(request):
    if request.method == "POST":
        un = request.POST.get('user_name')
        pd = request.POST.get('password')
        obj = admin_login(username=un, password=pd)
        obj.save()
        return render(savelogin)


def adminlogin(request):
    if request.method == "POST":
        un = request.POST.get('user_name')
        pwd = request.POST.get('password')
        if admin_login.objects.filter(username=un, password=pwd).exists():
            request.session['user_name'] = un
            request.session['password'] = pwd
            messages.success(request, " Login Successful")
            return redirect(dashboard)
        elif reception_login.objects.filter(user_name=un, password=pwd).exists():
            reception = reception_login.objects.get(user_name=un, password=pwd)
            request.session['username'] = un
            request.session['password'] = pwd
            messages.success(request, " Login Successful")
            return redirect(reception_indexpage)
        else:
            messages.warning(request, "Please Enter Valid username and password...")
            return redirect(login)

@never_cache
def LogoutAdmin(request):
    if 'user_name' in request.session:
        del request.session['user_name']
    if 'password' in request.session:
        del request.session['password']
    messages.success(request, 'Logout successful...!')
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
def LogoutReception(request):
    if 'username' in request.session:
        del request.session['username']
    if 'password' in request.session:
        del request.session['password']
    messages.success(request, 'Logout successful...!')
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

from django.contrib.auth.decorators import login_required
from django.utils.cache import add_never_cache_headers


@login_required
def some_protected_view(request):
    # Your view logic goes here
    # For example:
    # Your view logic...

    # Create the HTTP response
    response = HttpResponse()

    # Set cache-control headers to prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response
class NoCacheMiddleware:

    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response