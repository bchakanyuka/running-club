from django.shortcuts import redirect, render
from django.db.models import Sum, Count
from .models import Run
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import gpxpy

# Create your views here.
def leaderboard_view(request):
    if request.method == 'POST':
        #Prevent unauthenticated users from uploading
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to upload runs.")
            return redirect('login')
        
        #Handle GPX File Upload POST request        
        gpx_file = request.FILES.get('gpx_file')
        if gpx_file and gpx_file.name.lower().endswith('.gpx'):
            try:
                #read and decode file contents
                content_str = gpx_file.read().decode('utf-8')
                gpx = gpxpy.parse(content_str)

                #extract start time
                start_time = None
                if gpx.tracks:
                    for track in gpx.tracks:
                        for segment in track.segments:
                            if segment.points:
                                start_time = segment.points[0].time
                                break

                #calculate metrics
                total_distance_km = gpx.length_2d() / 1000
                duration_seconds = gpx.get_duration()
                duration_minutes = duration_seconds / 60 if duration_seconds else 0

                if total_distance_km > 0 and duration_minutes > 0:
                    pace_decimal = duration_minutes / total_distance_km
                    pace_minutes = int(pace_decimal)
                    pace_seconds =int((pace_decimal - pace_minutes) * 60)
                    pace_str = f"{pace_minutes}:{pace_seconds:02d} min/km"
                else:
                    pace_str = "N/A"

                #save to database
                Run.objects.create(
                    user=request.user,
                    file_name=gpx_file.name,
                    start_time=start_time,
                    distance_km=total_distance_km,
                    duration_mins=duration_minutes,
                    avg_pace=pace_str
                )
                messages.success(request, f"Successfully uploaded {gpx_file.name}!")
            except Exception as e:
                messages.error(request,f"Error parsing GPX file: {e}")
        else:
            messages.error(request, "Please upload a valid .gpx file.")
        
        return redirect('leaderboard')
        
    #Aggregate total distance per user, ordered highest to lowest
    leaderboard = (Run.objects.values('user__username').annotate(total_distance=Sum('distance_km'), total_runs=Count('id')).order_by('-total_distance'))
    context = {'leaderboard': leaderboard,}
    return render(request, 'runs/leaderboard.html', context)

#filters runs only for the logged in user and handles deletion requests
@login_required
def profile_view(request):
    #Handle run deletion via POST request
    if request.method == 'POST' and 'delete_run_id' in request.POST:
        run_id = request.POST.get('delete_run_id')
        #Check to ensure the run belongs to the logged-in user
        Run.objects.filter(id=run_id, user=request.user).delete()
        messages.success(request, "Run deleted successfully.")
        return redirect('profile')

    #fetch only the logged-in user's runs, newest first
    user_runs = Run.objects.filter(user=request.user).order_by('-start_time')

    context = {'user_runs': user_runs}
    return render(request, 'runs/profile.html', context)

#signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() #Creates user and securerly hashes the password
            login(request, user) #Automatically log them in after signup
            return redirect('leaderboard')
    else:
        form = UserCreationForm()

    return render(request, 'runs/signup.html', {'form': form})

#login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('leaderboard')
    else:
        form = AuthenticationForm()

    return render(request, 'runs/login.html', {'form': form})

#logout view
def logout_view(request):
    if request.method =='POST':
        logout(request)
        return redirect('leaderboard')