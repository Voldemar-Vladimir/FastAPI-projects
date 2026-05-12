import uvicorn
import datetime
from fastapi import FastAPI, HTTPException, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from models import SessionLocal, Booking
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
bootstrap = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'

homes = [
    {"id": 1, "price_per_day": 3000, "distance_to_sea": 300, "rooms": 3,
     "pool": True, "tv": True, "rating": 4.99,
     "img": "static/img/home2.png"},
    {"id": 2, "price_per_day": 2000, "distance_to_sea": 600, "rooms": 2,
     "pool": False, "tv": True, "rating": 4.89,
     "img": "static/img/home1.png"}
]

# ===================== ГЛАВНАЯ СТРАНИЦА =====================
@app.get("/", response_class=HTMLResponse)
def index():
    cards = ""
    for h in homes:
        pool = "✅" if h["pool"] else "❌"
        tv = "✅" if h["tv"] else "❌"
        cards += f"""
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <img src="{h['img']}" class="card-img-top" alt="Домик {h['id']}">
                <div class="card-body">
                    <h5>Домик №{h['id']}</h5>
                    <ul>
                        <li>💸 Цена: <strong>{h['price_per_day']} ₽/сут</strong></li>
                        <li>🏖️ До моря: {h['distance_to_sea']} м</li>
                        <li>🛏️ Комнат: {h['rooms']}</li>
                        <li>🏊 Бассейн: {pool}</li>
                        <li>📺 Телевизор: {tv}</li>
                        <li>💯 Оценка: {h['rating']}</li>
                    </ul>
                    <a href="/booking?home_id={h['id']}" class="btn btn-success">Забронировать</a>
                </div>
            </div>
        </div>"""
    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
    <title>Домики у моря</title>{bootstrap}</head>
    <body><div class="container py-4"><h1>🏡 Домики у моря</h1><div class="row">{cards}</div></div></body></html>"""
    return HTMLResponse(content=html)

# ===================== ФОРМА БРОНИРОВАНИЯ =====================
@app.get("/booking", response_class=HTMLResponse)
def booking_form(request: Request, home_id: int = None):
    # Найдём цену выбранного дома, чтобы передать в скрытое поле
    price_per_day = 3000  # значение по умолчанию
    if home_id:
        chosen = next((h for h in homes if h["id"] == home_id), None)
        if chosen:
            price_per_day = chosen["price_per_day"]

    return HTMLResponse(content=f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
    <title>Бронирование</title>{bootstrap}</head>
    <body><div class="container py-4"><h1>📅 Бронирование</h1>
    <form action="/booking" method="post" id="bookingForm">
        <input type="hidden" name="home_id" value="{home_id}">
        <!-- Скрытое поле с ценой за сутки – нужно для расчёта -->
        <input type="hidden" id="price_per_day" value="{price_per_day}">
        <div class="mb-3"><label>Заезд: <input type="date" name="check_in" id="check_in" class="form-control" required></label></div>
        <div class="mb-3"><label>Выезд: <input type="date" name="check_out" id="check_out" class="form-control" required></label></div>
        <div class="mb-3"><label>Имя: <input type="text" name="name" class="form-control" required></label></div>
        <div class="mb-3"><label>Телефон: <input type="tel" name="phone" class="form-control" required></label></div>
        <div class="mb-3"><label>Email: <input type="email" name="email" class="form-control"></label></div>
        <h5>Дополнительно:</h5>
        <div class="form-check"><input type="checkbox" name="mini_bar" class="form-check-input service" data-price="4000">🍷 Мини-бар 4000₽</div>
        <div class="form-check"><input type="checkbox" name="massage" class="form-check-input service" data-price="2000">💆 Массаж 2000₽</div>
        <div class="form-check"><input type="checkbox" name="wifi" class="form-check-input service" data-price="350">📡 Интернет 350₽</div>
        <div class="form-check"><input type="checkbox" name="tv" class="form-check-input service" data-price="500">📺 Телевизор 500₽</div>
        <div class="form-check"><input type="checkbox" name="transfer" class="form-check-input service" data-price="1000">🚗 Трансфер 1000₽</div>
        <div class="mt-3"><strong>💰 Итого: <span id="totalPrice">0</span> ₽</strong></div>
        <button type="submit" class="btn btn-success mt-3">Забронировать</button>
    </form></div>
    <script>
    function calculate() {{
        let checkIn = document.getElementById('check_in').value;
        let checkOut = document.getElementById('check_out').value;
        let pricePerDay = parseInt(document.getElementById('price_per_day').value);
        let days = 0;
        if (checkIn && checkOut) {{
            let dateIn = new Date(checkIn);
            let dateOut = new Date(checkOut);
            if (dateOut > dateIn) {{
                days = Math.floor((dateOut - dateIn) / (1000 * 60 * 60 * 24));
            }}
        }}
        let total = days * pricePerDay;
        // Добавляем выбранные услуги
        document.querySelectorAll('.service:checked').forEach(function(cb) {{
            total += parseInt(cb.getAttribute('data-price'));
        }});
        document.getElementById('totalPrice').innerText = total > 0 ? total : 0;
    }}
    // Пересчёт при изменении дат
    document.getElementById('check_in').addEventListener('input', calculate);
    document.getElementById('check_out').addEventListener('input', calculate);
    // Пересчёт при клике на любой чекбокс услуги
    document.querySelectorAll('.service').forEach(function(cb) {{
        cb.addEventListener('change', calculate);
    }});
    // Первоначальный расчёт
    calculate();
    </script>
    </body></html>""")

