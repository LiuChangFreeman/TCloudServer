#encoding=utf-8
import re
import MySQLdb
from Main.views import *
class ConfNode(object):
    def __init__(self,name='',path='',comment='',browseable='',public='',guest='',rd='',wr='',writelist=[],validusers=[],invalidusers=[],readlist=[]):
        self.name=name
        self.path=path
        self.comment=comment
        self.browseable=browseable
        self.public=public
        self.guest=guest
        self.rd=rd
        self.wr=wr
        self.writelist=writelist
        self.readlist=readlist
        self.validusers=validusers
        self.invalidusers=invalidusers
    def readconf(self,conf):
        items=re.findall('.+?(?=\n)',conf,flags=re.DOTALL)
        for item in items:
            if item=='\n':
                pass
            elif '[' in item and ']' in item:
                self.name=re.findall('(?<=\[).+?(?=\])',item)[0]
            else:
                key=re.search(r'\t(.+?) = (.*)',item).group(1)
                value=re.search(r'\t(.+?) = (.*)',item).group(2)
                if key=='path':
                    self.path=value
                if key=='comment':
                    self.comment=value
                if key=='browseable':
                    self.browseable=value
                if key=='public':
                    self.public=value
                if key=='read only':
                    self.rd=value
                if key=='guest ok':
                    self.guest=value
                if key=='writeable':
                    self.wr=value
                if key=='write list':
                    self.writelist=value.split(',')
                if key=='read list':
                    self.readlist=value.split(',')
                if key=='valid users':
                    self.validusers=value.split(',')
                if key=='invalid users':
                    self.invalidusers=value.split(',')
        if self.name=='home':
            self.writelist=getusers()
    def writeconf(self):
        temp=''
        temp+='['+self.name+']\n'
        temp+='\tpath = '+self.path+'\n'
        if self.comment !='':
            temp += '\tcomment = ' + self.comment + '\n'
        if self.browseable !='':
            temp += '\tbrowseable = ' + self.browseable + '\n'
        if self.public !='':
            temp += '\tpublic = ' + self.public + '\n'
        if self.guest !='':
            temp += '\tguest ok = '+self.guest+'\n'
        if self.rd !='':
            temp += '\tread only = ' + self.rd + '\n'
        if self.wr !='':
            temp += '\twriteable = ' + self.wr + '\n'
        # if self.name!='share':
        #     temp += '\tcreate mask = 0766\n'
        #     temp += '\tforce create mode = 0766\n'
        #     temp += '\tdirectory mask = 0777\n'
        #     temp += '\tforce directory mode = 0777 \n'
        #     temp += '\tdirectory security mask = 0777\n'
        #     temp += '\tforce directory security mode = 0777\n'
        if len(self.writelist)>0:
            temp += '\twrite list = '
            for user in self.writelist:
                temp += str(user)+','
            temp=temp[:-1]
            temp+='\n'
        if len(self.readlist)>0:
            temp += '\tread list = '
            for user in self.readlist:
                temp += str(user)+','
            temp=temp[:-1]
            temp+='\n'
        if len(self.validusers)>0:
            temp += '\tvalid users = '
            for user in self.validusers:
                temp += str(user)+','
            temp=temp[:-1]
            temp+='\n'
        if len(self.invalidusers)>0:
            temp += '\tinvalid users = '
            for user in self.invalidusers:
                temp += str(user)+','
            temp=temp[:-1]
            temp+='\n'
        return temp+'\n'
def getusers():
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    sql = "select username from user"
    cursor.execute(sql)
    results = cursor.fetchall()
    temp=[]
    for user in results:
        temp.append(user[0])
    return temp
