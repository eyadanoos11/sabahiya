with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# إضافة الاستيرادات
if 'from fastapi import WebSocket' not in c and 'WebSocket' not in c.split('\n')[0]:
    c = c.replace(
        'from fastapi import FastAPI, Request, Form, UploadFile, File',
        'from fastapi import FastAPI, Request, Form, UploadFile, File, WebSocket, WebSocketDisconnect'
    )

# إضافة مسار صفحة الرسم + WebSocket
if '/draw' not in c:
    route = '''
# ==== لوحة الرسم المشتركة ====
connected_clients = set()

@app.get("/draw", response_class=HTMLResponse)
async def draw_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    users = load_users()
    user = users.get(request.session["user"], {})
    return templates.TemplateResponse(request=request, name="draw.html", context={"user": user})

@app.websocket("/ws/draw")
async def websocket_draw(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # إخبار الجميع بعدد المتصلين
        for client in connected_clients:
            try:
                await client.send_json({"type": "count", "count": len(connected_clients)})
            except:
                pass
        while True:
            data = await websocket.receive_json()
            # بث الرسم للجميع عدا المرسل
            for client in connected_clients:
                if client != websocket:
                    try:
                        await client.send_json(data)
                    except:
                        pass
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        for client in connected_clients:
            try:
                await client.send_json({"type": "count", "count": len(connected_clients)})
            except:
                pass
    except Exception:
        connected_clients.discard(websocket)

uvicorn.run(app'''
    c = c.replace('uvicorn.run(app', route, 1)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('✅ تم إضافة WebSocket للرسم في main.py')
