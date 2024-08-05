from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.db import IntegrityError
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import subprocess
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
import datetime

# Create your views here.


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
        })
    else:
        if request.POST['password1'] == request.POST['password2'] and request.POST['password1'] != '' and request.POST['username'] != '':
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'Nombre de usuario no disponible',
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden',
        })


def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
        
    # Definir una lista vacía para los resultados del script
    tasks_dbf_lista = []

    try:
        # Llamar al script Leer_pasaje_parametros.py con subprocess y capturar la salida
        resultado = subprocess.run(['python3', '/home/u_com108/Desarrollos/Validaciones_dbf/Leer_pasaje_parametros.py'],
                                   capture_output=True, text=True, check=True)
        
        # Verificar si la ejecución fue exitosa
        if resultado.returncode == 0:
            # Dividir la salida en líneas y agregar cada línea a tasks_dbf
            tasks_dbf_lista = resultado.stdout #.strip() #.split('\n')
            print("Tipo de dato DBF: ", type(tasks_dbf_lista))
            print("Valores encontrados en DBF:", tasks_dbf_lista)
        else:
            print("Error al ejecutar Leer_pasaje_parametros.py:", resultado.stderr)
    
    except subprocess.CalledProcessError as e:
        print("Error de subprocess:", e)
    
    # Crear una instancia de Task y completar los campos
    tasks_dbf = Task(
        title= eval(tasks_dbf_lista[0]), #.split(':')[1].strip()),
        description=eval(tasks_dbf_lista[1]), #.split(':')[1].strip()),  # Extraer y evaluar la descripción
        created_at=eval(tasks_dbf_lista[2].split(':')[1].strip()),  # Extraer y evaluar la fecha de creación
        datecompleted=eval(tasks_dbf_lista[3].split(':')[1].strip()),  # Extraer y evaluar la fecha de completado
        important=eval(tasks_dbf_lista[4].split(':')[1].strip()),  # Extraer y evaluar si es importante
        user=User.objects.get(username=int(tasks_dbf_lista[5].split(':')[1].strip()))  # Extraer el ID de usuario)  # Aquí debes cambiar 'username' por el nombre de usuario correcto
    )

    # Guardar el objeto en la base de datos
    tasks_dbf.save()

    print("tipo de dato de task dbf: ",type(tasks_dbf))
    print("tipo de dato de task: ",type(tasks))

    """ 
    # Formato de salida deseado
    tasks_dbf = [
        f"<Task: {title.strip()} - by u_com{user_id}>"
    ]"""

    # Imprimir resultado
    print("tasks_dbf es: ",tasks_dbf)
    print("task es: ", tasks)

    # Intentar generar la URL inversa para cada tarea en tasks
    for task in tasks:
        try:
            task.detail_url = reverse('task_detail', args=[task.id])
        except NoReverseMatch as e:
            print("No se pudo generar la URL inversa para task:", e)
            task.detail_url = '#'  # O proporciona una URL alternativa


    return render(request, 'tasks.html', {'tasks': tasks, 'tasks_dbf': tasks_dbf})

"""
    # pasar parametros a otro script.py
    # # Lista de parámetros a pasar al script mi_script.py
    num_registro = 1
    
    # Llamar al script mi_script.py con subproceso para que traiga los datos del DBF
    resultado = subprocess.run(['python3', '/home/u_com108/Desarrollos/Validaciones_dbf/Leer_pasaje_parametros.py'], + num_registro, capture_output=True, text=True, check=True)
    
    # Verificar si la ejecución fue exitosa
    if resultado.returncode == 0:
        # El valor devuelto por Buscar_en_DBF.py estará en resultado.stdout
        tasks_dbf = resultado.stdout
        print("Valor del registro encontrado:", tasks_dbf)
    else:
        print("Error al ejecutar Buscar_en_DBF.py:", resultado.stderr)
    
    return render(request, 'tasks.html', {'tasks': tasks, 'tasks_dbf': tasks_dbf})
"""


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks_completed.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'POST':
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            
            # pasar parametros a otro script.py
            # # Lista de parámetros a pasar al script mi_script.py
            parametros = [new_task.title, new_task.description]

            # Llamar al script mi_script.py con subprocess
            subprocess.run(['python3', '/home/u_com108/Desarrollos/Validaciones_dbf/Escribir_pasaje_parametros.py'] + parametros, check=True)

            new_task.save()
            return redirect('tasks')
        except Exception:
            return render(request, 'create_task.html', {
                'form': TaskForm(),
                'error': 'Ocurrio un error al crear la tarea.',
            })
    else:
        return render(request, 'create_task.html', {
            'form': TaskForm(),
        })

@login_required    
def task_detail(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            #if form.is_valid():
            form.save()
            return redirect('tasks')
            #else:
            return render(request, 'task_detail.html', {'task': task, 'form': form})
        except Exception:
            return render(request, 'task_detail.html', {'task': task,'form': form, 'error': 'Ocurrio un error al actualizar la tarea.'})
    else:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})

@login_required
def create_task_(request):
    if request.method == 'POST':
        print(request.POST)  # for debugging purposes, remove in production
        title = request.POST['title']
        description = request.POST['description']
        if 'important' in request.POST:  # check if 'important' checkbox is checked in the
            important = True
        else:
            important = False
        user = request.user
        Task.objects.create(title=title, description=description, important=important, user=user)
        return redirect('tasks')
    else:
        return render(request, 'create_task.html', {
            'form': TaskForm(),
        })
    
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm(),
        })
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña incorrectos.',
            })


def signin2(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {
                'error': 'Usuario o contraseña incorrectos.',
            })
    else:
        return render(request, 'signin.html')