def changepermission(path,username,permission):
    conf = open('/etc/samba/smb.conf', 'r').read()
    blocks = re.findall('\[.+?\n\n', conf, flags=re.DOTALL)
    NodeList=[]
    result=''
    for i in range(len(blocks)):
        if i<2:
            result+=blocks[i]
        else:
            temp = ConfNode()
            temp.readconf(blocks[i])
            NodeList.append(temp)
    Target=ConfNode()
    for Node in NodeList:
        if Node.path==path:
            Target=Node
            continue
        result+=Node.writeconf()
    if permission == u"释放":
        pass
    else:
        if permission == u"独占":
            templist=[]
            templist.append(username)
            templist.append('root')
            Target.name=path.split('/')[-1]
            Target.path=path
            Target.validusers = templist
            Target.public = 'no'
            Target.browseable = 'yes'
            Target.guest = 'no'
            Target.wr = 'yes'
            Target.readlist = templist
            Target.writelist = templist
            Target.invalidusers = []
        if permission == u"只读":
            if findpermission(path,username)==u'独占':
                Target.writelist = getusers()
                Target.validusers = getusers()
                Target.readlist = getusers()
            Target.name=path.split('/')[-1]
            Target.path=path
            Target.public = 'no'
            Target.browseable = 'yes'
            Target.guest = 'no'
            Target.wr = 'no'
            Target.rd='yes'
            Target.invalidusers = []
            if len(Target.writelist)==0:
                Target.writelist = getusers()
                Target.validusers = getusers()
                Target.readlist = getusers()
            if username in  Target.writelist:
                Target.writelist.remove(username)
        if permission == u"读写":
            if findpermission(path,username)==u'独占':
                Target.writelist = getusers()
                Target.validusers = getusers()
                Target.readlist = getusers()
            Target.name=path.split('/')[-1]
            Target.path=path
            Target.public = 'no'
            Target.browseable = 'yes'
            Target.guest = 'no'
            Target.wr = 'no'
            Target.rd='yes'
            Target.invalidusers = []
            if len(Target.writelist)==0:
                Target.writelist = getusers()
                Target.validusers = getusers()
                Target.readlist = getusers()
            if username not in Target.writelist:
                Target.writelist.append(username)
        result +=Target.writeconf()
    file=open('/etc/samba/smb.conf','wb+')
    file.write(result)
    file.close()
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    sql = "select * from permission where username='%s'" % username
    cursor.execute(sql)
    results = cursor.fetchall()
    flag = False
    for row in results:
        if row[0] == username and row[1] == path:
            if permission==u'释放':
                sql = "delete from permission where path='%s'"%path
                cursor.execute(sql)
            elif permission==u'独占':
                sql = "delete from permission where path='%s'" % path
                cursor.execute(sql)
                sql = "insert into permission values(%s,%s,%s)"
                sqldata = (username, path, permission)
                cursor.execute(sql, sqldata)
            else:
                sql = "update permission set permission=%s where path=%s and username=%s"
                sqldata = (permission, path,username)
                cursor.execute(sql, sqldata)
                if findpermission(path,username)==u'独占':
                    users = getusers()
                    users.remove(username)
                    for user in users:
                        sql = "insert into permission values(%s,%s,%s)"
                        sqldata = (user, path, u'读写')
                        cursor.execute(sql, sqldata)
            connection.commit()
            connection.close()
            flag = True
            break
    if not flag:
        if permission == u'独占':
            sql = "delete from permission where path='%s'" % path
            cursor.execute(sql)
        sql = "insert into permission values(%s,%s,%s)"
        sqldata = (username, path, permission)
        cursor.execute(sql, sqldata)
        if permission==u'读写' or permission==u'只读':
            users=getusers()
            users.remove(username)
            for user in users:
                sql = "insert into permission values(%s,%s,%s)"
                sqldata = (user,path, u'读写')
                cursor.execute(sql, sqldata)
        connection.commit()
        connection.close()
    return True
def SetPermission(path,username,permission):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='545269649', port=3306, use_unicode=1,
                                 charset='utf8')
    cursor = connection.cursor()
    connection.select_db('NasDb')
    sql = "delete from permission where username='%s' and path='%s'" % (username, path)
    cursor.execute(sql)
    if permission == u'隐藏'or permission == u'只读':
        sql = "insert into permission values(%s,%s,%s)"
        sqldata = (username, path, permission)
        cursor.execute(sql, sqldata)
    connection.commit()
    connection.close()
    return