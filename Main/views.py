# encoding=utf-8
from django.shortcuts import render
from django.http.response import HttpResponse, StreamingHttpResponse
from django.http import HttpResponseRedirect
import MySQLdb
import os
import time
import json
class Node(object):
    def __init__(self, name, type, path,permission):
        self.childs = []
        self.name = name
        self.type = type
        self.path = path
        self.permission=permission
        self.time=None
    def traverse(self):
        dic = {}
        dic['type'] = self.type
        dic['name'] = self.name
        dic['path'] = self.path
        dic['time'] = self.time
        dic['permission']=self.permission
        if len(self.childs) > 0:
            array = []
            for item in self.childs:
                itemdic = {}
                temp = []
                itemdic['type'] = item.type
                itemdic['name'] = item.name
                itemdic['path'] = item.path
                itemdic['time'] = item.time
                itemdic['permission']=item.permission
                if len(temp) > 0:
                    itemdic['subdic'] = temp
                array.append(itemdic)
            if len(array) > 0:
                dic['subdic'] = array
        return dic
    def fulltraverse(self):
        dic = {}
        dic['type'] = self.type
        dic['name'] = self.name
        dic['path'] = self.path
        dic['time'] = self.time
        dic['permission'] = self.permission
        if len(self.childs) > 0:
            array = []
            for item in self.childs:
                itemdic = {}
                temp = []
                if len(item.childs) > 0:
                    for child in item.childs:
                        temp.append(child.traverse())
                itemdic['type'] = item.type
                itemdic['name'] = item.name
                itemdic['path'] = item.path
                itemdic['time'] = item.time
                itemdic['permission']=item.permission
                if len(temp) > 0:
                    itemdic['subdic'] = temp
                array.append(itemdic)
            if len(array) > 0:
                dic['subdic'] = array
        return dic
def findpermission(path,username):
        connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
        cursor = connection.cursor()
        connection.select_db('NasDb')
        sql = "select permission from permission where username='%s' and path='%s'" % (username,path)
        cursor.execute(sql)
        result = cursor.fetchall()
        temp=u'读写'
        for row in result:
            temp=row[0]
        return temp
def isvalid(path,username):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    sql = "select * from permission where path='%s'" % path
    cursor.execute(sql)
    recordings = cursor.fetchall()
    temp = True
    for row in recordings:
        if row[2] == u'独占'and row[0]!=username:
            temp=False
    return temp
def directorytree(path,username):
    temp = Node(name=path.split('/')[-1], type='folder', path=path,permission=findpermission(path,username))
    for root, dirs, files in os.walk(path, topdown=True):
        for name in dirs:
            #temp.childs.append(directorytree(os.path.join(root, name), username))
            temppath=os.path.join(root, name)
            tempnode1 = Node(name=temppath.split('/')[-1], type='folder', path=temppath, permission=findpermission(temppath, username))
            ModifiedTime = time.localtime(os.stat(os.path.join(root, name)).st_mtime)
            tempnode1.time= time.strftime('%Y-%m-%d %H:%M:%S', ModifiedTime)
            temp.childs.append(tempnode1)
        for name in files:
            temppath = os.path.join(root, name)
            tempnode2 = Node(name=name.split('/')[-1], type='file', path=temppath,permission=findpermission(temppath, username))
            ModifiedTime = time.localtime(os.stat(os.path.join(root, name)).st_mtime)
            tempnode2.time= time.strftime('%Y-%m-%d %H:%M:%S', ModifiedTime)
            temp.childs.append(tempnode2)
        break
    return temp
def adduser(username, password):
    if username != 'root':
        os.system('useradd %s -p %s' % (username, password))
    os.system('echo -e \"%s\n%s\" | smbpasswd -a %s -s' % (password, password, username))
def deluser(username):
    os.system('smbpasswd -x %s' % username)
    if username != 'root':
        os.system('userdel %s' % username)
