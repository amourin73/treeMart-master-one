from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'inbox.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'send.html', {'form': form})
