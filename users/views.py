from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from .utils import send_verification_email


def register(request):
    """Регистрация с подтверждением email"""
    if request.user.is_authenticated:
        return redirect('mailing:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Неактивен до подтверждения email
            user.save()
            send_verification_email(user, request)
            messages.success(
                request,
                'Регистрация успешна! Проверьте email для подтверждения аккаунта.'
            )
            return redirect('users:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def verify_email(request, token):
    """Подтверждение email по токену (в нашем случае — по email)"""
    try:
        user = CustomUser.objects.get(email=token)
        if user.is_email_verified:
            messages.info(request, 'Email уже подтверждён.')
        else:
            user.is_email_verified = True
            user.is_active = True
            user.save()
            messages.success(request, 'Email подтверждён! Теперь вы можете войти.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')
    return redirect('users:login')


def login_view(request):
    """Вход в систему по email"""
    if request.user.is_authenticated:
        return redirect('mailing:home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # 👇 Аутентификация по email (USERNAME_FIELD)
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('mailing:home')
            else:
                messages.error(request, 'Неверный email или пароль.')
        else:
            messages.error(request, 'Неверный email или пароль.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('mailing:home')