from django.urls import path
from . import views


urlpatterns = [

    path("add/", views.add_child, name="add_child"),

    path("list/", views.children_list, name="children_list"),

    path("edit/<int:child_id>/", views.edit_child, name="edit_child"),

    path("deactivate/<int:child_id>/", views.deactivate_child, name="deactivate_child"),

    path("dashboard/", views.child_dashboard, name="child_dashboard"),
    
    path("allowance/<int:child_id>/",
         views.manage_allowance,
         name="manage_allowance"),

    path("allowance/edit/<int:category_id>/",
         views.edit_allowance,
         name="edit_allowance"),

    path("my-allowance/",
         views.child_allowances,
         name="child_allowances"),
    
    path(
        "request-funds/",
        views.request_funds,
        name="request_funds"
    ),

    path(
        "requests/",
        views.parent_requests,
        name="parent_requests"
    ),

    path(
        "review-request/<int:request_id>/",
        views.review_request,
        name="review_request"
    ),
    
    path(
        "overview/",
        views.parent_children_dashboard,
        name="parent_children_dashboard"
    ),
    
    
    path(
        "reset-password/<int:child_id>/",
        views.reset_child_password,
        name="reset_child_password"
    ),

    path(
        "approve-request/<int:request_id>/",
        views.approve_request,
        name="approve_request"
    ),

    path(
        "reject-request/<int:request_id>/",
        views.reject_request,
        name="reject_request"
    ),
    
    path(
        "delete-child/<int:child_id>/",
        views.delete_child,
        name="delete_child"
    ),
    
    path(
        "settings/",
        views.child_settings,
        name="child_settings"
    ),
    
    path(
        "allowance-history/",
        views.allowance_history,
        name="allowance_history"
    ),

]