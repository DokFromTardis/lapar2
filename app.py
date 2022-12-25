
import random
import qrcode
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import time
import threading
import datetime
import os
import smtplib, ssl
def create_rassilku(text):
    cursor.execute("SELECT email, username FROM users")
    for i in cursor.fetchall():
        port = 465  # For SSL
        smtp_server = "smtp.mail.ru"
        sender_email = "noreply@laparvape.ru"  # Enter your address
        receiver_email = i[0]
        password = "bjRr20tQpHchjsh771fj"
        msg = MIMEMultipart()
        msg['Subject'] = 'Рассылка'
        msg['From'] = "noreply@laparvape.ru"
        msg['To'] = i[0]
        text = MIMEText(f'Здравствуйте, {i[1]}!\n' + text)
        msg.attach(text)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
create_rassilku("testim")
def get_promo_code(num_chars):
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(0, num_chars):
     slice_start = random.randint(0, len(code_chars) - 1)
     code += code_chars[slice_start: slice_start + 1]
    return code
def job():
    cursor.execute("SELECT email from users WHERE date = %s", (datetime.datetime.today().strftime('%Y-%m-%d'), ))
    for i in cursor.fetchall():
        prom2 = get_promo_code(6)
        img = qrcode.make(f'http://localhost:5000/activateqr/{prom2}')
        img.save(f'{prom2}.png')
        cursor.execute("UPDATE users SET second_promo = %s WHERE email = %s", (prom2, i[0]))
        import smtplib, ssl
        port = 465  # For SSL
        smtp_server = "smtp.mail.ru"
        sender_email = "noreply@laparvape.ru"  # Enter your address
        receiver_email = i[0]
        password = "bjRr20tQpHchjsh771fj"
        msg = MIMEMultipart()
        msg['Subject'] = 'С днём рождения!'
        msg['From'] = "noreply@laparvape.ru"
        msg['To'] = i[0]
        with open(f'{prom2}.png', 'rb') as f:
            img_data = f.read()
        image = MIMEImage(img_data, name="Промокод")
        text = MIMEText("В честь вашего дня рождения дарим промокод на скидку в 20%! Покажите этот QR-код нашему продавцу. Ни в коем случае не сканируйте данный QR код, в таком случае он станет не действительным")
        msg.attach(image)
        msg.attach(text)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        cursor.execute("UPDATE users SET date = date + interval '1 year' WHERE email = %s", (i[0], ))
        conn.commit()
        os.remove(f'{prom2}.png')
def fubction():
    while True:
        job()
        time.sleep(60) # wait one minute
x = threading.Thread(target=fubction)
x.start()
@app.route("/activateqr/<code>")
def activate(code):
    cursor.execute("SELECT * from users WHERE first_promo = %s", (code,))
    rows = cursor.fetchall()
    cursor.execute("SELECT * from users WHERE second_promo = %s", (code, ))
    rows2 = cursor.fetchall()
    if rows:
        variable2 = "first_promo"
    elif rows2:
        variable2 = "second_promo"
    if rows or rows2:
        cursor.execute("UPDATE users SET " + variable2 + "= '' WHERE " + variable2 + "= %s", (code,))
        conn.commit()
        return "Промокод успешно активирован"
    else:
        return "Не удалось найти промокод"
@app.route("/register", methods=['POST', 'GET'])
def registration():
    if not session["registrated"]:
        if request.method == "GET":
            return render_template("signup.html")
        else:
            cursor.execute("SELECT * from users WHERE email = %s", (request.form.get("email"), ))
            if cursor.fetchall():
                return "Уже есть пользователь с такой почтой"
            prom = get_promo_code(6)
            img = qrcode.make(f'http://localhost:5000/activateqr/{prom}')
            img.save(f'{prom}.png')
            cursor.execute("INSERT into users(username, email, password, date, first_promo) VALUES (%s,%s,%s,TO_DATE(%s, 'DD/MM/YYYY'), %s)", (request.form.get("username"), request.form.get("email"), request.form.get("password"), request.form.get("dobUk")[:-4] +  str(datetime.date.today().year) , prom))
            conn.commit()
            import smtplib, ssl
            port = 465  # For SSL
            smtp_server = "smtp.mail.ru"
            sender_email = "noreply@laparvape.ru"  # Enter your address
            receiver_email = request.form.get("email")# Enter receiver address
            password = "bjRr20tQpHchjsh771fj"
            msg = MIMEMultipart()
            msg['Subject'] = 'Успешная регистрация'
            msg['From'] = "noreply@laparvape.ru"
            msg['To'] = request.form.get("email")
            with open(f'{prom}.png', 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name="Промокод")
            text = MIMEText("Покажите этот QR-код нашему продавцу. Ни в коем случае не сканируйте данный QR код, в таком случае он станет не действительным")
            msg.attach(image)
            msg.attach(text)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            os.remove(f'{prom}.png')
            session["registrated"] = True
            return "<h1>Успешно!</h1><h3>Проверьте вашу почту</h3><a href='www.http://laparvape.ru'> Вернутся на главную </a>"
    else:
        return "Вы уже зарегистрированны!"
app.run()
