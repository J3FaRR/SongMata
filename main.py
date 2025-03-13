from telebot import TeleBot
from kvsqlite.sync import Client
from datetime import datetime
from telebot.types import InlineKeyboardMarkup as mk , InlineKeyboardButton as btn
from timeit import default_timer as timer
import pytz

owner: int = 6700145061 # your id

TOKEN: str = "BOT-TOKEN" #your token

Tho = TeleBot(
    TOKEN,
    parse_mode="markdown",
    skip_pending=True,
    disable_web_page_preview=True,
    num_threads=60
)

db = Client(
    "SongMata.db",
    "users"
    )

chat = Client(
    "SongMata.db",
    "chats"
    )

pr = Client(
    "SongMata.db",
    "private"
    )

if not chat.exists("cast"):
    chat.set(
    "cast",{
        "ask":False,
        "text":None,
        "views":0,
        "chats":[]
        }
    )

z = pytz.timezone('Asia/Baghdad')

channels: list[int | str] = ["@chilly_chilly_chilly_chilly"]

def channel(idu: int) -> str | None:
    channel = ""
    for i in channels:
        try:
            re = Tho.get_chat_member(i,idu)
            if re.status not in ["member","administrator","creator"] and idu != owner:channel+=f'{i}\n'
        except Exception as e:print(e)
    if channel:return channel
    else:return None

def check(idu: int, name: str, username: str) -> list:
    d: str = str(datetime.now(z).date()).replace("-","/")
    t: list = str(datetime.now(z).time()).split(".")[0].split(":")
    h: int = int(t[0])
    m: str = t[1]
    s: str = t[2]
    if h > 12:
        h = h - 12
        td: str = f"[{d} | {h}:{m}:{s} pm]"
    else:
        td: str = f"[{d} | {h}:{m}:{s} am]"
    if not db.exists(f"user_{idu}"):
        db.set(f"user_{idu}",{
            "id":idu,
            "last":{"name":name,"user_name":username},
            "all":{
                "user_names":[(username,td)],
                "names":[(name,td)]
            }
        })
        return ["new"]
    else:
        data: dict = db.get(f"user_{idu}")
        name_old: str = data["last"]["name"]
        username_old: str = data["last"]["user_name"]
        if name_old != name and username_old != username:
            all: dict = data["all"]
            names: list = all["names"]
            user_names: list = all["user_names"]
            names.append((name,td))
            user_names.append((username,td))
            data["all"]["names"] = names
            data["all"]["user_names"] = user_names
            data["last"]["name"] = name
            data["last"]["user_name"] = username
            db.set(f"user_{idu}",data)
            return ["both",name_old,username_old]
        elif name_old != name:
            all: dict = data["all"]
            names:list = all["names"]
            names.append((name,td))
            data["all"]["names"] = names
            data["last"]["name"] = name
            db.set(f"user_{idu}",data)
            return ["name",name_old]
        elif username_old != username:
            all: dict = data["all"]
            user_names:list = all["user_names"]
            user_names.append((username,td))
            data["all"]["user_names"] = user_names
            data["last"]["user_name"] = username
            db.set(f"user_{idu}",data)
            return ["username",username_old]

def NewChat(chat_id: int) -> None:
    chat_info: dict = Tho.get_chat(chat_id)
    chat_name: str = chat_info.title
    chat_username: str = ("@"+str(chat_info.username)).replace("@None","لايوجد")
    link: str = str(chat_info.invite_link).replace("None","لايوجد")
    message: str = '''
* مجموعة جديدة ضافت البوت*

- أسم المجموعة: *{}*
- أيدي المجموعة: *{}*
- يوزر المجموعة: *{}*
- رابط خاص للمجموعة: *{}*
-------------------------------------
'''.format(chat_name, chat_id, chat_username, link)
    Tho.send_message(owner,message)

def cast(msg, text: str, type: str) -> None:
    ids: list[int] = []
    if type == "private":
        keys: list = pr.keys("user_%")
        for id in keys:
            ids.append(pr.get(id[0]))
    elif type == "chats":
        keys: list = chat.keys("chat_%")
        for id in keys:
            ids.append(chat.get(id[0]))
    i ,F ,T = 0,0,0
    start = timer()
    Tho.send_message(
        chat_id = msg.chat.id,
        text=f"""*بدأت الاذاعة:*
عدد المستخدمين : {len(ids)}""")
    for Id in ids:
        i = i+1
        try:
            Tho.send_message(
                Id,
                text
                )
            T = T+1
        except:
            F = F+1
    end = timer()
    ttt = end-start
    Tho.send_message(
                chat_id=msg.chat.id,
                text =f"""*أنتهت الاذاعة:*
عدد المستخدمين : {len(ids)}
نجحت لـ : {T}/{T+F}  -  {round((T/(T+F))*100,2)}%
فشلت لـ : {F}/{T+F}  -  {round((F/(T+F))*100,2)}%
تم الارسال لـ : {round(((T+F)/len(ids))*100,2)}%
استغرقت الاذاعة: {round(ttt/60,1)} دقائق""")
                
