from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from .models import CustomUser, ProfessionalUser, Education, Employments
from django.views.defaults import page_not_found
from chatbot.models import Session
from forum.models import Post, Comment
from .forms import (
    UpdateDetailsForm,
    UpdatePasswordForm,
    DeactivateAccountForm,
    UpdateDescriptionForm,
    UpdateFlairForm,
    UpdateEducationForm,
    UpdateEmploymentsFrom, BanForm,
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
    user = CustomUser.objects.get(username=request.user.username)
    if user.is_professional:
        professional_user = ProfessionalUser.objects.get(user=request.user)
        try:
            education = Education.objects.get(prof_id=professional_user)
        except Education.DoesNotExist:
            education = None
        try:
            employments = Employments.objects.get(prof_id=professional_user)
        except Employments.DoesNotExist:
            employments = None

        update_education_form = UpdateEducationForm(instance=education)
        update_employments_form = UpdateEmploymentsFrom(instance=employments)

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
        elif "update_education" in request.POST:
            return update_education(request)
        elif "update_employments" in request.POST:
            return update_employments(request)

    # Pass the forms to the context for rendering in the template
    if user.is_professional:
        context = {
            "update_details_form": update_details_form,
            "update_password_form": update_password_form,
            "deactivate_account": deactivate_account_form,
            "update_description_form": update_description_form,
            "update_flair_form": update_flair_form,
            "update_education_form": update_education_form,
            "update_employments_form": update_employments_form,
        }
    else:
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
def update_education(request):
    """
    Handles the update education form submission.

    If the form is valid, the user's education is updated, and a success message is displayed.
    The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        professional_user = ProfessionalUser.objects.get(user=request.user)
        try:
            # Try to get an existing Education instance
            education = Education.objects.get(prof_id=professional_user)
            # If an instance exists, create a form with the POST data and the existing instance
            form = UpdateEducationForm(request.POST, instance=education)
        except ObjectDoesNotExist:
            # If no instance exists, create a new form with the POST data
            form = UpdateEducationForm(request.POST)
        if form.is_valid():
            # Save the form data to the instance
            education = form.save(commit=False)
            education.prof_id = professional_user
            education.save()
            messages.success(request, "Education updated successfully")
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"update_education_form": form})


@login_required
def update_employments(request):
    """
    Handles the update employments form submission.

    If the form is valid, the user's employments are updated, and a success message is displayed.
    The user is then redirected to the dashboard.
    """
    if request.method == "POST":
        professional_user = ProfessionalUser.objects.get(user=request.user)
        try:
            # Try to get an existing Employment instance
            employment = Employments.objects.get(prof_id=professional_user)
            # If an instance exists, create a form with the POST data and the existing instance
            form = UpdateEmploymentsFrom(request.POST, instance=employment)
        except ObjectDoesNotExist:
            # If no instance exists, create a new form with the POST data
            form = UpdateEmploymentsFrom(request.POST)
        if form.is_valid():
            # Save the form data to the instance
            employment = form.save(commit=False)
            employment.prof_id = professional_user
            employment.save()
            messages.success(request, "Employment updated successfully")
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {"update_employments_form": form})


@login_required
def logout(request):
    """Logs out the user"""
    request.session.pop("session_ids", None)
    auth.logout(request)
    return redirect("/")


@login_required
def profile(request, username):
    """Renders the profile page at /profile/username"""
    user = CustomUser.objects.get(username=username)
    recent_posts = (
        Post.objects.filter(user=user)
        .filter(is_deleted=False)
        .order_by("-created_at")[:3]
    )
    recent_comments = (
        Comment.objects.filter(user=user)
        .filter(is_deleted=False)
        .order_by("-created_at")[:3]
    )
    context = {
        "viewed_user": user,
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
    }
    return render(request, "user_profile.html", context)


@login_required
def ban_user(request, username):
    """
    Bans a user from the platform. Only superusers can ban users.
    Banned users cannot access any part of the platform, including the chatbot and forum.
    :param request: Request object
    :param username: Username of the user to ban
    """
    if request.user.is_superuser:
        selected_user = get_object_or_404(CustomUser, username=username)
        if request.method == "POST":
            form = BanForm(request.POST, instance=selected_user)
            if form.is_valid():
                selected_user.is_banned = True
                selected_user.reason_banned = form.cleaned_data["reason_banned"]
                selected_user.save()
                messages.success(request, f"User {selected_user.username} has been banned")
                return redirect("profile", username=selected_user.username)
        else:
            form = BanForm(instance=selected_user)
        context = {"form": form, "selected_user": selected_user}
        return render(request, "banpage.html", context)
    else:
        # Return 403 Forbidden
        return render(request, "errors/403.html", status=403)


def codeofconduct(request):
    """Renders the code of conduct page"""
    return render(request, "codeofconduct.html")


def handler400(request, *args, **argv):
    """Custom error handlers bad request"""
    return render(request, "errors/400.html", status=400)


def handler403(request, *args, **argv):
    """Custom error handlers forbidden"""
    return render(request, "errors/403.html", status=403)


def handler404(request, exception):
    """Custom error handlers not found"""
    return page_not_found(request, exception, template_name="errors/404.html")


def handler500(request, *args, **argv):
    """Custom error handlers server error"""
    return render(request, "errors/500.html", status=500)


def handler503(request, *args, **argv):
    """Custom error handlers service unavailable"""
    return render(request, "errors/503.html", status=503)
