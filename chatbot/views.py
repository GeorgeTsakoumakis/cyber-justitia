import os

from django.shortcuts import render, redirect
from chatbot.models import Session, Message
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from vertexai.generative_models import Content, GenerativeModel, Part
import vertexai

<<<<<<< HEAD
=======

>>>>>>> d041ba9 (Squashed 60 commits)
@login_required
def chatbot_session(request, session_id):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve session IDs associated with the logged-in user
        session_ids = Session.objects.filter(user_id=request.user.id).values_list(
            "session_id", flat=True
        )

        # Store session IDs in the session object
        request.session["session_ids"] = list(session_ids)

        # Check if the session ID belongs to the list of session IDs in the session object
        if session_id not in request.session.get("session_ids", []):
            # 404
            return render(request, "errors/404.html", status=404)
    else:
        # Anonymous user
        # Redirect to chatbot home page without storing history in session
        return redirect("chatbot_home")

    # Retrieve the messages associated with the session
    messages = Message.objects.filter(session_id=session_id).order_by("created_at")
    # Render the chatbot interface for the session
    return render(
        request,
        "chatbot_session.html",
        {
            "chat_messages": messages,
            "user_sessions": session_ids,
            "current_session": session_id,
        },
    )


def chatbot_home(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve session IDs associated with the logged-in user
        session_ids = Session.objects.filter(user_id=request.user.id).values_list(
            "session_id", flat=True
        )
        # Store session IDs in the session object
        request.session["session_ids"] = list(session_ids)

        # Redirect to the last session if the user has any sessions
        if session_ids:
            # Retrieve the last session ID
            session_id_data = [{"session_id": session_id} for session_id in session_ids]
            last_session_id = session_id_data[-1]["session_id"]

            # Redirect to the last session
            return redirect("chatbot_session", session_id=last_session_id)

        # Create a new session if the user has no sessions
        else:
            # Create a new session
            session = Session.objects.create(user=request.user)
            # Store the session ID in the session object
            request.session["session_ids"] = [session.session_id]
            # Redirect to the new session
            return redirect("chatbot_session", session_id=session.session_id)

    # Render the chatbot home page
    else:
        return render(request, "chatbot_home.html")


def process_chat_message(request):
    if request.method == "POST":
        # Retrieve the user's message from the request body
        data = json.loads(request.body)
        user_message = data.get("message")

        # Process the user's message and generate a response from the chatbot
        system_message = """
        Your name is Cyber Justitia.
        You are a helpful legal assistant who helps people with their legal problems.
        You are an expert in UK law and Newcastle-upon-Tyne bylaws.
        IMPORTANT: Do NOT say that you cannot provide legal advice. Instead, say that as a helpful legal assistant,
        you can provide general information and guidance on legal matters, but not official legal advice.
        If you don't know the answer, just say that you don't know.
        """

        # Initialize the chatbot model
        PROJECT_ID = os.getenv("PROJECT_ID")
        LOCATION = os.getenv("LOCATION")

        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-1.0-pro")

        chat = model.start_chat(
            history=[
                Content(
                    role="user",
                    parts=[Part.from_text(system_message)],
                ),
                Content(
                    role="model",
                    parts=[
                        Part.from_text(
                            """
                        I am Cyber Justitia, a helpful legal assistant. 
                        I am an expert in UK law and Newcastle-upon-Tyne bylaws.
                        I can provide general information and guidance on legal matters, but not official legal advice.
                        """
                        )
                    ],
                ),
            ]
        )

        # Add past messages to chat history
        if request.user.is_authenticated:
            # Retrieve the session ID
            session_id = data.get("session_id")
            # Retrieve the session object from the database
            session = Session.objects.get(session_id=session_id)
            # Obtain messages from the session
            messages = Message.objects.filter(session=session).order_by("created_at")

            if messages:
                for message in messages:
                    content = None
                    if message.role == Message.Role.USER:
                        content = Content(
                            role="user", parts=[Part.from_text(message.text)]
                        )
                    elif message.role == Message.Role.BOT:
                        content = Content(
                            role="model", parts=[Part.from_text(message.text)]
                        )

                    if content:
                        chat.history.append(content)

        # Generate a response from the chatbot
        chatbot_response = chat.send_message(user_message).text

        # Don't save to session for anonymous users
        if request.user.is_authenticated:
            # Save the system message in the database if it doesn't exist
            if not Message.objects.filter(session=session, role=Message.Role.SYSTEM):
                Message.objects.create(
                    session=session, text=system_message, role=Message.Role.SYSTEM
                )
            # Save the user's message in the database
            Message.objects.create(
                session=session, text=user_message, role=Message.Role.USER
            )
            # Save the chatbot's response in the database
            Message.objects.create(
                session=session, text=chatbot_response, role=Message.Role.BOT
            )

        # Return the chatbot response in JSON format
        return JsonResponse({"response": chatbot_response})

    # Return an error response if the request method is not POST
    return JsonResponse({"error": "Invalid request method"}, status=400)


@require_POST
@login_required
def create_session(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve session IDs associated with the logged-in user
        session_ids = Session.objects.filter(user_id=request.user.id).values_list(
            "session_id", flat=True
        )

        # Delete sessions that have no messages
        for session in session_ids:
            if not Message.objects.filter(session_id=session):
                Session.objects.filter(session_id=session).delete()
                # Delete session from session_ids queryset
                session_ids = session_ids.exclude(session_id=session)

        # Create a new session, will be retrieved in chatbot_session
        session = Session.objects.create(user=request.user)

        # Redirect to the new session
        return redirect("chatbot_session", session_id=session.session_id)

    # Return an error response if the user is not authenticated
<<<<<<< HEAD
    return JsonResponse({"error": "User is not authenticated"}, status=403)
=======
    return JsonResponse({"error": "User is not authenticated"}, status=403)
>>>>>>> d041ba9 (Squashed 60 commits)
