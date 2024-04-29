from django.urls import path
from dashboard import views


urlpatterns = [
    path('home/', views.dashboard, name='dashboard'),
    path("createcustomer/", views.createcustomer, name="createcustomer"),
    path("add_order/<int:dataid>/", views.add_order, name="add_order"),
    path("edit_order/<int:dataid>/", views.edit_order, name="edit_order"),
    path("update_add_order/<int:dataid>/", views.update_add_order, name="update_add_order"),
    path("save_add_order/", views.save_add_order, name="save_add_order"),
    path("addtailors/", views.addtailors, name="addtailors"),
    path("save_tailor/", views.save_tailor, name="save_tailor"),
    path('select_dates/', views.select_dates, name='select_dates'),
    path('tailor_work_details/', views.tailor_work_details, name='tailor_work_details'),
    path('tailor_appointments/', views.tailor_appointments, name='tailor_appointments'),
    path('search_tailor/', views.search_tailor, name='search_tailor'),
    path("view_tailors/", views.tailor_details, name="view_tailors"),
    path("additems/", views.additems, name="additems"),
    path("additem/<int:dataid>/", views.additem, name="additem"),
    path("save_items/", views.save_items, name="save_items"),
    path("customer_details/", views.customer_details, name="customer_details"),
    path("order_details/", views.order_details, name="order_details"),
    path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),
    path("edit_customer/<int:dataid>/", views.edit_customer, name="edit_customer"),
    path("update_customer/<int:dataid>/", views.update_customer, name="update_customer"),
    path("search_mobile/", views.search_mobile, name="search_mobile"),
    
    # path("login_auth/",views.login_auth,name="login_auth"),
    path("adminlogin/", views.adminlogin, name='adminlogin'),
    path("savelogin/", views.savelogin, name='savelogin'),
    path("LogoutAdmin/", views.LogoutAdmin, name="LogoutAdmin"),
    path("LogoutReception/", views.LogoutReception, name="LogoutReception"),
    path('check_tailor_works/', views.check_tailor_works, name='check_tailor_works'),
    path('fetch_tailor_options/', views.fetch_tailor_options, name='fetch_tailor_options'),
    path('customer_bill/<int:customer_id>/', views.customer_bill, name='customer_bill'),

    path("upcoming_deliveries/", views.upcoming_deliveries, name="upcoming_deliveries"),

    path("customerdlt/<int:dlt>/", views.customerdlt, name="customerdlt"),
    path("orderdlt/<int:dlt>/", views.orderdlt, name="orderdlt"),
    path("savecustomer/", views.savecustomer, name="savecustomer"),
    # path("save_tailor/",views.save_tailor,name="save_tailor"),
    path('generate_pdf/<int:customer_id>/', views.print_measurement, name='generate_pdf'),
    path('customer_list/', views.all_customers, name='customer_list'),
    # path('customer_history/', views.customer_history, name='customer_history'),
    # path('cus_history_view/', views.cus_history_view, name='cus_history_view'),
    path('edit_tailor/<int:dataid>/', views.edit_tailor, name='edit_tailor'),
    path("updatetailor/<int:dataid>/", views.updatetailor, name='updatetailor'),
    path('delete_tailor/<int:dataid>/', views.delete_tailor, name='delete_tailor'),
    path('single_customer/<int:customer_id>/', views.single_customer, name='single_customer'),

#API LINKS

    path('tailor/<int:tailor_id>/order/<int:id>/inprogress-to-completed/', views.InProgressToCompletedAPIView.as_view(),
         name='inprogress_to_completed'),

    path('tailor/login/', views.TailorLoginView.as_view(), name='tailor-login'),
    path('tailor/<int:tailor_id>/assigned_works/', views.TailorAssignedWorksAPIView.as_view(),
         name='tailor-assigned-works'),
    path('tailor/<int:tailor_id>/completed-works/', views.CompletedOrderListAPIView.as_view(),
         name='completed_works_list'),

    path('order/<int:order_id>/items/', views.ItemListAPIView.as_view(), name='item_list'),

    path('tailor/<int:tailor_id>/inprogress-works/', views.InProgressWorksAPIView.as_view(), name='inprogress-works'),
        path('tailor/<int:tailor_id>/order/<int:id>/inprogress/', views.AssignedToInProgressAPIView.as_view(),
         name='assigned-to-inprogress'),

]
