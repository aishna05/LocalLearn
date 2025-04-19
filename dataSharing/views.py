from django.shortcuts import render

# Create your views here.
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def download_data(request):
    # Example user data – replace with DB data if needed
    data = {
        "username": "UserA",
        "scores": [90, 80, 100],
        "notes": "Shared offline"
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="userdata.json"'
    return response

@csrf_exempt
def upload_data(request):
    if request.method == 'POST' and request.FILES.get('datafile'):
        uploaded_file = request.FILES['datafile']
        file_data = uploaded_file.read().decode('utf-8')
        try:
            data = json.loads(file_data)
            print("Uploaded Data:", data)  # You can save it to DB
            return HttpResponse("Data uploaded successfully!")
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON file.", status=400)
    return HttpResponse("No file uploaded.", status=400)
