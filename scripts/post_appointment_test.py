import json, urllib.request, urllib.error
url='http://localhost:8000/api/appointments'
payload={
    'start_dt':'2025-11-20T10:00:00',
    'end_dt':'2025-11-20T11:00:00',
    'room_id':1,
    'patient_id':1,
    'student_id':4,
    'supervisor_id':2,
    'notes':'Teste via script'
}
data=json.dumps(payload).encode('utf-8')
req=urllib.request.Request(url,data,headers={'Content-Type':'application/json'},method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        body=resp.read().decode('utf-8')
        print('STATUS', resp.status)
        print(body)
except urllib.error.HTTPError as e:
    try:
        err=e.read().decode('utf-8')
    except:
        err=str(e)
    print('HTTP ERROR', e.code)
    print(err)
except Exception as ex:
    print('EXCEPTION', ex)
