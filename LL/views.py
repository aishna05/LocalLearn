from django.shortcuts import render , get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from . import models
from django.contrib.auth.decorators import login_required
from .models import Notes, SharedNote, User, Subject
from django.http import JsonResponse
from django.core import serializers
import json
from django.utils import timezone
from django.conf import settings
import os
from django.views.decorators.cache import never_cache

@never_cache  # Prevent caching of the service worker
def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'service-worker.js')
    try:
        with open(sw_path, 'r') as sw_file:
            return HttpResponse(sw_file.read(), content_type='application/javascript')
    except FileNotFoundError:
        return HttpResponse("Service Worker not found.", status=404)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            user.date_joined = timezone.now()
            user.save()
            
            login(request, user)
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'signup.html', {'error': str(e)})
            
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            user.last_login = timezone.now()
            user.save()
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    subjects = models.Subject.objects.filter(user_id=user)
    notes = models.Notes.objects.filter(user=user)
    media = models.Media.objects.filter(user=user)
    my_notes = notes  # Same as notes above
    shared_notes = Notes.objects.filter(sharednote__recipient=request.user)
    
    context = {
        'subjects': subjects,
        'notes': notes,
        'media': media,
        'my_notes': my_notes,
        'shared_notes': shared_notes,
    }
    
    return render(request, 'main.html', context)

@login_required
def add_subject(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        
        # Create a new subject
        subject = models.Subject.objects.create(name=subject_name, user_id=request.user)
        subject.save()
        
        return redirect('dashboard')
    return render(request, 'add_subject.html')

@login_required
def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        subject_id = request.POST.get('subject')
        
        if not subject_id:
            return render(request, 'add_note.html', {'error': 'Subject is required'})
        
        try:
            subject = Subject.objects.get(id=int(subject_id), user_id=request.user)
            note = Notes.objects.create(
                title=title,
                content=content,
                user=request.user,
                subject=subject
            )
            return redirect('dashboard')
        except Subject.DoesNotExist:
            return render(request, 'add_note.html', {'error': 'Invalid subject'})
        except ValueError:
            return render(request, 'add_note.html', {'error': 'Invalid subject ID'})
    
    # Handle GET request
    subject_id = request.GET.get('subject')
    subjects = Subject.objects.filter(user_id=request.user)
    return render(request, 'add_note.html', {
        'subject_id': subject_id,
        'subjects': subjects
    })

@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id, user=request.user)
    subjects = Subject.objects.filter(user_id=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        subject_id = request.POST.get('subject')
        
        try:
            subject = Subject.objects.get(id=subject_id, user_id=request.user)
            note.title = title
            note.content = content
            note.subject = subject
            note.save()
            return redirect('dashboard')
        except Subject.DoesNotExist:
            return render(request, 'edit_note.html', {
                'error': 'Invalid subject',
                'note': note,
                'subjects': subjects
            })
    
    return render(request, 'edit_note.html', {
        'note': note,
        'subjects': subjects
    })

@login_required
def delete_note(request, note_id):
    note = models.Notes.objects.get(id=note_id, user=request.user)
    note.delete()
    return redirect('dashboard')

@login_required
def delete_subject(request, subject_id):
    subject = models.Subject.objects.get(id=subject_id, user_id=request.user)
    subject.delete()
    return redirect('dashboard')

@login_required
def delete_media(request, media_id):
    media = models.Media.objects.get(id=media_id, user=request.user)
    media.delete()
    return redirect('dashboard')

@login_required
def view_media(request, media_id):
    media = models.Media.objects.get(id=media_id, user=request.user)
    context = {
        'media': media,
    }
    return render(request, 'view_media.html', context)

@login_required
def edit_media(request, media_id):
    media = models.Media.objects.get(id=media_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        
        # Update the media
        media.title = title
        if file:
            media.file = file
        media.save()
        
        return redirect('dashboard')
    
    context = {
        'media': media,
    }
    
    return render(request, 'edit_media.html', context)

@login_required
def search_notes(request):
    query = request.GET.get('query', '').strip()
    
    if query:
        notes = models.Notes.objects.filter(
            user=request.user,
            title__icontains=query
        )
        subjects = models.Subject.objects.filter(user_id=request.user)
        
        context = {
            'notes': notes,
            'subjects': subjects,
            'query': query
        }
        return render(request, 'main.html', context)
    
    return redirect('dashboard')

@login_required
def search_subject(request):
    query = request.GET.get('query')
    notes = models.Subject.objects.filter(user=request.user, title__icontains=query)
    
    context = {
        'notes': notes,
    }
    
    return render(request, 'search_notes.html', context)

@login_required
def share_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id, owner=request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        recipient = get_object_or_404(User, username=username)
        SharedNote.objects.create(sender=request.user, recipient=recipient, note=note)
        return redirect('shared_notes')
    return render(request, 'share_note.html', {'note': note})

@login_required
def shared_notes(request):
    sent = SharedNote.objects.filter(sender=request.user)
    received = SharedNote.objects.filter(recipient=request.user)
    return render(request, 'shared_notes.html', {'sent': sent, 'received': received})

@login_required
def view_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id, user=request.user)
    return render(request, 'view_full_note.html', {'note': note})

@login_required
def export_notes(request):
    notes = models.Notes.objects.filter(user=request.user)
    data = serializers.serialize('json', notes)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=notes.json'
    return response

@login_required
def import_notes(request):
    if request.method == 'POST':
        json_file = request.FILES['json_file']
        data = json.load(json_file)
        for item in data:
            models.Notes.objects.create(
                user=request.user,
                title=item['fields']['title'],
                content=item['fields']['content'],
                # Add other fields as necessary
            )
        return redirect('dashboard')
    return render(request, 'import_notes.html')

@login_required
def share_notes_list(request):
    notes = Notes.objects.filter(user=request.user)
    return render(request, 'share_notes_list.html', {'notes': notes})

