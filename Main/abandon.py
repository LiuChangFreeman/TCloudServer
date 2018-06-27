def tofullhtml(data):
    temp = '<li><span class="' + data['type'] + '" >' + data['name'] + '</span>'
    temp = temp + '<a href="/main?path=' + data['path'] + '"/>'
    subdic = []
    if data.has_key('subdic'):
        subdic = data['subdic']
    if len(subdic) > 0:
        temp = temp + '<ul>'
        for item in subdic:
            temp = temp + tofullhtml(item)
        temp = temp + '</ul>'
    temp = temp + '</li>'
    return temp
def tohtml(data):
    temp = '<form action="/multiple" method="post">'
    temp += '<div>'
    temp += u'<div style="width:200px;display:inline-block;text-align:center;border:1px solid black;"><input type="submit" name="submit" value="删除"></div>'
    temp += u'<div style="width:200px;display:inline-block;text-align:center;border:1px solid black;"><input type="submit" name="submit" value="下载"></div>'
    temp += '<div>'
    temp += '<li><div>'
    if data['type'] == 'folder':
        temp += '<a href="/main?path=' + data['path'] + '">'
        temp += '<span class="' + data['type'] + '" >' + data['name'] + '</span></a></div>'
    subdic = []
    if data.has_key('subdic'):
        subdic = data['subdic']
    if len(subdic) > 0:
        temp += '<ul style="width:500px;border:1px solid black;">'
        for item in subdic:
            temp += '<li><div><div style="width:350px;display:inline-block">'
            if item['type'] == 'folder':
                temp += '<a href="/main?path=' + item['path'] + '">'
            if item['type'] == 'file':
                temp += '<a href="/download?path=' + item['path'] + '">'
            temp += '<span class="' + item['type'] + '" >' + item['name'] + '</span>'
            temp += '</a></div>'
            temp += '<div style="width:50px;display:inline-block">'
            temp += '<input type="checkbox" name="path" value="' + item['path'] + '">'
            temp += '</div></div></li>'
        temp += '</form></ul>'
    temp += '</li>'
    return temp
def managetree(data,username):
    temp = '<li><div>'
    if data['type'] == 'folder':
        temp += '<a href="/main?path=' + data['path'] + '">'
        temp += '<span class="' + data['type'] + '" >' + data['name'] + '</span></a></div>'
    subdic = []
    if data.has_key('subdic'):
        subdic = data['subdic']
    if len(subdic) > 0:
        temp += '<ul style="width:500px;border:1px solid black;">'
        for item in subdic:
            temp += '<li><form action="/permission" method="post"><div><div style="width:350px;display:inline-block">'
            if item['type'] == 'folder':
                temp += '<a href="/permission?path=' + item['path'] + '&username='+username+'">'
            if item['type'] == 'file':
                temp += '<a href="/download?path=' + item['path'] + '">'
            temp += '<span class="' + item['type'] + '" >' + item['name'] + '</span>'
            temp += '</a></div>'
            temp += '<div style="width:50px;display:inline-block">'
            temp += '<input type="button" name="path" value="' + item['path'] + '">'
            temp += '</div>'
            temp += '<div style="width:50px;display:inline-block">'
            temp += '<input type="button" name="path" value="' + item['path'] + '">'
            temp += '</div>'
            temp += '</div></form></li>'
        temp += '</ul>'
    temp += '</li>'
    return temp