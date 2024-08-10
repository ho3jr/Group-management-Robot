from pyrogram import Client, filters
from pyrogram.types import Message , InlineKeyboardMarkup, InlineKeyboardButton 
import pyromod
import sqlite3 as sq

api_id = 18790467
api_hash = "68bf0527a74571a8dbb9cfffe70ef964"
bot_token = "7227821685:AAFGAFJRmdGaeXL5qtJIywlRrEsKQUsaVx8"

app = Client(
    "Grp_MngrBot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)


Id_Members_For_Delete_DataBase = []


delete_user_data = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("حذف شود", callback_data="Stats_of_Group")],
        [InlineKeyboardButton("حذف نشود", callback_data="set_Admin")],
    ]
)

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
        num_of_message INTEGER
        )"""
)
db.commit()

@app.on_message(filters.group)
async def hello(c:Client, m:Message):

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
                INSERT INTO users(id_tel , firstname, lastname, user_name, language_user, group_id, num_of_message) VALUES(?,?,?,?,?,?,?)""",
                (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, m.from_user.language_code, m.chat.id, 1)
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

    if m.text == "info":
        info_user = cursor.execute(
            """SELECT num_of_message FROM users WHERE id_tel=? AND group_id=? """,(m.from_user.id, m.chat.id)
        )
        num_of_message = 0
        for i in info_user:
            num_of_message = i[0]

        infoTEXT = "نام: {}\nنام خانوادگی: {}\nایدی عددی: `{}`\nیوزرنیم: @{} \nزبان استفاده شده: `{}`\nتعداد پیام: {}".format(m.from_user.first_name, m.from_user.last_name, m.from_user.id, m.from_user.username, m.from_user.language_code, num_of_message)
        await app.send_message(m.chat.id, infoTEXT,reply_to_message_id=m.id)

    if m.text == "بن" or m.text == "سیک" or m.text == "ban":
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



@app.on_callback_query()
async def query1(Client, call1):
    data = call1.data

    async def get_chat_member_status():     #get chat member status in group
        try:
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

    if data == "dont_delete":


        await app.edit_message_text(call1.id, call1.message.id, "اطلاعات در دیتابیس نگه داشته شد.")
        # await app.answer_callback_query(call1.id, "اطلاعات در دیتابیس نگه داشته شد.")




            

app.run()




# def get_peer_type(peer_id: int) -> str:
#     if peer_id < 0:
#         if MIN_CHAT_ID <= peer_id:
#             return "chat"

#         if MIN_CHANNEL_ID <= peer_id < MAX_CHANNEL_ID:
#             return "channel"
#     elif 0 < peer_id <= MAX_USER_ID:
#         return "user"

#     raise ValueError(f"Peer id invalid: {peer_id}")
