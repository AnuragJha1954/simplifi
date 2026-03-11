from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import ChildProfile, ExpenseCategory, ChildWallet, FundRequest, AllowanceHistory
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()


@login_required
def add_child(request):

    if request.user.role != "parent":
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        age = request.POST.get("age")

        if User.objects.filter(username=username).exists():
            return redirect("add_child")

        child_user = User.objects.create_user(
            username=username,
            password=password,
            role="child"
        )

        child_profile = ChildProfile.objects.create(
            parent=request.user,
            child_user=child_user,
            age=age
        )

        ChildWallet.objects.create(
            child=child_profile
        )

       

        return redirect("children_list")

    return render(request, "children/add_child.html")




@login_required
def children_list(request):

    if request.user.role != "parent":
        return redirect("dashboard_home")

    children = ChildProfile.objects.filter(
        parent=request.user
    ).prefetch_related("fund_requests")

    requests = FundRequest.objects.filter(
        child__parent=request.user,
        status="pending"
    ).select_related("child", "category")

    return render(
        request,
        "children/children_list.html",
        {
            "children": children,
            "requests": requests
        }
    )




@login_required
def edit_child(request, child_id):

    child = get_object_or_404(
        ChildProfile,
        id=child_id,
        parent=request.user
    )

    if request.method == "POST":

        age = request.POST.get("age")

        child.age = age
        child.save()

        

        return redirect("children_list")

    return render(
        request,
        "children/edit_child.html",
        {"child": child}
    )







@login_required
def deactivate_child(request, child_id):

    child = get_object_or_404(
        ChildProfile,
        id=child_id,
        parent=request.user
    )

    child.is_active = False
    child.child_user.is_active = False

    child.child_user.save()
    child.save()

    

    return redirect("children_list")





@login_required
def child_dashboard(request):

    child_profile = request.user.child_profile

    categories = child_profile.categories.all()
    fund_requests = child_profile.fund_requests.all()

    total_allowance = sum(
        category.allocated_amount for category in categories
    )

    success = None

    if request.method == "POST":

        category_id = request.POST.get("category")
        amount = Decimal(request.POST.get("amount"))
        reason = request.POST.get("reason")

        FundRequest.objects.create(
            child=child_profile,
            category_id=category_id,
            amount=amount,
            reason=reason
        )

        success = "Your request was sent to your parent!"

    return render(
        request,
        "children/child_dashboard.html",
        {
            "categories": categories,
            "wallet_total": total_allowance,
            "fund_requests": fund_requests,
            "success": success
        }
    )




@login_required
@login_required
def manage_allowance(request, child_id):

    if request.user.role != "parent":
        return redirect("dashboard_home")

    child = get_object_or_404(
        ChildProfile,
        id=child_id,
        parent=request.user
    )

    if request.method == "POST":

        name = request.POST.get("category")
        amount = Decimal(request.POST.get("amount"))

        category = ExpenseCategory.objects.create(
            child=child,
            name=name,
            allocated_amount=amount
        )

        # Log history
        AllowanceHistory.objects.create(
            child=child,
            category=category,
            amount=amount,
            action="added",
            note="Parent added allowance"
        )

        return redirect("manage_allowance", child_id=child.id)

    categories = child.categories.all()

    total_allocated = categories.aggregate(
        total=Sum("allocated_amount")
    )["total"] or 0

    return render(
        request,
        "children/manage_allowance.html",
        {
            "child": child,
            "categories": categories,
            "total_allocated": total_allocated
        }
    )





@login_required
def edit_allowance(request, category_id):

    category = get_object_or_404(ExpenseCategory, id=category_id)

    if request.user != category.child.parent:
        return redirect("dashboard_home")

    if request.method == "POST":

        new_amount = Decimal(request.POST.get("amount"))

        wallet = category.child.wallet

        wallet.total_allocated -= category.allocated_amount
        wallet.total_allocated += new_amount
        wallet.save()

        category.allocated_amount = new_amount
        category.save()

        

        return redirect("manage_allowance", child_id=category.child.id)

    return render(
        request,
        "children/edit_allowance.html",
        {"category": category}
    )





@login_required
def child_allowances(request):

    if request.user.role != "child":
        return redirect("dashboard_home")

    child_profile = request.user.child_profile

    categories = child_profile.categories.all()

    total_allowance = categories.aggregate(
        total=Sum("allocated_amount")
    )["total"] or 0

    fund_requests = child_profile.fund_requests.all()

    return render(
        request,
        "children/child_allowances.html",
        {
            "categories": categories,
            "wallet_total": total_allowance,
            "fund_requests": fund_requests
        }
    )





