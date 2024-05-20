from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, ProfessionalUser
from chatbot.models import Session
from .forms import UpdateDetailsForm, UpdatePasswordForm, DeactivateAccountForm


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
    # TODO: Add different POST forms for different actions based on prototype (frontend) and retrieve information here,
    #  redirect to appropriate functions to handle the actions
    # user = request.user
    # if request.method == 'POST':
    #     if 'delete' in request.POST and request.POST['delete'] == 'on':
    #         user.is_active = False
    #         user.save()
    #         return redirect('/')
    #     else:
    #         return redirect('dashboard')
    # if request.method == 'POST':
    #     # Get the new data from the form
    #     first_name = request.POST['firstName']
    #     last_name = request.POST['lastName']
    #     username = request.POST['username']
    #     email = request.POST['email']
    #     password = request.POST['password']
    #     new_password = request.POST['newpassword']
    #
    #     # Update the user's information if the new data is not empty
    #     if first_name:
    #         user.first_name = first_name
    #     if last_name:
    #         user.last_name = last_name
    #     if username:
    #         user.username = username
    #     if email:
    #         user.email = email
    #
    #     # Check if the password field is not empty and if the new password is different from the old one
    #     if password and user.check_password(password) and password != new_password:
    #         user.set_password(new_password)
    #
    #     # Save the user object
    #     user.save()
    #
    #     # Redirect to the profile page
    #     return redirect('dashboard')
    #
    # context = {
    #     'user': user,
    # }
    if request.method == "POST":
        if "update_details" in request.POST:
            return update_details(request)
        elif "change_password" in request.POST:
            return change_password(request)
        elif 'deactivate_account' in request.POST:
            return deactivate_account(request)
        elif "update_description" in request.POST:
            return update_description(request)
    else:
        update_details_form = UpdateDetailsForm(instance=request.user)
        update_password_form = UpdatePasswordForm(instance=request.user)
        deactivate_account_form = DeactivateAccountForm(instance=request.user)

    context = {
        'update_details_form': update_details_form,
        'update_password_form': update_password_form,
        'deactivate_account': deactivate_account_form,
        "update_details_form": update_details_form,
    }

    return render(request, "dashboard.html", context)


def deactivate_account(request):
    if request.method == 'POST':
        form = DeactivateAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            if form.cleaned_data['deactive_profile']:
                request.user.is_active = False
                request.user.save()
                messages.success(request, 'Account deactivated successfully')
                return redirect('index')
            else:
                messages.error(request, 'Please check the box to confirm account deactivation')
                return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('dashboard')
    return redirect('dashboard')

@login_required
def change_password(request):
    if request.method == "POST":
        form = UpdatePasswordForm(request.POST, instance=request.user)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Password updated successfully")
            # Keep the user logged in
            auth.login(request, request.user)
            return redirect("dashboard")
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect("dashboard")
    return redirect("/")


@login_required
def update_details(request):
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
    if request.method == "POST":
        description = request.POST["description"]
        request.user.description = description
        request.user.save()
        messages.success(request, "Description updated successfully")
        return redirect("dashboard")
    return redirect("dashboard")


@login_required
def logout(request):
    request.session.pop("session_ids", None)
    auth.logout(request)
    return redirect("/")


def codeofconduct(request):
    return render(request, "codeofconduct.html")


def handler400(request, *args, **argv):
    return render(request, "errors/400.html", status=400)


def handler403(request, *args, **argv):
    return render(request, "errors/403.html", status=403)


def handler404(request, *args, **argv):
    return render(request, "errors/404.html", status=404)


def handler500(request, *args, **argv):
    return render(request, "errors/500.html", status=500)


def handler503(request, *args, **argv):
    return render(request, "errors/503.html", status=503)
