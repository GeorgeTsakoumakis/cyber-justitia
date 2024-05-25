from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, ProfessionalUser
from chatbot.models import Session
from .forms import (
    UpdateDetailsForm,
    UpdatePasswordForm,
    DeactivateAccountForm,
    UpdateDescriptionForm,
    UpdateFlairForm,
)


def anonymous_required(redirect_url):
    """
    Decorator for views that allow only unauthenticated users to access view.
    Usage:
    @anonymous_required(redirect_url='company_info')
    def homepage(request):
        return render(request, 'homepage.html')

    :param redirect_url: URL to redirect to if user is authenticated
    Adapted from https://gist.github.com/m4rc1e/b28cfc9d24c3c2c47f21f2b89cffda86
    """

    def _wrapped(view_func, *args, **kwargs):
        def check_anonymous(request, *args, **kwargs):
            view = view_func(request, *args, **kwargs)
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view

        return check_anonymous

    return _wrapped


def index(request):
    """Renders the index page"""
    return render(request, "index.html")


@anonymous_required(redirect_url="chatbot/")
def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        user_type = request.POST["user_type"]
        try:
            flair = request.POST["flair"]
        except:
            flair = None

        try:
            validate_password(password)
        except Exception as e:
            messages.info(request, "Password not strong enough")
            return redirect("register")

        if password != password2:
            messages.info(request, "Password not matching")
            return redirect("register")

        is_professional = False
        if user_type == "standard":
            is_professional = False
            flair = None
        elif user_type == "professional":
            is_professional = True

        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, "Username already exists")
            return redirect("register")
        elif CustomUser.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            return redirect("register")
        else:
            # Save user to database
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.save()
            if is_professional:
                prof = ProfessionalUser(user=user, flair=flair)
                prof.save()
            return redirect("login")

    return render(request, "register.html")


@anonymous_required(redirect_url="chatbot/")
def login(request):
    """Handles the login form"""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            session_ids = Session.objects.filter(user=user).values_list(
                "session_id", flat=True
            )
            request.session["session_ids"] = list(session_ids)
            return redirect("chatbot/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("login")

    return render(request, "login.html")


@login_required
def dashboard(request):
    """
    Handles all POST requests from the dashboard page.

    Depending on the action in the POST request, different functions are called
    to handle the respective form submissions (update details, change password,
    deactivate account, update description)."""
    # Initialize forms with the current user's data
    update_details_form = UpdateDetailsForm(instance=request.user)
    update_password_form = UpdatePasswordForm(instance=request.user)
    deactivate_account_form = DeactivateAccountForm(instance=request.user)
    update_description_form = UpdateDescriptionForm(instance=request.user)
    update_flair_form = UpdateFlairForm(instance=request.user)

    if request.method == "POST":
        if "update_details" in request.POST:
            return update_details(request)
        elif "change_password" in request.POST:
            return change_password(request)
        elif "deactivate_account" in request.POST:
            return deactivate_account(request)
        elif "update_description" in request.POST:
            return update_description(request)
        elif "update_flair" in request.POST:
            return update_flair(request)

    # Pass the forms to the context for rendering in the template
    context = {
        "update_details_form": update_details_form,
        "update_password_form": update_password_form,
        "deactivate_account": deactivate_account_form,
        "update_description_form": update_description_form,
        "update_flair_form": update_flair_form,
    }

    return render(request, "dashboard.html", context)


@login_required()
def deactivate_account(request):
    """
    Deactivates the user's account.

    If the form is valid and the 'deactivate_profile' checkbox is checked,
    the user's account is set to inactive, and the user is redirected to the index page
    with a success message.
    """
    if request.method == "POST":
        # creates a form instance and populates it with data from the request
        form = DeactivateAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            # Check if the 'deactivate_profile' checkbox was checked in the form
            if form.cleaned_data["deactivate_profile"]:
                request.user.is_active = False
                request.user.save()
                messages.success(request, "Account deactivated successfully")
                return redirect("index")
        else:
            return render(request, "dashboard.html", {"deactivate_account_form": form})
    return redirect("dashboard")


@login_required
def change_password(request):
    """
    Handles the change password form submission.

    If the form is valid, the user's password is updated, the user is kept logged in,
    and a success message is displayed. The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        form = UpdatePasswordForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Password updated successfully")
            # Keep the user logged in
            auth.login(request, request.user)
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"change_password_form": form})
    return redirect("dashboard")


@login_required
def update_details(request):
    """
    Handles the update details form submission.

    If the form is valid, the user's details are updated, and a success message is displayed.
    The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        form = UpdateDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Details updated successfully")
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"update_details_form": form})
    return redirect("dashboard")


@login_required
def update_description(request):
    """
    Handles the update description form submission.

    If the form is valid, the user's description is updated, and a success message is displayed.
    The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        form = UpdateDescriptionForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Description updated successfully")
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"update_description_form": form})


@login_required
def update_flair(request):
    """
    Handles the update flair form submission.

    If the form is valid, the user's flair is updated, and a success message is displayed.
    The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        # Get the professional user profile if it exists, otherwise creates it
        profile, created = ProfessionalUser.objects.get_or_create(user=request.user)

        form = UpdateFlairForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Flair updated successfully")
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"update_flair_form": form})


@login_required
def logout(request):
    """Logs out the user"""
    request.session.pop("session_ids", None)
    auth.logout(request)
    return redirect("/")


@login_required
def profile(request):
    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email
    return render(
        request,
        "user_profile.html",
        {"first_name": first_name, "last_name": last_name, "email": email},
    )


def codeofconduct(request):
    """Renders the code of conduct page"""
    return render(request, "codeofconduct.html")


def handler400(request, *args, **argv):
    """Custom error handlers bad request"""
    return render(request, "errors/400.html", status=400)


def handler403(request, *args, **argv):
    """Custom error handlers forbidden"""
    return render(request, "errors/403.html", status=403)


def handler404(request, *args, **argv):
    """Custom error handlers not found"""
    return render(request, "errors/404.html", status=404)


def handler500(request, *args, **argv):
    """Custom error handlers server error"""
    return render(request, "errors/500.html", status=500)


def handler503(request, *args, **argv):
    """Custom error handlers service unavailable"""
    return render(request, "errors/503.html", status=503)
