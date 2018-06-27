#encoding=utf-8
import shutil
import os
from Main.views import *

def upload(request):
    if request.method == "POST":
        files = request.FILES.getlist('file',None)
        path=request.POST.get('path')
        username=request.session['username']
        if findpermission(path, username) != u'读写':
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "您没有权限上传文件!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse("<script>alert('您没有权限上传文件!');window.history.back(-1);</script>")
            return resopnse
        if not files:
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "请选择文件后再上传!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse("<script>alert('请选择文件后再上传!');window.history.back(-1);</script>")
            return resopnse
        for file in files:
            store = open(os.path.join(path, file.name.split('\\')[0]),'wb+')
            for chunk in file.chunks():
                store.write(chunk)
            store.close()
        if request.session.has_key("mobile"):
            result = {"success": True, "error": "", "msg": "上传成功!", "errorCode": 0, "data": {}}
            resopnse = HttpResponse(json.dumps(result))
        else:
            resopnse=HttpResponse("<script>alert('上传成功!');location.replace(document.referrer);</script>")
        return resopnse
def download(request):
    filename=request.GET.get('path')
    def file_iterator(file_name, chunk_size=512):
      with open(file_name,'rb') as f:
        while True:
          c = f.read(chunk_size)
          if c:
            yield c
          else:
            break
    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Length'] = os.path.getsize(filename)
    response['Accept-Length'] = os.path.getsize(filename)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename.split('/')[-1])
    return response
def uploadfolder(request):
    if request.method == "POST":
        files = request.FILES.getlist('file',None)
        choice=request.POST.get('submit')
        path=request.POST.get('path')
        foldername = request.POST.get('foldername', None)
        username=request.session['username']
        if findpermission(path,username)!=u'读写':
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "您没有权限建文件夹!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse("<script>alert('您没有权限建文件夹!');window.history.back(-1);</script>")
            return resopnse

        if not foldername:
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "文件夹名不为空!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse("<script>alert('文件夹名不为空!');window.history.back(-1);</script>")
            return resopnse
        folderpath=os.path.join(path,foldername)
        if os.path.exists(folderpath):
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "文件夹已存在!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse("<script>alert('文件夹已存在!');window.history.back(-1);</script>")
            return resopnse
        os.mkdir(folderpath)
        for file in files:
            store = open(os.path.join(folderpath, file.name),'wb+')
            for chunk in file.chunks():
                store.write(chunk)
            store.close()
        if request.session.has_key("mobile"):
            result = {"success": True, "error": "", "msg": "建立文件夹成功!", "errorCode": 0, "data": {}}
            resopnse = HttpResponse(json.dumps(result))
        else:
            resopnse = HttpResponse("<script>alert('建立文件夹成功!');window.history.back(-1);</script>")
        return resopnse
def multiple(request):
    paths=request.POST.getlist('path')
    choice=request.POST.get('submit')
    username = request.session['username']
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    if choice==u'删除':
        for path in paths:
            permission=findpermission(path,username)
            if permission!=u'读写':
                if request.session.has_key("mobile"):
                    result = {"success": False, "error": u"您没有权限删除"+path+u"等文件!", "msg": "", "errorCode": -1, "data": {}}
                    resopnse = HttpResponse(json.dumps(result))
                else:
                    resopnse = HttpResponse(u"<script>alert('您没有权限删除"+path+u"等文件!');window.history.back(-1);</script>")
                return resopnse
            if os.path.isdir(path):
                shutil.rmtree(path)
            if os.path.isfile(path):
                os.remove(path)
            connection.select_db('NasDb')
            sql = "delete from permission where path='%s'" %path
            cursor.execute(sql)
            connection.commit()
        connection.close()
        if request.session.has_key("mobile"):
            result = {"success": True, "error": "", "msg": "删除成功!", "errorCode": 0, "data": {}}
            resopnse = HttpResponse(json.dumps(result))
        else:
            resopnse = HttpResponse("<script>alert('删除成功!');window.history.back(-1);</script>")
        return resopnse
    elif choice==u'下载':
        #os.system('rm -rf /download;mkdir /download')
        os.system('cd /download;rm -rf *')
        for path in paths:
            os.system('cp -r '+path+' /download/'+path.split('/')[-1])
        os.system('cd /download;zip -r /download/download.zip `ls -A`')
        filename = '/download/download.zip'
        def file_iterator(file_name, chunk_size=512):
            with open(file_name, 'rb') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
        response = StreamingHttpResponse(file_iterator(filename))
        response['Content-Length'] = os.path.getsize(filename)
        response['Accept-Length'] = os.path.getsize(filename)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename.split('/')[-1])
        return response