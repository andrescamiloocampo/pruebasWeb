from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserRegisterForm,guardarVideoForm
from crispy_forms.helper import FormHelper
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.http import HttpRequest
import cv2
import threading
import os
import django
from django.conf import settings
from django.contrib.auth.models import User
from streamz.models import comentarios
from django.contrib.auth.decorators import login_required
from .models import Video

# Create your views here.

def principal(request):
    imagenes = Video.objects.all().values()
    context = {
        'imagenes':imagenes
    }
    return render(request,'main.html',context)
# def live_video(request):
#     try:
#         cam = camara()
#         return StreamingHttpResponse(gen(cam),content_type="multipart/x-mixed-replace;boundary=frame")
#         pass
#     except:
#         pass

@login_required
def live_video(request):
    cap = cv2.VideoCapture(0)

    def gen():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')


class camara(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed,self.frame) = self.video.read()
        threading.Thread(target=self.update,args=()).start()
            
    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed,self.frame) = self.video.read()

def gen(camara):
    while True:
        frame = camara.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')
        
def iniciar_transmision(request):
    if request.user.is_authenticated:
        return redirect('/stream')
    else:
        return redirect('/login')

def streamz(request):
    template = loader.get_template('stream.html')
    return HttpResponse(template.render())

def login(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render())

def registro(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()            
            return redirect('/')
    else:
        form = UserRegisterForm()

    helper = form.helper    
    context = {
        'form':form,
        'helper':helper  
    }
    return render(request,'registro.html',context)

def usuario(request):
    context = {'myUser':request.user}
    return render(request,'usuario.html',context)

def vista_comentarios(request,id):
    comments = comentarios.objects.all().values()
    imagen = Video.objects.get(id=id)
    context = {
        'comments':comments,
        'imagen':imagen
    }
    return render(request,'comentarios.html',context)

@login_required
def guardarVideo(request):
    if request.method == 'POST':
        form = guardarVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = Video(usuario=request.user, imagen=form.cleaned_data['imagen'])
            video.save()
            return redirect('exito')
    else:
        form = guardarVideoForm()

    return render(request, 'guardar_video.html', {'form': form})

def exito(request):
    return render(request, 'exito.html')