@Tho.message_handler(commands=["start"],chat_types=["private"])
def mainF(msg):
    idu: int = msg.from_user.id
    name: str = msg.from_user.full_name
    username: str = msg.from_user.username
    if not pr.exists(f"user_{idu}"):
        pr.set(f"user_{idu}",idu)
    i = channel(idu)
    if i:
        Tho.reply_to(msg,f"*أشترك بالقناة لتتمكن من استخدام البوت\n{i}أشترك وأرجع أرسل /start*")
        check(idu,name,username)
        return
    text: str = """*أهلا {} في البوت*
مهمتي أنبهك اذا احد غيّر أسمه أو يوزره
أرفعني مشرف بالمجموعة وأرسل تفعيل
وتقدر تشوف سجل الاسماء او يوزرات اي عضو بس أرسل الايدي.""".format(name)
    m = mk(row_width=1)
    Thoo = btn("المطور",url=f"tg://user?id={owner}")
    Foqar = btn("ضيفني لكروبك",url=f"https://t.me/{Tho.get_me().username}?startgroup=Commands&admin=ban_users+restrict_members+delete_messages+add_admins+change_info+invite_users+pin_messages+manage_call+manage_chat+manage_video_chats+promote_members")
    m.row(Thoo,Foqar)
    textt: str = '''
*أهلا عزيزي المالك
أرسل /get_file لأرسال التخزين
أرسل /status للحصول على الاحصائيات
رد على رسالة بـ /private_cast لأذاعتها بالخاص
رد على رسالة بـ /group_cast لأذاعتها بالمجموعات بدون loop
أرسل /cancel_group_cast لأنهاء أذاعة الكروبات
رد على الرسالة بـ /group_cast_loop لأذاعة loop
*'''
    if idu == owner:Tho.reply_to(msg,textt)
    Tho.reply_to(msg,text,reply_markup=m)
    check(idu,name,username)

@Tho.message_handler(commands=["cancel_group_cast"])
def cancel_cast(msg):
    idu: int = msg.from_user.id
    if idu != owner:return
    views: int = chat.get("cast")["views"]
    chat.set(
    "cast",{
        "ask":False,
        "text":None,
        "views":0,
        "chats":[]
        }
    )
    Tho.reply_to(msg,"*تم الالغاء\nتم أرسالها في {} كروب*".format(views))

@Tho.message_handler(commands=["group_cast_loop"])
def cast_group_loop(msg):
    idu: int = msg.from_user.id
    if idu != owner:return
    if msg.reply_to_message:
        text: str = msg.reply_to_message.text
        cast(msg,text,"chats")
        return
    else:
        Tho.send_message(msg.chat.id,"*قم بالرد على الرسالة المراد اذاعتها*")

@Tho.message_handler(commands=["private_cast"])
def private_cast(msg):
    idu: int = msg.from_user.id
    if idu != owner:return
    if msg.reply_to_message:
        text: str = msg.reply_to_message.text
        cast(msg,text,"private")
        return
    else:
        Tho.send_message(msg.chat.id,"*قم بالرد على الرسالة المراد اذاعتها*")

@Tho.message_handler(commands=["group_cast"])
def group_cast(msg):
    idu: int = msg.from_user.id
    chat_id: int = msg.chat.id
    if idu != owner:return
    if msg.reply_to_message:
        text: int = msg.reply_to_message.text
        chat.set(
            "cast",{
                "ask":True,
                "chats":[],
                "text":text,
                "views":0
            }
        )
        Tho.reply_to(msg,"*يتم الاذاعة*")
    else:
        Tho.reply_to(msg,"*رد على الرسالة المراد اذاعتها*")

@Tho.message_handler(commands=["get_file"],chat_types=["private"])
def getFile(msg):
    idu: int = msg.from_user.id
    name: str = msg.from_user.full_name
    username: str = msg.from_user.username
    check(idu,name,username)
    if idu != owner:return
    Tho.send_document(idu,open("zang_mata.sqlite","rb"),caption="*قاعدة البيانات*")

@Tho.message_handler(commands=["status"])
def status(msg):
    idu: int = msg.from_user.id
    name: str = msg.from_user.full_name
    username: str = msg.from_user.username
    chats: int = len(chat.keys("chat_%"))
    people: int = len(db.keys("user_%"))
    users: int = len(pr.keys("user_%"))
    Tho.reply_to(msg,f"*قسم الاحصائيات*\n\n- عدد المجموعات: *{chats}*\n- عدد المستخدمين بالخاص: *{users}*\n- عدد الذين تم تخزينهم: *{people}*")
    check(idu,name,username)

