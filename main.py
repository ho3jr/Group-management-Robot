from pyrogram import Client, filters
from pyrogram.types import Message , InlineKeyboardMarkup, InlineKeyboardButton 
import pyromod
import sqlite3 as sq
from pyrogram.types import ChatPermissions

api_id = 18790467
api_hash = "68bf0527a74571a8dbb9cfffe70ef964"
bot_token = "7227821685:AAFGAFJRmdGaeXL5qtJIywlRrEsKQUsaVx8"

app = Client(
    "Grp_MngrBot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)


Id_Members_For_Delete_DataBase = []


# delete_user_data = InlineKeyboardMarkup(
#     [
#         [InlineKeyboardButton("حذف شود", callback_data="Stats_of_Group")],
#         [InlineKeyboardButton("حذف نشود", callback_data="set_Admin")],
#     ]
# )

db = sq.connect("data_users.db")
cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS users(
        id_db INTEGER PRIMARY KEY,
        id_tel INTEGER,
        firstname VARCHAR(30),
        lastname VARCHAR(30),
        user_name VARCHAR(30),
        language_user VARCHAR(20),
        group_id INTEGER,
        num_of_message INTEGER,
        the_state_of_silence  VARCHAR(10)
        )"""
)
db.commit()

@app.on_message(filters.group)
async def main_group(c:Client, m:Message):

    async def delete_message():
        try:
            await app.delete_messages(int(m.chat.id), int(m.id))
        except Exception as error:
            await app.send_message(m.chat.id, "The peer ID is invalid or not known yet. Make sure you meet the peer before interacting with it.")
            print(error)

    async def check_unmuted():
        cursor.execute("SELECT the_state_of_silence FROM users WHERE id_tel=? AND group_id=?", (m.from_user.id,m.chat.id,))
        result = cursor.fetchone()
        if result:
            return result

    async def get_chat_member_status():     #get chat member status in group
        try:
            status_member = await app.get_chat_member(m.chat.id,m.from_user.id)
            status_member = str(status_member.status)
            status_member = status_member.split(".")[1]
            return(status_member)
        except:
            status_member = "negative"
            return(status_member)

    def check_id_in_database():
        cursor.execute("SELECT id_tel FROM users WHERE id_tel=? AND group_id=?", (m.from_user.id,m.chat.id,))
        result = cursor.fetchone()
        if result:
            return True
        
    async def add_user_to_database(): 

        if check_id_in_database():
             return True
        else:
            db.execute(
                """
                INSERT INTO users(id_tel , firstname, lastname, user_name, language_user, group_id, num_of_message, the_state_of_silence) VALUES(?,?,?,?,?,?,?,?)""",
                (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, m.from_user.language_code, m.chat.id, 1, "unmuted")
            )
            db.commit()
            return False
        
    async def add_one_message_to_database(): 
        if await add_user_to_database():
            num_of_message = cursor.execute(
                """SELECT num_of_message FROM users"""
            )
            for i in num_of_message:
                num_of_message = i[0]   #recive num_of_message and save in num_of_message
                num_of_message = int(num_of_message)

            cursor.execute(
                "UPDATE users SET num_of_message=? WHERE id_tel =? AND group_id=?",(num_of_message+1, m.from_user.id, m.chat.id)
            )
            db.commit()
        else:
            pass

    await add_one_message_to_database() 
    state_of_silence = await check_unmuted()
    if state_of_silence[0] == "muted":
        await app.delete_messages(m.chat.id, m.id)

    if m.text == "info":
        info_user = cursor.execute(
            """SELECT num_of_message FROM users WHERE id_tel=? AND group_id=? """,(m.from_user.id, m.chat.id)
        )
        num_of_message = 0
        for i in info_user:
            num_of_message = i[0]

        infoTEXT = "نام: {}\nنام خانوادگی: {}\nایدی عددی: `{}`\nیوزرنیم: @{} \nزبان استفاده شده: `{}`\nتعداد پیام: {}".format(m.from_user.first_name, m.from_user.last_name, m.from_user.id, m.from_user.username, m.from_user.language_code, num_of_message)
        await app.send_message(m.chat.id, infoTEXT,reply_to_message_id=m.id)

    elif m.text == "بن" or m.text == "سیک" or m.text == "ban":
        member_status = await get_chat_member_status()
        if member_status =="OWNER" or member_status =="ADMINISTRATOR":
            try:
                await app.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)

                Id_Members_For_Delete_DataBase.append(m.reply_to_message.from_user.id)
                Id_Members_For_Delete_DataBase.append(m.chat.id)

                delete_user_data = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("حذف شود", callback_data="delete"+str(m.reply_to_message.from_user.id)+str(m.chat.id))],
                        [InlineKeyboardButton("حذف نشود", callback_data="dont_delete")],
                    ]
                )
                await app.send_message(m.chat.id, "**کاربر با آیدی `{}` از گروه اخراج شد!**\n\nاطلاعات کاربر از دیتابیس  و تاریخچه گروه حذف شود؟".format(m.reply_to_message.from_user.id),reply_markup=delete_user_data)
            
            except:
                await app.send_message(m.chat.id, "**کاربر اخراج نشد!**\nاین اخطار ممکن است به دلیل ادمین بودن کاربر  باشد.")

    
    if m.text == "سکوت" or m.text == "mute" or m.text == "حذف سکوت" or m.text == "unmute":
        member_status = await get_chat_member_status()
        if member_status =="OWNER" or member_status =="ADMINISTRATOR":
            if m.text ==  "سکوت" or m.text == "mute":
                cursor.execute(
                    "UPDATE users SET the_state_of_silence=? WHERE id_tel =? AND group_id=?",("muted",m.reply_to_message.from_user.id, m.chat.id)
                )
                db.commit()

                await app.send_message(m.chat.id, "**کاربر با ایدی `{}` سکوت شد!**".format(m.reply_to_message.from_user.id))

            elif m.text ==  "حذف سکوت" or m.text == "unmute": 
                cursor.execute(
                    "UPDATE users SET the_state_of_silence=? WHERE id_tel =? AND group_id=?",("unmuted",m.reply_to_message.from_user.id, m.chat.id)
                )
                db.commit()
                await app.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id,ChatPermissions(
                    can_send_messages= True,
                    can_send_media_messages=True,
                    can_send_other_messages = True,
                    can_send_polls = True,
                    can_add_web_page_previews= True,
                    can_change_info = True,
                    can_invite_users= True,
                    can_pin_messages= True))
                await app.send_message(m.chat.id, "**کاربر با ایدی `{}` حذف سکوت شد!**".format(m.reply_to_message.from_user.id))

    elif m.text == "سوپر سکوت" or m.text == "supermute" or m.text == "super mute":
        member_status = await get_chat_member_status()
        if member_status =="OWNER" or member_status =="ADMINISTRATOR":
            try:
                await app.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id,ChatPermissions())
                await app.send_message(m.chat.id, "**کاربر با ایدی `{}` سوپر سکوت شد!**".format(m.reply_to_message.from_user.id))
            except:
                 await app.send_message(m.chat.id, "**کاربر  سوپر سکوت نشد. دسترسی های ربات و کاربر مورد نظر را چک کنید.**")
                 
@app.on_callback_query()
async def query1(Client, call1):

    
    data = call1.data

    async def get_chat_member_status():     #get chat member status in group
        try:
            print("\n")
            print("status member:", status_member)
            print("\n")
            status_member = await app.get_chat_member(call1.message.chat.id,call1.from_user.id)
            status_member = str(status_member.status)
            status_member = status_member.split(".")[1]
            return(status_member)
        except:
            status_member = "negative"
            return(status_member)


    if data == "delete"+str(Id_Members_For_Delete_DataBase[0])+str(Id_Members_For_Delete_DataBase[1]):

        stutus_member = await get_chat_member_status()
        if stutus_member =="OWNER" or stutus_member =="ADMINISTRATOR":
            db.execute("""DELETE FROM users WHERE id_tel = ? AND group_id = ?""",(Id_Members_For_Delete_DataBase[0], Id_Members_For_Delete_DataBase[1]))
            db.commit()
            await app.send_message(call1.message.chat.id , "اطلاعات حذف شد")
        else:
            await app.answer_callback_query(call1.id, "شما ادمین گروه نیستید!")


    elif data == "dont_delete":
        try:
            await app.edit_message_text(int(call1.message.chat.id), int(call1.message.id), "اطلاعات در دیتابیس نگه داشته شد.")
        except Exception as error:
            await app.send_message(call1.message.chat.id, "The peer ID is invalid or not known yet. Make sure you meet the peer before interacting with it.")
            print(error)

app.run()