def register(request):
    if request.method == 'GET':
        if request.session['username'] == 'root':
            return render(request, "register.html")
        else:
            return HttpResponse('<script>window.onload=function(){alert("您不是管理员，不能注册用户!");window.history.back(-1);}</script>')
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        mobile= request.POST.get("mobile")
        connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
        cursor = connection.cursor()
        connection.select_db('NasDb')
        try:
            sql = "select * from user"
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                if row[1] == username:
                    if mobile != None:
                        result = {"success": False, "error": "该用户名已经被注册!", "msg": "", "errorCode": -1, "data": {}}
                        resopnse = HttpResponse(json.dumps(result))
                    else:
                        resopnse=HttpResponse('<script>window.onload=function(){alert("该用户名已经被注册!");window.history.back(-1);}</script>')
                    return resopnse
        except:
            if mobile != None:
                result = {"success": False, "error": "注册失败，发生异常!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse =HttpResponse('<script>window.onload=function(){alert("注册失败，发生异常!");window.history.back(-1);}</script>')
            return resopnse
        try:
            sql = "insert into user(username,password,pwdchanged) values(%s,%s,%s)"
            sqldata = (username, password, 'false')
            cursor.execute(sql, sqldata)
            connection.commit()
            connection.close()
            #adduser(username, password)
            if mobile != None:
                result = {"success": True, "error": "", "msg": "注册用户成功!", "errorCode": -1, "data": {}}
                request.session['mobile'] = True
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse=HttpResponse('<script>window.onload=function(){alert("注册用户成功!");window.location.href=\'/register\'}</script>')
            return resopnse
        except:
            if mobile != None:
                result = {"success": False, "error": "注册失败，发生异常!", "msg": "", "errorCode": -1, "data": {}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse =HttpResponse('<script>window.onload=function(){alert("注册失败，发生异常!");window.history.back(-1);}</script>')
            return resopnse
def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        mobile= request.POST.get("mobile")
        connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
        cursor = connection.cursor()
        connection.select_db('NasDb')
        sql = "select * from user where username='%s'" % username
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result)==0:
            if mobile!=None:
                result={"success":False,"error":"不存在的用户","msg":"","errorCode":-1,"data":{}}
                request.session['mobile'] = True
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse =  HttpResponse('<script>window.onload=function(){alert("不存在的用户名!");window.history.back(-1);}</script>')
            return resopnse
        if result[0][2]== password:
            request.session['username'] = str(result[0][1])
            connection.close()
            # if result[0][3] == 'false':
            #     html = {}
            #     html['username'] = str(result[0][1])
            #     if mobile != None:
            #         result = {"success": True, "error": "","msg":"您需要先更改密码", "errorCode":0, "data": {}}
            #         request.session['mobile'] = True
            #         return HttpResponse(json.dumps(result))
            #     return render(request, "changepassword.html", {"data": html})
            if username == 'root':
                if mobile != None:
                    result = {"success": True, "error": None,"msg":"管理员登录成功!", "errorCode": 0, "data": {}}
                    request.session['mobile'] = True
                    resopnse = HttpResponse(json.dumps(result))
                else:
                    resopnse = HttpResponseRedirect('/manage')
                return resopnse
            if mobile!=None:
                result={"success":True,"error":None,"msg":"用户登录成功!","errorCode":0,"data":{"url":"/main?path=/mainlist"}}
                request.session['mobile'] = True
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse = HttpResponseRedirect('/main?path=/home')
            return resopnse
        else:
            connection.close()
            if mobile!=None:
                result={"success":False,"error":"密码不正确!","msg":"","errorCode":-1,"data":{}}
                resopnse = HttpResponse(json.dumps(result))
            else:
                resopnse = HttpResponse('<script>window.onload=function(){alert("密码不正确!");window.history.back(-1);}</script>')
            return resopnse
def logout(request):
    if request.session.has_key("mobile"):
        result = {"success": True, "error": "", "msg": "登出成功!", "errorCode": 0, "data": {}}
        request.session['mobile'] = True
        resopnse=HttpResponse(json.dumps(result))
    else:
        resopnse=HttpResponseRedirect('/index')
    for key in request.session.keys():
        del request.session[key]
    return resopnse
def logoff(request):
    username = request.GET.get('username')
    #deluser(username)
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    try:
        sql = "delete from user where username='%s'" % username
        cursor.execute(sql)
        sql = "delete from permission where username='%s'" % username
        cursor.execute(sql)
        connection.commit()
        connection.close()
        return HttpResponse(u'<script>window.onload=function(){alert("用户' + username + u'删除成功!");location.replace(document.referrer);}</script>')
    except:
        return HttpResponse(u'<script>window.onload=function(){alert("删除失败，发生异常!");window.history.back(-1);}</script>')
def synpassword(username, password):
    if username != 'root':
        os.system('echo -e \"%s\n%s\" | passwd %s' % (password, password, username))
    os.system('echo -e \"%s\n%s\" | smbpasswd -a %s -s' % (password, password, username))
def changepassword(request):
    if request.method == 'GET':
        html = {}
        html['username'] = request.GET.get('username')
        return render(request, "changepassword.html", {"data": html})
    if request.method == 'POST':
        username = request.POST.get("username")
        oldpassword = request.POST.get("oldpassword")
        newpassword1 = request.POST.get("newpassword1")
        newpassword2 = request.POST.get("newpassword2")
        if newpassword1 != newpassword2:
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "两次密码不相同!", "msg": "", "errorCode": -1, "data": {}}
                return HttpResponse(json.dumps(result))
            return HttpResponse('<script>window.onload=function(){alert("两次密码不相同!");window.history.back(-1);}</script>')
        connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,
                                     charset='utf8')
        cursor = connection.cursor()
        connection.select_db('NasDb')
        try:
            sql = "select * from user where username='%s'" % username
            cursor.execute(sql)
            result = cursor.fetchall()
            if result[0][2] == oldpassword:
                sql = "update user set password=%s,pwdchanged=%s where username=%s"
                sqldata = (newpassword1, 'true', username)
                cursor.execute(sql, sqldata)
                connection.commit()
                connection.close()
                synpassword(username, newpassword1)
                if request.session.has_key("mobile"):
                    result = {"success": True, "error": "", "msg": "更新密码成功!", "errorCode": 0, "data": {}}
                    return HttpResponse(json.dumps(result))
                return HttpResponse(
                    '<script>window.onload=function(){alert("更新密码成功!");window.location.href=\'/index\'}</script>')
            else:
                if request.session.has_key("mobile"):
                    result = {"success": False, "error": "旧密码不正确!", "msg": "", "errorCode": -1, "data": {}}
                    return HttpResponse(json.dumps(result))
                return HttpResponse(
                    '<script>window.onload=function(){alert("旧密码不正确!");window.history.back(-1);}</script>')
        except:
            if request.session.has_key("mobile"):
                result = {"success": False, "error": "更新密码失败，发生异常!", "msg": "", "errorCode": -1, "data": {}}
                return HttpResponse(json.dumps(result))
            return HttpResponse(
                '<script>window.onload=function(){alert("更新密码失败，发生异常!");window.history.back(-1);}</script>')