# ===================== СТРАНИЦА УСПЕХА =====================
@app.get("/success", response_class=HTMLResponse)
def success():
    return HTMLResponse(content=f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Спасибо</title>{bootstrap}</head>
    <body><div class="container py-5 text-center">
        <h1>✅ Заказ принят!</h1>
        <p>Мы свяжемся с вами.</p>
        <a href="/" class="btn btn-primary">На главную</a>
    </div></body></html>""")

# ===================== ПОЛУЧЕНИЕ СЕССИИ БД =====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===================== ОБРАБОТКА POST-БРОНИ =====================
@app.post("/booking")
def create_form(
    home_id: int = Form(...),
    check_in: datetime.date = Form(...),
    check_out: datetime.date = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    mini_bar: bool = Form(False),
    massage: bool = Form(False),
    wifi: bool = Form(False),
    tv: bool = Form(False),
    transfer: bool = Form(False),
    db: Session = Depends(get_db)
):
    # Определяем цену дома
    chosen = next((h for h in homes if h["id"] == home_id), None)
    if not chosen:
        raise HTTPException(status_code=404, detail="Дом не найден")
    days = (check_out - check_in).days
    if days <= 0:
        raise HTTPException(status_code=400, detail="Дата выезда должна быть позже заезда")
    price = days * chosen["price_per_day"]
    if mini_bar: price += 4000
    if massage: price += 2000
    if wifi: price += 350
    if tv: price += 500
    if transfer: price += 1000

    booking = Booking(
        home_id=home_id,
        check_in=check_in,
        check_out=check_out,
        name=name,
        phone=phone,
        email=email,
        mini_bar=mini_bar,
        massage=massage,
        wifi=wifi,
        tv=tv,
        transfer=transfer,
        total_price=price
    )
    db.add(booking)
    db.commit()
    return RedirectResponse("/success", status_code=303)

# ===================== API ДЛЯ ОДНОГО ДОМА =====================
@app.get("/homes/{home_id}")
def show_home(home_id: int):
    for home in homes:
        if home["id"] == home_id:
            return home
    raise HTTPException(status_code=404, detail="Дом не найден")

if __name__ == "__main__":
    uvicorn.run(app)