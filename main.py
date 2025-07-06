import os
import time
import random
import requests
import threading
from string import ascii_lowercase, digits
from queue import Queue
import sys
import datetime
import itertools
from flask import Flask
from threading import Thread

# إعدادات التيلجرام - تم تعيينها بشكل دائم
TELEGRAM_TOKEN = '7736686621:AAHPdUjlbZN4y4E7DzaHTkUanfThLH4Rx2E'
TELEGRAM_CHAT_ID = '7123174825' 

# بيانات الهواتف
PHONES = [
    # هواوي (4 هواتف)
    {"brand": "Huawei", "model": "P30 Pro", "user_agent": "Mozilla/5.0 (Linux; Android 10; LIO-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"},
    {"brand": "Huawei", "model": "Mate 40", "user_agent": "Mozilla/5.0 (Linux; Android 11; TAS-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36"},
    {"brand": "Huawei", "model": "P40 Lite", "user_agent": "Mozilla/5.0 (Linux; Android 10; JNY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36"},
    {"brand": "Huawei", "model": "Nova 7i", "user_agent": "Mozilla/5.0 (Linux; Android 10; JEF-NX9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"},
    
    # شاومي (2 هواتف)
    {"brand": "Xiaomi", "model": "Redmi Note 10", "user_agent": "Mozilla/5.0 (Linux; Android 11; M2004J19C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"},
    {"brand": "Xiaomi", "model": "Mi 11", "user_agent": "Mozilla/5.0 (Linux; Android 12; M2011K2G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36"},
    
    # آيفون (2 هواتف)
    {"brand": "iPhone", "model": "iPhone 13", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"},
    {"brand": "iPhone", "model": "iPhone 12 Pro", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1"},
    
    # هواتف إضافية (2 هواتف)
    {"brand": "Samsung", "model": "Galaxy S21", "user_agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36"},
    {"brand": "Oppo", "model": "Reno 6", "user_agent": "Mozilla/5.0 (Linux; Android 11; CPH2237) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"}
]

# إعدادات التنسيق
COLORS = {
    "header": "\033[92m",
    "success": "\033[92m",
    "error": "\033[91m",
    "warning": "\033[93m",
    "info": "\033[94m",
    "reset": "\033[0m"
}

# أحرف وأرقام للنقاط
INSTA_CHARS = ascii_lowercase + digits  # فقط أحرف وأرقام (بدون نقاط)
CHARS_LENGTH = len(INSTA_CHARS)

# متغيرات لتتبع حالة البرنامج
total_checked = 0
start_time = time.time()
last_clean_time = time.time()

# إنشاء تطبيق Flask لـ Keep-Alive
app = Flask('')

@app.route('/')
def home():
    return "Instagram Username Hunter is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def start_keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_header():
    clear_screen()
    print(COLORS["header"] + "=" * 70)
    print("أداة البحث عن يوزرات إنستقرام المتاحة".center(70))
    print(f"المطور: MEHEMT".center(70))
    print("نظام فحص لا نهائي لجميع اليوزرات الرباعية".center(70))
    print("=" * 70 + COLORS["reset"])
    print(f"{COLORS['info']}[*] عدد اليوزرات المفحوصة: {total_checked:,}{COLORS['reset']}")
    print(f"{COLORS['info']}[*] مدة التشغيل: {datetime.timedelta(seconds=int(time.time()-start_time))}{COLORS['reset']}")
    print(f"{COLORS['info']}[*] آخر تنظيف للشاشة: {datetime.timedelta(seconds=int(time.time()-last_clean_time))} مضت{COLORS['reset']}\n")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            return True, "تم الإرسال بنجاح ✅"
        return False, f"فشل الإرسال: {response.status_code}"
    except Exception as e:
        return False, f"خطأ في الإرسال: {str(e)}"

def send_user_to_telegram(username):
    """ إرسال يوزر واحد إلى التيلجرام مع تأكيد الإرسال """
    message = f"يوزر من MEHEMT\n\n——⟩ <code>{username}</code>\n\nالمطور: @IllIllIlllIlIll"
    return send_telegram(message)

def get_random_cookies():
    """ توليد كوكيز عشوائية للطلب """
    csrftoken = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
    mid = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnoprstuvwxyz0123456789', k=30))
    ig_did = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8)) + '-' + \
             ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + '-' + \
             ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + '-' + \
             ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + '-' + \
             ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
    return {
        'csrftoken': csrftoken,
        'mid': mid,
        'ig_did': ig_did
    }

