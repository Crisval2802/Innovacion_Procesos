from datetime import date, datetime
from django.shortcuts import redirect, render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from xml.etree import ElementTree as ET
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from pagina_web.models import cliente, registro, registro_detalle
from django.core.paginator import Paginator
from django.http import Http404
import json

# Create your views here.
class Redirigir(View):
    def get(self, request):
        return redirect('home')

#Clase para inciar sesion 
class Login(View):
    def get(self,request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('usuario')
        password = request.POST.get('contra')
        #Valida que se encuentre el usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) 
            return redirect('home')
        else:
            datos={'Error': "Correo o contraseña incorrectos"}
            return render(request, 'login.html', {"datos":datos})
        
class Inicio(View):
    def get(self, request):
        return render(request, 'inicio.html')

class Registro(View):
    def get(self, request):
        return render(request, 'registro.html')
    
    def post(self, request):
        username = request.POST.get('usuario')
        aux_usuarios=list(User.objects.filter(username=username).values())
        #Validacion para no registrar 2 o mas usuarios con el mismo nombre
        if len(aux_usuarios)>0:
            datos={'Error': "Ya existe un registro con ese nombre de usuario"}
            return render(request, 'registro.html', {"datos":datos})
        
        email = request.POST.get('email')
        aux_usuarios=list(User.objects.filter(email=email).values())
        #Validacion para no registrar 2 o mas usuarios con el mismo correo
        if len(aux_usuarios)>0:
            datos={'Error': "Ya existe un registro con ese correo"}
            return render(request, 'registro.html', {"datos":datos})
        contra = request.POST.get('contra')

        #Se registra el usuario en la tabla auth_user de django que sirve para iniciar sesion
        user = User.objects.create_user(username, email, contra)
        user.save()
        datos={'Exito': "Registro realizado exitosamente"}
        return render(request, 'registro.html', {"datos":datos})
    

class Home(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        clientes = cliente.objects.filter(id_usuario=request.user.id)
        return render(request, 'home.html', {"Usuario": request.user.username,"Clientes":clientes})
    
    def post(self, request):
        if 'archivo' in request.FILES:
            archivos = request.FILES.getlist('archivo')
            datos_xml_list = []

            for archivo in archivos:
                try:
                    #Parse del XML
                    tree = ET.parse(archivo)
                    root = tree.getroot()

                    #Obtener datos de la estructura del XML 
                    emisor_rfc = root.find('.//cfdi:Emisor', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}).get('Rfc')
                    receptor_rfc = root.find('.//cfdi:Receptor', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}).get('Rfc')
                    fecha = root.get('Fecha')
                    folio = root.get('Folio')
                    subtotal = float(root.get('SubTotal'))
                    total = float(root.get('Total'))
                    
                    if root.find('cfdi:Impuestos', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}):
                        iva=root.find('cfdi:Impuestos', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}).get('TotalImpuestosTrasladados')
                    else:
                        iva=0
                    conceptos = []
                    for concepto in root.findall('.//cfdi:Concepto', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}):
                        clave_prod_serv = concepto.get('ClaveProdServ')
                        cantidad = concepto.get('Cantidad')
                        clave_unidad = concepto.get('ClaveUnidad')
                        unidad = concepto.get('Unidad')
                        descripcion = concepto.get('Descripcion')
                        valor_unitario = concepto.get('ValorUnitario')
                        importe = concepto.get('Importe')
                        
                        conceptos.append({
                            'clave_prod_serv': clave_prod_serv,
                            'cantidad': cantidad,
                            'clave_unidad': clave_unidad,
                            'unidad': unidad,
                            'descripcion': descripcion,
                            'valor_unitario': valor_unitario,
                            'importe': importe,
                        })

                    impuestos_traslados = [] 

                    for traslado in root.findall('.//cfdi:Traslado', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'}):
                        base = traslado.get('Base')
                        impuesto = traslado.get('Impuesto')
                        tipo_factor = traslado.get('TipoFactor')
                        tasa_cuota = traslado.get('TasaOCuota')
                        importe = traslado.get('Importe')
                        impuestos_traslados.append({
                            'base': base,
                            'impuesto': impuesto,
                            'tipo_factor': tipo_factor,
                            'tasa_cuota': tasa_cuota,
                            'importe': importe,
                        })

                    #Lista de datos a enviar al HTML
                    datos_xml_list.append({
                        'habilitado': True,
                        'emisor_rfc': emisor_rfc,
                        'receptor_rfc': receptor_rfc,
                        'fecha': fecha,
                        'folio': folio,
                        'subtotal': subtotal,
                        'iva':iva,
                        'total': total,
                        'conceptos': conceptos,
                        'impuestos_trasladados': impuestos_traslados,
                    })
                    
                except ET.ParseError:
                    #Manejar errores al parsear el XML
                    pass

            # datos_ordenados_fecha = sorted(datos_xml_list, key=lambda x: x['fecha'], reverse=True)
            # print(datos_ordenados_fecha)
            clientes = cliente.objects.filter(id_usuario=request.user.id)
            return render(request, 'home.html', {'datos_xml_list': datos_xml_list, "Usuario": request.user.username, "Clientes": clientes})
        
        return render(request, 'home.html', {'error': 'No se proporcionó ningún archivo XML'})

#Clase para borrar la sesion del usuario        
class CerrarSesion(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post(self, request):
        logout(request)
        return redirect('login')
    

class Resumen(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post(self, request):
        datos = json.loads(request.POST.get('datos'))
        #print(datos)
        # Obtener el template HTML
        template_path = 'resumen.html'
        template = get_template(template_path)
        
        lista_filtrada=[]
        total_iva=0
        subtotal=0
        total=0
        for item in datos:
            if (item["habilitado"])==True:
                fecha = datetime.strptime(item['fecha'], "%Y-%m-%dT%H:%M:%S").date()
                item['fecha'] = fecha.strftime("%Y-%m-%d")
                
                if item['iva']:
                    total_iva+=float(item['iva'])
                subtotal+=float(item['subtotal'])


                lista_filtrada.append(item)
            
        total = subtotal + total_iva
        # Renderizar el template con los datos
        context = {'datos': lista_filtrada, 'total_iva':round(total_iva,2), 'total':round(total,2), 'subtotal':round(subtotal,2)}
        html = template.render(context)

        # Crear un archivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumen_iva.pdf"'

        # Convertir HTML a PDF
        pisa_status = pisa.CreatePDF(
            html, dest=response, encoding='utf-8')

        # Si se creó el PDF correctamente, devolver el PDF
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF')
        return response
    
class Usuario(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        return render(request, 'usuario.html', {"correo": request.user.email, "usuario": request.user.username})

class Cambiar_Usuario(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post(self, request):
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        user=User.objects.get(id=request.user.id)

        if (user.username!=username):
            aux_usuarios=list(User.objects.filter(username=username).values())
            #Validacion para no registrar 2 o mas usuarios con el mismo nombre
            if len(aux_usuarios)>0:
                return render(request, 'usuario.html', {"correo": request.user.email, "usuario": request.user.username, 'Error': "Error, ese nombre de usuario ya esta ocupado"})
        
        if (user.email!=email):
            aux_usuarios=list(User.objects.filter(email=email).values())
            #Validacion para no registrar 2 o mas usuarios con el mismo correo
            if len(aux_usuarios)>0:
                return render(request, 'usuario.html', {"correo": request.user.email, "usuario": request.user.username, 'Error': "Error, ese correo ya esta ocupado"})



        user.username=request.POST.get('usuario')
        user.email=request.POST.get('email')
        user.save()


        return render(request, 'usuario.html', {"correo": request.POST.get('email'), "usuario": request.POST.get('usuario'), 'Exito': "Datos actualizados exitosamente"})


class Cambiar_Contra(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post (self,request):
        password = request.POST.get('contra')
        aux_user = User.objects.get(id=request.user.id)
        aux_user.set_password(password)
        aux_user.save()

        #Se ractiva la sesion
        usuario_actualizado = authenticate(username=request.user.username, password=password)
        login(request, usuario_actualizado)
        return render(request, 'usuario.html', {"correo": request.user.email, "usuario": request.user.username, 'Exito_contra': "Contraseña actualizada exitosamente"})

class Clientes(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        clientes = cliente.objects.filter(id_usuario=request.user.id)
        return render(request, 'clientes.html', {"Clientes":clientes})

    def post(self,request):
        #Si el metodo es put se va a otra funcion
        if "_put" in request.POST:
            return self.put(request)

        #Si no hubo errores, se realiza el registro en la BD
        rfc = request.POST.get('rfc')
        #Se busca registros de clientes para verificar que el usuario no registre 2 veces el mismo RFC
        aux_clientes = cliente.objects.filter(id_usuario=request.user.id).filter(rfc=rfc)
        if aux_clientes:
            clientes = cliente.objects.filter(id_usuario=request.user.id)
            return render(request, 'clientes.html', {"Error": "Ya tienes registrado un cliente con ese RFC", "Clientes":clientes})
        else:
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            cliente.objects.create(id_usuario=request.user, nombre=nombre, apellido=apellido,rfc=rfc)

            clientes = cliente.objects.filter(id_usuario=request.user.id)
            return render(request, 'clientes.html', {"Exito": "Registro Exitoso", "Clientes":clientes})
    
    @method_decorator(login_required, name='dispatch')
    def put(self, request):
        aux_cliente = cliente.objects.get(id=request.POST.get('id'))
        aux_cliente.nombre=request.POST.get('nombre')
        aux_cliente.apellido=request.POST.get('apellido')

        #Se busca registros de clientes para verificar que el usuario no registre 2 veces el mismo RFC
        aux_clientes = cliente.objects.filter(id_usuario=request.user.id).filter(rfc=request.POST.get('rfc'))
        if aux_clientes:
            aux_cliente.save()
        else:
            aux_cliente.rfc=request.POST.get('rfc')
            aux_cliente.save()

        
        return self.get(request)
    
class Registros(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        #Se obtienen todos los registros y se hace la paginacion
        registros = registro.objects.filter(id_cliente__id_usuario=request.user).order_by('-id')
        page = request.GET.get('page', 1)
        try:
            paginator = Paginator(registros, 15)
            aux_registros = paginator.page(page)
        except:
          raise   Http404
        return render(request, 'registros.html', {"entity": aux_registros, 'paginator':paginator})
    
    def post(self,request):
        datos = json.loads(request.POST.get('datos'))
        #print(datos)
        total_iva=0
        subtotal=0
        total=0
        #For para obtener los totales y realizar el registro
        lista_filtrada=[]
        for item in datos:
            if (item["habilitado"])==True:
                aux=item['impuestos_trasladados']
                total_iva+=float(item['iva'])
                subtotal+=float(item['subtotal'])
                lista_filtrada.append(item)
        
        total=total_iva+subtotal
        if len(lista_filtrada)>0:
            if request.POST.get("tipo")=="gasto":
                tipo=True
            else:
                tipo=False
            rfc_cliente = request.POST.get('cliente')
            aux_cliente = cliente.objects.get(rfc=rfc_cliente, id_usuario=request.user.id)
            nuevo_registro = registro.objects.create(subtotal=subtotal, total=total, iva=total_iva, id_cliente_id=aux_cliente.id, tipo=tipo, fecha=date.today())
            #For para registrar los detalles en base al id del nuevo registro
            for item in lista_filtrada:
                aux=item['impuestos_trasladados']
                iva=0
                for item2 in aux:
                    if item2["importe"]:
                        iva=float(item2["importe"])
                iva=round(iva,2)
                #Se ajusta el formato de la fecha para poderlo registrar
                fecha = datetime.strptime(item['fecha'], "%Y-%m-%dT%H:%M:%S").date()
                fecha_formateada = fecha.strftime("%Y-%m-%d")
                if item["folio"]:
                    folio = item["folio"]
                else:
                    folio = "sin folio"
                registro_detalle.objects.create(fecha=fecha_formateada, folio=folio, subtotal=item['subtotal'], total=item['total'], iva=iva, emisor=item['emisor_rfc'], receptor=item['receptor_rfc'], id_registro=nuevo_registro)
            return JsonResponse({"Message":"Registro exitoso"})
        else:
            return JsonResponse({"Message":"Error, no se puede realizar un registro vacio"})
    
class Reporte_registro(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post(self, request):
        datos = registro_detalle.objects.filter(id_registro_id=request.POST.get("id")).order_by('-fecha')
        #print(datos)
        # Obtener el template HTML
        template_path = 'reporte.html'
        template = get_template(template_path)
        
        aux_registro = registro.objects.get(id=request.POST.get("id"))
        aux_cliente=cliente.objects.get(id=aux_registro.id_cliente.id)
       
        if aux_registro.tipo==False:
            tipo="Ingreso"
        else:
            tipo="Gasto"
        # Renderizar el template con los datos
        context = {'datos': datos, 'total_iva':round(aux_registro.iva,2), 'total':round(aux_registro.total,2), 'subtotal':round(aux_registro.subtotal,2), "fecha":aux_registro.fecha, "tipo":tipo, "cliente":aux_cliente}
        html = template.render(context)

        # Crear un archivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumen_iva.pdf"'

        # Convertir HTML a PDF
        pisa_status = pisa.CreatePDF(
            html, dest=response, encoding='utf-8')

        # Si se creó el PDF correctamente, devolver el PDF
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF')
        return response