def rootchangepassword(request):
    if request.method == 'GET':
        html = {}
        html['username'] = request.GET.get('username')
        return render(request, "root.html", {"data": html})
    if request.method == 'POST':
        username = request.POST.get("username")
        newpassword1 = request.POST.get("newpassword1")
        newpassword2 = request.POST.get("newpassword2")
        if newpassword1 != newpassword2:
            return HttpResponse('<script>window.onload=function(){alert("两次密码不相同!");window.history.back(-1);}</script>')
        connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,
                                     charset='utf8')
        cursor = connection.cursor()
        connection.select_db('NasDb')
        try:
            sql = "update user set password=%s,pwdchanged=%s where username=%s"
            sqldata = (newpassword1, 'false', username)
            cursor.execute(sql, sqldata)
            connection.commit()
            connection.close()
            synpassword(username, newpassword1)
            return HttpResponse(
                '<script>window.onload=function(){alert("更新密码成功!");window.location.href=\'/index\'}</script>')
        except:
            return HttpResponse(
                '<script>window.onload=function(){alert("更新密码失败，发生异常!");window.history.back(-1);}</script>')
def managepage(data):
    temp = '<table class="table" style="width:800px;">'
    temp += '<tr>'
    temp += u'<td><lable>访问权限控制</lable></td>'
    temp += u'<td><lable>用户密码更改</lable></td>'
    temp += u'<td><lable>已更改初始密码</lable></td>'
    temp += u'<td><lable>一键删除用户</lable></td>'
    temp += '</tr>'
    for user in data:
        temp += '<tr>'
        temp += '<td><a href="/permission?username=' + user[1] + '&path=/home"><span>' + user[1] + '</span></a>'
        temp += '<td><a href="/root?username=' + user[1] + '"><span>' + user[2] + '</span></a>'
        temp += '<td><lable>' + user[3] + '</lable></td>'
        temp += '<td><a href="/delete?username=' + user[1] + u'"><span>删除</span></a>'
        temp += '</tr>'
    temp += '</table>'
    return temp
def main(request):
    username=request.session["username"]
    path = request.GET.get('path')
    tree = directorytree(path,username)
    data = tree.traverse()
    temp = []
    if data.has_key('subdic'):
        for node in data['subdic']:
            if node['permission'] == u'隐藏':
                continue
            temp.append(node)
    data['subdic'] = temp
    data['logintime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data['username']=username
    result = {}
    result['html'] =data
    if request.session.has_key("mobile"):
        data['logintime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data['username'] = 'root'
        result = {"success": True, "error": "", "msg": "", "errorCode": 0, "data": data}
        return HttpResponse(json.dumps(result).decode("unicode-escape"))
    return render(request, "main.html", {"data": result})
def manage(request):
    username = request.session["username"]
    # if username != 'root':
    #     if request.session.has_key("mobile"):
    #         result = {"success": False, "error": "您不是管理员用户!", "msg": "", "errorCode": 3, "data":{}}
    #         return HttpResponse(json.dumps(result))
    #     return HttpResponseRedirect('/index')
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    sql = "select * from user"
    cursor.execute(sql)
    results = cursor.fetchall()
    users = []
    for user in results:
        if user[1] != 'root':
            users.append(user)
    result = {}
    result['html'] = managepage(users)
    result['users']=users
    result['username'] = request.session["username"]
    result['logintime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if request.session.has_key("mobile"):
        temp = result
        del temp["html"]
        users=temp["users"]
        temp["users"]=[]
        for item in users:
            data={"username":item[1],"changed":item[3]}
            temp["users"].append(data)
        result = {"success": True, "error": "", "msg": "用户信息", "errorCode": 0, "data": temp}
        return HttpResponse(json.dumps(result))
    return render(request, "manage.html", {"data": result})
def index(request):
    if request.method == 'GET':
        if request.session.has_key("username"):
            return HttpResponseRedirect('/main?path=/home')
        if request.session.has_key("mobile"):
            result = {"success": True, "error": "", "msg": "您需要登录。", "errorCode": 0, "data": {}}
            request.session['mobile'] = True
            return HttpResponse(json.dumps(result))
        return render(request, "login.html")