def check_username(username):
    """ التحقق من اسم المستخدم باستخدام طريقة إنشاء حساب - أكثر موثوقية """
    cookies = get_random_cookies()
    phone = random.choice(PHONES)
    
    headers = {
        'Host': 'www.instagram.com',
        'content-length': '85',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': '0',
        'sec-ch-ua-mobile': '?0',
        'x-instagram-ajax': ''.join(random.choices('0123456789abcdef', k=12)),
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'x-asbd-id': '198387',
        'user-agent': phone['user_agent'],
        'x-csrftoken': cookies['csrftoken'],
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.instagram.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.instagram.com/accounts/emailsignup/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-IQ,en;q=0.9',
    }
    
    email = 'a' + ''.join(random.choices(ascii_lowercase, k=10)) + '@gmail.com'
    data = {
        'email': email,
        'username': username,
        'first_name': '',
        'opt_into_one_tap': 'false'
    }
    
    try:
        response = requests.post(
            'https://www.instagram.com/accounts/web_create_ajax/attempt/',
            headers=headers,
            data=data,
            cookies=cookies,
            timeout=15
        )
        
        if response.status_code != 200:
            return False, phone
        
        response_json = response.json()
        
        if 'errors' in response_json:
            if 'username' in response_json['errors']:
                # اسم المستخدم غير متاح
                return False, phone
        
        # إذا لم يكن هناك خطأ في اليوزر، فهذا يعني أنه متاح
        return True, phone
    except:
        return False, phone

def worker(username_queue, results_list, lock, thread_id):
    """ دالة الخيط لفحص اليوزرات """
    global total_checked
    
    while True:
        username = username_queue.get()
        if username is None:  # إشارة لإنهاء الخيط
            username_queue.task_done()
            break
            
        available, phone = check_username(username)
        
        with lock:
            total_checked += 1
            
            # تحديث الشاشة كل 1000 يوزر
            if total_checked % 1000 == 0:
                show_header()
            
            if available:
                # إرسال اليوزر إلى التيلجرام فوراً مع تأكيد الإرسال
                send_success, send_message = send_user_to_telegram(username)
                
                if send_success:
                    send_status = f"{COLORS['success']}✅ تم الإرسال{COLORS['reset']}"
                else:
                    send_status = f"{COLORS['error']}❌ فشل الإرسال: {send_message}{COLORS['reset']}"
                
                # إضافة اليوزر للنتائج مع حالة الإرسال
                results_list.append((username, send_success, send_message))
                
                print(f"{COLORS['success']}[+] {username} - متاح | {send_status} {COLORS['reset']} | الهاتف: {phone['brand']} {phone['model']}")
            else:
                print(f"{COLORS['error']}[-] {username} - غير متاح {COLORS['reset']} | الهاتف: {phone['brand']} {phone['model']}")
        
        username_queue.task_done()
        time.sleep(random.uniform(0.5, 1.5))  # تأخير عشوائي لتجنب الحظر

def generate_quad_usernames():
    """ توليد جميع اليوزرات الرباعية الممكنة (4 أحرف) """
    chars = INSTA_CHARS
    for combo in itertools.product(chars, repeat=4):
        yield ''.join(combo)

def start_search(threads):
    """ بدء البحث في حلقة لا نهائية """
    global total_checked, last_clean_time
    
    # إعداد خيوط العمل
    username_queue = Queue()
    results = []
    lock = threading.Lock()
    
    # بدء الخيوط
    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=worker, args=(username_queue, results, lock, i))
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    # توليد جميع اليوزرات الرباعية
    username_generator = generate_quad_usernames()
    
    # حلقة لا نهائية للفحص
    cycle_count = 0
    while True:
        cycle_count += 1
        print(f"{COLORS['info']}[*] بدأ دورة الفحص رقم: {cycle_count}{COLORS['reset']}")
        
        # إضافة اليوزرات إلى الطابور
        added_count = 0
        for username in username_generator:
            username_queue.put(username)
            added_count += 1
            
            # تنظيف الشاشة كل 5 ساعات (18000 ثانية)
            current_time = time.time()
            if current_time - last_clean_time >= 18000:
                clear_screen()
                last_clean_time = current_time
                show_header()
        
        # انتظار انتهاء جميع المهام
        username_queue.join()
        
        print(f"{COLORS['info']}[*] تم الانتهاء من دورة الفحص رقم: {cycle_count}{COLORS['reset']}")
        print(f"{COLORS['info']}[*] إجمالي اليوزرات المفحوصة: {total_checked:,}{COLORS['reset']}")
        
        # إعادة تهيئة المولد للدورة التالية
        username_generator = generate_quad_usernames()
        
        # تأخير قبل بدء الدورة التالية
        time.sleep(5)

def main():
    global start_time, last_clean_time
    
    # بدء خادم Keep-Alive
    start_keep_alive()
    
    # إعداد وقت البدء
    start_time = time.time()
    last_clean_time = start_time
    
    # إرسال رسالة بدء التشغيل
    welcome_msg = "<b>🚀 تم بدء أداة البحث عن يوزرات إنستقرام بنجاح!</b>"
    success, message = send_telegram(welcome_msg)
    
    # عرض الواجهة
    clear_screen()
    show_header()
    
    # إعدادات ثابتة للبحث
    THREAD_COUNT = 20  # عدد الخيوط
    
    # بدء البحث في حلقة لا نهائية
    start_search(THREAD_COUNT)

if __name__ == "__main__":
    main()