@Tho.message_handler(chat_types=["private"])
def mainget(msg):
    iduu: str | int = msg.text
    idu: int = msg.from_user.id
    name: str = msg.from_user.full_name
    username: str = msg.from_user.username
    i = channel(idu)
    if i:
        Tho.reply_to(msg,f"*أشترك بالقناة لتتمكن من استخدام البوت\n{i}أشترك وأرجع أرسل /start*")
        check(idu,name,username)
        return
    if db.exists(f"user_{iduu}"):
        data: dict = db.get(f"user_{iduu}")["all"]
        names_list: list = data["names"]
        usernames_list: list = data["user_names"]
        names: str = ""
        usernames: str = ""
        num: int = 0
        for i in names_list:
            num +=1
            names += f"*{num}.* `{i[1]}` *{i[0]}*\n"
        num: int = 0
        for i in usernames_list:
            num +=1
            usernames += f"*{num}.* `{i[1]}` *@{i[0]}*\n"
        text: str = f"""*👤 السجل الشخصي لـ* [{iduu}](tg://user?id={iduu})
        
*ملاحظة:* التوقيت حسب محافظة *بغداد*
*- Names*
{names}
*- Usernames*
{usernames}
"""
        Tho.reply_to(msg,text)
    else:
        Tho.reply_to(msg,"*هذا المستخدم غير مسجل بقاعدة بيانات البوت او ان الايدي خاطئ*")
    check(idu,name,username)

@Tho.message_handler(commands=["start"],chat_types=["group","supergroup"])
def groups_commands(msg):
    name: str = msg.from_user.full_name
    text: str = """*أهلا {} في البوت*
مهمتي أنبهك اذا احد غيّر أسمه أو يوزره
أرفعني مشرف بالمجموعة وأرسل تفعيل
وتقدر تشوف سجل الاسماء او يوزرات اي عضو بس أرسل الايدي.""".format(name)
    m = mk(row_width=1)
    Thoo = btn("المطور",url=f"tg://user?id={owner}")
    Foqar = btn("ضيفني لكروبك",url=f"https://t.me/{Tho.get_me().username}?startgroup=Commands&admin=ban_users+restrict_members+delete_messages+add_admins+change_info+invite_users+pin_messages+manage_call+manage_chat+manage_video_chats+promote_members")
    m.row(Thoo,Foqar)
    Tho.reply_to(msg,text,reply_markup=m)

@Tho.message_handler(chat_types=["group","supergroup"])
def groups(msg):
    idu: int = msg.from_user.id
    name: str = msg.from_user.full_name
    username: str = msg.from_user.username
    chat_id: int = msg.chat.id
    i = check(idu,name,username)
    if i:
        if i[0] == "name":
            text: str = """*المُستَخدِم* [{}](tg://user?id={})
غيّر أسمهُ مِن *{}* الىٰ *{}*""".format(idu,idu,i[1],name)
            Tho.send_message(chat_id,text)
        elif i[0] == "username":
            text: str = """*المُستَخدِم* [{}](tg://user?id={})
غيّر يوزره مِن *{}* الىٰ *{}*""".format(idu,idu,i[1],username)
            Tho.send_message(chat_id,text)
        elif i[0] == "both":
            text: str = """*المُستَخدِم* [{}](tg://user?id={})
غيّر يوزره و أسمه
الاسم القديم *{}*
اليوزر القديم *{}*""".format(idu,idu,i[1],i[2])
            Tho.send_message(chat_id,text)
    ask: dict = chat.get("cast")
    if ask["ask"] and chat_id not in ask["chats"]:
        text: str = ask["text"]
        count: int = ask["views"]
        ask["views"] += 1
        Tho.send_message(chat_id,text)
        chats = ask["chats"]
        chats.append(chat_id)
        ask["chats"] = chats
        chat.set("cast",ask)
    if msg.text == "تفعيل" and Tho.get_chat_member(chat_id,idu).status in ["administrator","creator"]:
        if chat.exists(f"chat_{chat_id}"):
            Tho.reply_to(msg,"*المجموعة مفعلة*")
        else:
            chat.set(f"chat_{chat_id}",chat_id)
            NewChat(chat_id)
            Tho.reply_to(msg,"*تم تفعيل المجموعة*")
    if not chat.exists(f"chat_{chat_id}"):
        chat.set(f"chat_{chat_id}",chat_id)
        NewChat(chat_id)
    if msg.text in ["ا","أ","أيدي","ايدي","id","Id","ID","iD","كشف"]:
        if msg.reply_to_message:
            id: int = msg.reply_to_message.from_user.id
        else:
            id: int = msg.from_user.id
        Tho.reply_to(msg,f"`{id}`")
    return


print("booo")
Tho.infinity_polling()