@login_required
def request_funds(request):

    if request.user.role != "child":
        return redirect("dashboard_home")

    child = request.user.child_profile

    categories = child.categories.all()

    if request.method == "POST":

        category_id = request.POST.get("category")
        amount = Decimal(request.POST.get("amount"))
        reason = request.POST.get("reason")

        FundRequest.objects.create(
            child=child,
            category_id=category_id,
            amount=amount,
            reason=reason
        )

       

        return redirect("request_funds")

    requests = child.fund_requests.all().order_by("-created_at")

    return render(
        request,
        "children/request_funds.html",
        {
            "categories": categories,
            "requests": requests
        }
    )







@login_required
def parent_requests(request):

    if request.user.role != "parent":
        return redirect("dashboard_home")

    requests = FundRequest.objects.filter(
        child__parent=request.user
    ).select_related("child", "category")

    return render(
        request,
        "children/parent_requests.html",
        {
            "requests": requests
        }
    )





@login_required
def review_request(request, request_id):

    req = get_object_or_404(FundRequest, id=request_id)

    if request.user != req.child.parent:
        return redirect("dashboard_home")

    if request.method == "POST":

        action = request.POST.get("action")
        note = request.POST.get("note")

        req.parent_note = note
        req.reviewed_at = timezone.now()

        if action == "approve":

            req.status = "approved"

            category = req.category
            category.allocated_amount += req.amount
            category.save()

        else:
            req.status = "rejected"

        req.save()


        return redirect("parent_requests")

    return render(
        request,
        "children/review_request.html",
        {"req": req}
    )




@login_required
def parent_children_dashboard(request):

    if request.user.role != "parent":
        return redirect("child_dashboard")

    children = ChildProfile.objects.filter(
        parent=request.user
    ).prefetch_related("categories", "fund_requests")

    children_data = []

    total_children = children.count()
    total_allowance = 0
    total_pending_requests = 0

    for child in children:

        categories = child.categories.all()

        total = categories.aggregate(
            total=Sum("allocated_amount")
        )["total"] or 0

        total_allowance += total

        pending_requests = child.fund_requests.filter(
            status="pending"
        ).count()

        total_pending_requests += pending_requests

        # Create percentage bars
        category_bars = []
        for cat in categories:

            percent = 0
            if total > 0:
                percent = (cat.allocated_amount / total) * 100

            category_bars.append({
                "name": cat.name,
                "amount": cat.allocated_amount,
                "percent": percent
            })

        children_data.append({
            "child": child,
            "total": total,
            "categories": category_bars,
            "pending_requests": pending_requests
        })

    return render(
        request,
        "children/parent_dashboard.html",
        {
            "children_data": children_data,
            "total_children": total_children,
            "total_allowance": total_allowance,
            "total_pending_requests": total_pending_requests
        }
    )






@login_required
def reset_child_password(request, child_id):

    child = get_object_or_404(
        ChildProfile,
        id=child_id,
        parent=request.user
    )

    success = None

    if request.method == "POST":

        new_password = request.POST.get("password")

        user = child.child_user
        user.set_password(new_password)
        user.save()

        success = "Password updated successfully"

    return render(
        request,
        "children/reset_password.html",
        {
            "child": child,
            "success": success
        }
    )




@login_required
def approve_request(request, request_id):

    req = get_object_or_404(
        FundRequest,
        id=request_id,
        child__parent=request.user
    )

    req.status = "approved"
    req.reviewed_at = timezone.now()

    category = req.category
    category.allocated_amount += req.amount
    category.save()

    req.save()

    # Log history
    AllowanceHistory.objects.create(
        child=req.child,
        category=req.category,
        amount=req.amount,
        action="request_approved",
        note=req.reason
    )

    return redirect("children_list")


@login_required
def reject_request(request, request_id):

    req = get_object_or_404(
        FundRequest,
        id=request_id,
        child__parent=request.user
    )

    req.status = "rejected"
    req.reviewed_at = timezone.now()
    req.save()

    # Log history
    AllowanceHistory.objects.create(
        child=req.child,
        category=req.category,
        amount=req.amount,
        action="request_rejected",
        note=req.reason
    )

    return redirect("children_list")





@login_required
def delete_child(request, child_id):

    if request.user.role != "parent":
        return redirect("dashboard_home")

    child = get_object_or_404(
        ChildProfile,
        id=child_id,
        parent=request.user
    )

    user = child.child_user

    child.delete()
    user.delete()

    return redirect("children_list")




@login_required
def child_settings(request):

    if request.user.role != "child":
        return redirect("dashboard_home")

    child_profile = request.user.child_profile

    success = None

    if request.method == "POST":

        age = request.POST.get("age")

        child_profile.age = age
        child_profile.save()

        success = "Profile updated"

    return render(
        request,
        "children/child_settings.html",
        {
            "child": child_profile,
            "success": success
        }
    )



@login_required
def allowance_history(request):

    if request.user.role != "parent":
        return redirect("dashboard_home")

    history = AllowanceHistory.objects.filter(
        child__parent=request.user
    ).select_related("child", "category").order_by("-created_at")

    return render(
        request,
        "children/allowance_history.html",
        {
            "history": history
        }
    )


