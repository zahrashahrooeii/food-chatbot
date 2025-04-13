from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home_view(request):
    # Pass the forms to the template context
    # We might refine this later to only show forms if not logged in
    if request.user.is_authenticated:
         return redirect('chat') # Redirect logged-in users to chat

    register_form = UserCreationForm()
    login_form = AuthenticationForm()
    return render(request, 'home.html', {'register_form': register_form, 'login_form': login_form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in the user automatically after registration
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('chat') # Redirect to chat page after successful registration
        else:
            # If form is invalid, re-render home page with errors
            login_form = AuthenticationForm() # Provide login form as well
            messages.error(request, 'Registration failed. Please correct the errors below.')
            # Add form with errors to context
            return render(request, 'home.html', {'register_form': form, 'login_form': login_form})
    else:
        # If GET request, redirect to home page where the form is displayed
        return redirect('home')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome back, {username}!')
                # Redirect to a success page, e.g., the chat page or intended page
                next_url = request.POST.get('next', 'chat') # Get next page or default to chat
                return redirect(next_url)
            else:
                 messages.error(request, 'Invalid username or password.')
        else:
            # Form is invalid
            messages.error(request, 'Invalid username or password. Please check your input.')
        # If login fails or form invalid, re-render home page with error message
        register_form = UserCreationForm() # Provide register form as well
        # Pass the invalid login form back to display errors
        return render(request, 'home.html', {'register_form': register_form, 'login_form': form})
    else:
        # If GET request, redirect to home page where the form is displayed
        return redirect('home')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home') # Redirect to home page after logout

@login_required # Ensure only logged-in users can access chat
def chat_view(request):
    # Placeholder for the chat page logic
    return render(request, 'chat.html')

# You might have other views here already, keep them 