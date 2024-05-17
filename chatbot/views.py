from django.shortcuts import render, redirect
from chatbot.models import Session, Message
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
import json
from vertexai.generative_models import Content, GenerativeModel, Part


def chatbot_session(request, session_id):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve session IDs associated with the logged-in user
        session_ids = Session.objects.filter(user_id=request.user.id).values_list('session_id', flat=True)

        # Delete sessions that have no messages
        for session in session_ids:
            if not Message.objects.filter(session_id=session):
                Session.objects.filter(session_id=session).delete()

        # Store session IDs in the session object
        request.session['session_ids'] = list(session_ids)

        # Check if the session ID belongs to the list of session IDs in the session object
        if session_id not in request.session.get('session_ids', []):
            # 404
            return render(request, 'errors/404.html', status=404)
    else:
        # Anonymous user
        # Redirect to chatbot home page without storing history in session
        return redirect('chatbot_home')

    # Retrieve the messages associated with the session
    messages = Message.objects.filter(session_id=session_id).order_by('created_at')
    # Retrieve all session IDs associated with the logged-in user
    # session_ids = Session.objects.filter(user_id=request.user.id).values_list('session_id', flat=True)
    # Render the chatbot interface for the session
    return render(request, 'chatbot_session.html', {
        'chat_messages': messages,
        'user_sessions': session_ids,
        'current_session': session_id,
    })


def chatbot_home(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve session IDs associated with the logged-in user
        session_ids = Session.objects.filter(user_id=request.user.id).values_list('session_id', flat=True)
        # Store session IDs in the session object
        request.session['session_ids'] = list(session_ids)

        # Redirect to the last session if the user has any sessions
        if session_ids:

            # Delete sessions that have no messages
            for session_id in session_ids:
                if not Message.objects.filter(session_id=session_id):
                    print(f"Deleting session {session_id}")
                    Session.objects.filter(session_id=session_id).delete()

            # Retrieve the last session ID
            session_id_data = [{'session_id': session_id} for session_id in session_ids]
            last_session_id = session_id_data[-1]['session_id']

            # Redirect to the last session
            return redirect('chatbot_session', session_id=last_session_id)

        # Create a new session if the user has no sessions
        else:
            # Create a new session
            session = Session.objects.create(user=request.user)
            # Store the session ID in the session object
            request.session['session_ids'] = [session.session_id]
            # Redirect to the new session
            return redirect('chatbot_session', session_id=session.session_id)

    # Render the chatbot home page
    else:
        return render(request, 'chatbot_home.html')


def process_chat_message(request):
    if request.method == 'POST':
        # Retrieve the user's message from the request body
        data = json.loads(request.body)
        user_message = data.get('message')

        # Process the user's message and generate a response from the chatbot
        system_message = """
        Your name is Cyber Justitia.
        You are a helpful legal assistant who helps people with their legal problems.
        You are an expert in UK law and Newcastle-upon-Tyne bylaws.
        IMPORTANT: Do NOT say that you cannot provide legal advice. Instead, say that as a helpful legal assistant, 
        you can provide general information and guidance on legal matters, but not official legal advice.
        If you don't know the answer, just say that you don't know.
        """
        human_message = user_message
        if human_message:
            messages = [SystemMessage(content=system_message), HumanMessage(content=human_message)]
        else:
            return JsonResponse({'error': 'Invalid message'}, status=400)

        chat = ChatVertexAI(
            model_name="gemini-1.0-pro",
            convert_system_message_to_human=True,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            },
        )

        result = chat.generate([messages])
        chatbot_response = result.generations[0][0].text

        # Don't save to session for anonymous users
        if request.user.is_authenticated:
            # Retrieve the session ID from the request body
            session_id = request.session.get('session_ids', [])[0]
            # Retrieve the session object from the database
            session = Session.objects.get(session_id=session_id)
            # Save the system message in the database
            Message.objects.create(session=session, text=system_message, role=Message.Role.SYSTEM)
            # Save the user's message in the database
            Message.objects.create(session=session, text=human_message, role=Message.Role.USER)
            # Save the chatbot's response in the database
            Message.objects.create(session=session, text=chatbot_response, role=Message.Role.BOT)

        # Return the chatbot response in JSON format
        return JsonResponse({'response': chatbot_response})

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@require_POST
def create_session(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Create a new session, will be retrieved in chatbot_session
        session = Session.objects.create(user=request.user)

        # Redirect to the new session
        return redirect('chatbot_session', session_id=session.session_id)

    # Return an error response if the user is not authenticated
    return JsonResponse({'error': 'User is not authenticated'}, status=403)
