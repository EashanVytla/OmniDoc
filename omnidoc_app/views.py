from django.shortcuts import render
from django.http import JsonResponse
import subprocess

def main_view(request):
    return render(request, 'main.html')  

def run_python_script(request):
    if request.method == 'POST':
        # Run your Python script using subprocess or any other method
        try:
            result = subprocess.run(['python3', 'path_to_your_script.py'], capture_output=True, text=True)
            return JsonResponse({'output': result.stdout})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
