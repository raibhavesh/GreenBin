# Import necessary modules from Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .form import RegisterCustomerForm  # ✅ FIXED IMPORT

User = get_user_model()

# View for customer registration
def register_customer(request):
    if request.method == "POST":
        form = RegisterCustomerForm(request.POST)
        if form.is_valid():
            # Save the form data, set custom user role, and redirect to login
            user_instance = form.save(commit=False)
            user_instance.username = user_instance.email
            user_instance.save()
            messages.success(request, "Account created. Please log in")
            return redirect("login")
        else:
            messages.warning(request, "Something went wrong. Please check form errors")
            print(form.errors)  # ✅ DEBUG: Print form errors in the terminal

    else:
        form = RegisterCustomerForm()

    return render(request, "accounts/register_customer.html", {"form": form})  # ✅ Re-render form to show errors


# View for user login
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect("/")
        else:
            messages.warning(request, "Invalid username or password")
    
    return render(request, "accounts/login.html")  # ✅ Removed unnecessary redirect to show errors


# View for user logout
def logout_user(request):
    logout(request)
    messages.success(request, "Active session ended. Log in to continue")
    return redirect("login")


def home(request):
    if request.user.is_authenticated:
        return render(request, "base.html")
    return redirect("login")
