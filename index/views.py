from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages  # 导入messages模块，用于显示消息
from django.http import JsonResponse
from .models import FastaFile, VisitLog
import os
import json
from django.conf import settings

# 注册视图
def register(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/register'
        )
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # 保存用户
            
            # 记录注册操作
            ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            VisitLog.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                operation_type='other',
                page_url='/register',
                request_data='用户注册'
            )
            
            messages.success(request, "注册成功！请登录。")  # 显示成功消息
            return redirect("login")  # 注册成功后跳转到登录页面
        else:
            messages.error(request, "注册失败！请检查输入的信息。")  # 显示错误消息
    else:
        form = UserCreationForm()
    return render(request, "src/register.html", {"form": form})

#nlkcal
# 登录视图
def login_view(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/login'
        )
        
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)  # 验证用户名和密码

        # 记录登录操作
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        login_status = '登录成功' if user is not None else '登录失败'
        
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='other',
            page_url='/login',
            request_data=f'用户登录: {login_status}'
        )

        if user is not None:
            login(request, user)  # 登录成功
            messages.success(request, "登录成功！")  # 显示登录成功消息
            return redirect("/index")  # 登录成功后跳转到主页
        else:
            messages.error(request, "用户名或密码错误！")  # 登录失败，显示错误消息
    return render(request, "src/login.html")



def home(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/home'
        )
        
    return render(request, "mainsrc/page1.html")



def logout_view(request):
    # 记录注销操作
    ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    VisitLog.objects.create(
        ip_address=ip_address,
        user_agent=user_agent,
        operation_type='other',
        page_url='/logout',
        request_data='用户注销'
    )
    
    logout(request)  # 注销当前用户
    return redirect('login')  # 注销后跳转到登录页面

def page1(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/page1'
        )
        
    return render(request, "mainsrc/page1.html")

def about(request):
    # 获取所有FASTA文件记录
    fasta_files = FastaFile.objects.all().order_by('-upload_date')
    
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/about'
        )
    
    return render(request, "mainsrc/about.html", {'fasta_files': fasta_files})

def page2(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/page2'
        )
        
    return render(request, "mainsrc/page2.html")

def enzymemodel(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='protein_embedding',
            page_url='/enzymemodel'
        )
        
    return render(request, "mainsrc/enzymemodel.html")

def similarenzyme(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='similar_search',
            page_url='/similarenzyme'
        )
        
    return render(request, "mainsrc/similarenzyme.html")

def dataanalysis(request):
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='data_analysis',
            page_url='/dataanalysis'
        )
        
    return render(request, "mainsrc/dataanalysis.html")

def importdatabase(request):
    # 获取所有FASTA文件记录
    fasta_files = FastaFile.objects.all().order_by('-upload_date')
    
    # 如果没有预设文件，尝试自动发现并添加
    if not fasta_files.exists():
        try:
            discover_fasta_files()
            fasta_files = FastaFile.objects.all().order_by('-upload_date')
        except Exception as e:
            print(f"自动发现文件时出错: {str(e)}")
    
    # 记录访问日志
    if request.method == 'GET':
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='page_view',
            page_url='/importdatabase'
        )
    
    return render(request, "mainsrc/importdatabase.html", {'fasta_files': fasta_files})


# 获取FASTA文件内容的API
def get_fasta_content(request, file_id):
    try:
        # 从数据库获取文件记录
        fasta_file = FastaFile.objects.get(id=file_id)
        
        # 记录访问日志
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建访问记录
        VisitLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            operation_type='matrix_view',
            page_url=f'/get_fasta_content/{file_id}',
            request_data=f'查看文件: {fasta_file.name}'
        )
        
        # 构建文件的绝对路径
        file_path = os.path.join(settings.BASE_DIR, fasta_file.file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'文件不存在: {file_path}'}, status=404)
        
        # 读取文件内容
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 更新访问记录
        if request.META.get('REMOTE_ADDR'):
            visit_logs = VisitLog.objects.filter(
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0')
            ).order_by('-visit_time')
            
            if visit_logs.exists():
                latest_log = visit_logs.first()
                latest_log.viewed_file = fasta_file
                latest_log.save()
        
        return JsonResponse({'content': content, 'filename': fasta_file.name})
    
    except FastaFile.DoesNotExist:
        return JsonResponse({'error': '文件记录不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'发生错误: {str(e)}'}, status=500)

# 自动发现FASTA文件
def discover_fasta_files():
    # 记录访问日志
    ip_address = "系统操作"
    user_agent = "自动发现文件脚本"
    
    # 创建访问记录
    VisitLog.objects.create(
        ip_address=ip_address,
        user_agent=user_agent,
        operation_type='other',
        page_url='/discover_fasta_files',
        request_data='系统自动发现FASTA文件'
    )
    
    # 检查项目根目录下的data/fasta_files目录
    fasta_dir = os.path.join(settings.BASE_DIR, 'data', 'fasta_files')
    
    # 如果目录不存在，创建它
    if not os.path.exists(fasta_dir):
        os.makedirs(fasta_dir)
        print(f"创建目录: {fasta_dir}")
    
    # 遍历目录中的所有文件
    for file in os.listdir(fasta_dir):
        if file.endswith('.fasta'):
            file_path = os.path.join('data', 'fasta_files', file)
            
            # 检查是否已存在
            if not FastaFile.objects.filter(file_path=file_path).exists():
                # 创建新记录
                FastaFile.objects.create(
                    name=file.replace('.fasta', ''),
                    description=f"自动发现的FASTA文件: {file}",
                    file_path=file_path
                )
                print(f"添加了新的FASTA文件: {file_path}")


#
# # def