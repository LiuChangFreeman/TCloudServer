#encoding=utf-8
from django.http.response import HttpResponse, StreamingHttpResponse
import os
import re
from Main.views import *
from Main.confctrl import *
def permission(request):
    if request.method=='GET':
        username=request.GET.get('username')
        path = request.GET.get('path')
        tree = directorytree(path,username)
        data = tree.traverse()
        result = {}
        result['html'] = data
        result['path'] = path
        result['user'] = username
        result['logintime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #os.system('systemctl restart smb')
        if request.session.has_key("mobile"):
            data['logintime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data['username']='root'
            result = {"success": True, "error": "", "msg": "", "errorCode": 0, "data": data}
            return HttpResponse(json.dumps(result).decode("unicode-escape"))
        return render(request,'permission.html',{'data':result})
    if request.method=='POST':
        type=request.POST.get('submit')
        path=request.POST.get('path')
        username=request.POST.get('username')
        #changepermission(path, username, type)
        #os.system('systemctl restart smb')
        SetPermission(path, username, type)
        if request.session.has_key("mobile"):
            result = {"success": True, "error": "", "msg": "操作成功!", "errorCode": 0, "data": {}}
            resopnse = HttpResponse(json.dumps(result))
        else:
            resopnse=HttpResponse(username+'</br>'+path+'</br>'+type+u'<script>window.onload=function(){alert("操作成功!");location.replace(document.referrer);}</script>')
        return resopnse