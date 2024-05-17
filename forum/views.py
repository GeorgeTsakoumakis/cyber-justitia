from django.shortcuts import render

def forums(request):
    return render(request, 'forum.html')
