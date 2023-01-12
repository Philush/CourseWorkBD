import PySimpleGUI as sg
import PySimpleGUI as psg
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def booksList(check): #запрос списка книг
    if check == 0:
        cursor.execute("SELECT * FROM library;")
    elif check == 1:
        cursor.execute('SELECT * FROM library_reader;')
    else:
        cursor.execute("SELECT * FROM library_all;")
    return cursor.fetchall()

def adminList(event): #списки для админа
    if event == '-BOOKS-':
        cursor.execute("SELECT * FROM book;")
    elif event == '-AUTHORS-':
        cursor.execute("SELECT * FROM author;")
    elif event == '-PUBLISHERS-':
        cursor.execute("SELECT * FROM publisher;")
    elif event == '-RENTAL-':
        cursor.execute("SELECT * FROM rental;")
    elif event == '-USERS-':
        cursor.execute("SELECT * FROM reader;")
    return cursor.fetchall()

def delete(event, item): #удаление записей
    print("\n\n", item, " ", event)
    if event == '-DEL-B-':
        print(" fur")
        cursor.execute(f"CALL delBook('{item[0]}');")
    elif event == '-DEL-A-':
        cursor.execute(f"CALL delAuthor({item[0]});")
    elif event == '-DEL-P-':
        cursor.execute(f"CALL delPublisher({item[0]});")
    elif event == '-DEL-U-':
        print(item[11], " ", item[0])
        cursor.execute(f"REVOKE ALL ON book, author, publisher, reader, rental, library, library_reader FROM {item[11]};\
                        \n DROP USER {item[11]};\n\
                        CALL delReader({item[0]});")
    connection.commit()

def filter(): #фильтр
    cursor.execute("SELECT DISTINCT lastname FROM author;")
    author = cursor.fetchall()
    cursor.execute("SELECT DISTINCT theme FROM book;")
    theme = cursor.fetchall()
    cursor.execute("SELECT DISTINCT genre FROM book;")
    genre = cursor.fetchall()
    cursor.execute("SELECT DISTINCT name FROM publisher;")
    publishers = cursor.fetchall()
    layout_filter = [[sg.Text('Автор', size = (15, 1)) , sg.Combo(author, size=(20,2), enable_events=False, key='-AU-')],
                    [sg.Text('Тематика', size = (15, 1)) , sg.Combo(theme, size=(20,2), enable_events=False, key='-TH-')],
                    [sg.Text('Жанр', size = (15, 1)) , sg.Combo(genre, size=(20,2), enable_events=False, key='-GE-')],
                    [sg.Text('Издательство', size = (15, 1)) , sg.Combo(publishers, size=(20,2), enable_events=False, key='-PB-')],
                    [sg.Text('Год от', size = (15, 1)) , sg.Input(size=(20,2), key='-YO-')],
                    [sg.Text('Год до', size = (15, 1)) , sg.Input(size=(20,2), key='-YD-')],
                    [sg.Button('Принять', key = '-OK-'), sg.Cancel()]]
    window = sg.Window("Filter", layout_filter, finalize = True, modal=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            window.close()
            break
        elif event == '-OK-':
            print('евент')
            za = f"SELECT book.name, author.lastname || ' ' || author.firstname, book.theme, book.genre, book.count_pages,"
            za1 = f" publisher.name as pn, book.publish_year, book.annotation, book.b_shifr, book.availability FROM book "
            za2 = f"LEFT JOIN author ON author.id = book.author_id LEFT JOIN publisher ON publisher.id = book.publisher_id WHERE book.availability = True "
            au, th, ge, pu, yo, yd = values['-AU-'], values['-TH-'], values['-GE-'], values['-PB-'], values['-YO-'], values['-YD-']
            auz = f""
            thz = f""
            gez = f"" 
            puz = f"" 
            yoz = f"" 
            ydz = f""
            if au != f"":
                auz += f"AND author.lastname = '{au[0]}' " 
            if th != f"":
                thz += f"AND book.theme = '{th[0]}' "
            if ge != f"":
                gez += f"AND book.genre = '{ge[0]}' "
            if pu != f"":
                puz += f"AND publisher.name = '{pu[0]}' "
            if yo != f"":
                yoz += f"AND book.publish_year > {yo[:]} "
            if yd != f"":
                ydz += f"AND book.publish_year < {yd[:]} "
            print(za+za1+za2+auz+thz+gez+puz+yoz+ydz+";")
            cursor.execute(za+za1+za2+auz+thz+gez+puz+yoz+ydz+";")
            
            window.close()
    return cursor.fetchall()


def modal_add_author(): #модальное окно для добавления автора
    layout_add_author =[[sg.Text('Добавление автора', font=(20), justification='center')],
            [sg.Text('Фамилия', size = (15, 1)), sg.Input(key = '-LN-', size=(30, 1))], 
            [sg.Text('Имя', size = (15, 1)), sg.Input(key = '-FN-', size=(30, 1))],
            [sg.Text('Дата рождения', size = (15, 1)), sg.Input(key = '-DB-', size=(30, 1))],
            [sg.Text('Проверьте корректность данных', key = '-ERR-', text_color='red', visible=False, justification='center')],
            [sg.Button('Принять', key = '-OK-')],
            [sg.Cancel()]]
    window = sg.Window("Добавление автора", layout_add_author, finalize=True, modal=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            window.close()
            break
        elif event == '-OK-':
            try:
                ln, fn, db = values['-LN-'], values['-FN-'], values['-DB-']
                cursor.execute(f"CALL addAuthor('{ln}', '{fn}', '{db}');")
                print(f"CALL addAuthor('{ln}', '{fn}', '{db}');")
                connection.commit()
                window.close()
            except(Exception):
                window['-ERR-'].update(visible = True)
                connection.rollback()

def modal_add_publisher():#модальное окно для добавления издательства
    layout_add_publisher =[[sg.Text('Добавление издательства', font=(20), justification='center')],
            [sg.Text('Имя', size = (15, 1)), sg.Input(key = '-NM-', size=(30, 1))],
            [sg.Text('Улица', size = (15, 1)), sg.Input(key = '-ST-', size=(30, 1))],
            [sg.Text('Номер дома', size = (15, 1)), sg.Input(key = '-HN-', size=(30, 1))],
            [sg.Text('Строение', size = (15, 1)), sg.Input(key = '-BU-', size=(30, 1))],
            [sg.Text('Почтовый индекс', size = (15, 1)), sg.Input(key = '-PC-', size=(30, 1))],
            [sg.Text('Номер телефона', size = (15, 1)), sg.Input(key = '-PN-', size=(30, 1))],
            [sg.Text('Email', size = (15, 1)), sg.Input(key = '-EM-', size=(30, 1))],
            [sg.Text('Проверьте корректность данных', key = '-ERR-', text_color='red', visible=False, justification='center')],
            [sg.Button('Принять', key = '-OK-')],
            [sg.Cancel()]]
    window = sg.Window("Добавление издательства", layout_add_publisher, finalize=True, modal=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            window.close()
            break
        elif event == '-OK-':
            try:
                nm, st, hn, bu, pc, pn, em = values['-NM-'], values['-ST-'], values['-HN-'], values['-BU-'], values['-PC-'], values['-PN-'], values['-EM-']

                cursor.execute(f"CALL addPublisher('{nm}', '{st}', '{hn}', '{bu}', '{pc}', '{pn}', '{em}');")
                print(f"CALL addPublisher('{nm}', '{st}', '{hn}', '{bu}', '{pc}', '{pn}', '{em}');")
                connection.commit()
                window.close()
            except(Exception):
                window['-ERR-'].update(visible = True)
                connection.rollback()

def modal_add_reader():#модальное окно для добавления читателя
    layout_add_reader =[[sg.Text('Добавление читателя', font=(20), justification='center')],
            [sg.Text('Логин', size = (15, 1)), sg.Input(key = '-LG-', size=(30, 1))], 
            [sg.Text('Пароль', size = (15, 1)), sg.Input(key = '-PS-', size=(30, 1))],
            [sg.Text('Фамилия', size = (15, 1)), sg.Input(key = '-LN-', size=(30, 1))],
            [sg.Text('Имя', size = (15, 1)), sg.Input(key = '-FN-', size=(30, 1))],
            [sg.Text('Дата рождения', size = (15, 1)), sg.Input(key = '-DB-', size=(30, 1))],
            [sg.Text('Улица', size = (15, 1)), sg.Input(key = '-ST-', size=(30, 1))],
            [sg.Text('Номер дома', size = (15, 1)), sg.Input(key = '-HN-', size=(30, 1))],
            [sg.Text('Строение', size = (15, 1)), sg.Input(key = '-BU-', size=(30, 1))],
            [sg.Text('Квартира', size = (15, 1)), sg.Input(key = '-FL-', size=(30, 1))],
            [sg.Text('Почтовый индекс', size = (15, 1)), sg.Input(key = '-PC-', size=(30, 1))],
            [sg.Text('Номер телефона', size = (15, 1)), sg.Input(key = '-PN-', size=(30, 1))],
            [sg.Text('Email', size = (15, 1)), sg.Input(key = '-EM-', size=(30, 1))],
            [sg.Text('Проверьте корректность данных', key = '-ERR-', text_color='red', visible=False, justification='center')],
            [sg.Button('Принять', key = '-OK-')],
            [sg.Cancel()]]
    window = sg.Window("Добавление книги", layout_add_reader, finalize=True, modal=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            window.close()
            break
        elif event == '-OK-':
            print("\n",values['-LG-'], "\n", values['-PS-'], "\n")
            try:
                lstn, frtn, dateb, st, hn, \
                bu, fl, pc, pn, em, lg, ps = values['-LN-'], values['-FN-'],\
                                                                            values['-DB-'], values['-ST-'], values['-HN-'],\
                                                                            values['-BU-'], values['-FL-'], values['-PC-'],\
                                                                            values['-PN-'], values['-EM-'], values['-LG-'], values['-PS-']
                cursor.execute(f"CREATE USER {lg} WITH PASSWORD '{ps}';\n\
                                    GRANT SELECT ON book, author, publisher, rental, reader, library, library_reader TO {lg};\n\
                                    GRANT UPDATE ON book, rental TO {lg};\
                                    GRANT INSERT ON rental TO {lg};")
                cursor.execute(f"CALL addReader('{lstn}', '{frtn}', '{dateb}', '{st}', '{hn}', '{bu}', {fl}, '{pc}', '{pn}', '{em}', '{lg}');")
                print(f"CALL addReader({id}, '{lstn}', '{frtn}', '{dateb}', '{st}', '{hn}', '{bu}', {fl}, '{pc}', '{pn}', '{em}', '{lg}');")
                connection.commit()
                window.close()
            except(Exception):
                window['-ERR-'].update(visible = True)
                connection.rollback()

def modal_add_book():#модальное окно для добавления книги
    layout_add_book =[[sg.Text('Добавление книги', font=(20), justification='center')],
            [sg.Text('Б. шифр', size = (15, 1)), sg.Input(key = '-SHIFR-', size=(30, 1))], 
            [sg.Text('Название', size = (15, 1)), sg.Input(key = '-NAME-', size=(30, 1))],
            [sg.Text('ID автора', size = (15, 1)), sg.Input(key = '-IDA-', size=(30, 1))],
            [sg.Text('Тематика', size = (15, 1)), sg.Input(key = '-THEME-', size=(30, 1))],
            [sg.Text('Жанр', size = (15, 1)), sg.Input(key = '-GENRE-', size=(30, 1))],
            [sg.Text('Кличество страниц', size = (15, 1)), sg.Input(key = '-PAGES-', size=(30, 1))],
            [sg.Text('ID издательства', size = (15, 1)), sg.Input(key = '-IDP-', size=(30, 1))],
            [sg.Text('Год издания', size = (15, 1)), sg.Input(key = '-PY-', size=(30, 1))],
            [sg.Text('Аннотация', size = (15, 1)), sg.Input(key = '-ANNOT-', size=(30, 1))],
            [sg.Text('Проверьте корректность данных', key = '-ERR-', text_color='red', visible=False, justification='center')],
            [sg.Button('Принять', key = '-OK-')],
            [sg.Cancel()]]
    window = sg.Window("Добавление книги", layout_add_book, finalize=True, modal=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            window.close()
            break
        elif event == '-OK-':
            try:
                sh, nm, ai, th, ge, cp, pi, py, an = values['-SHIFR-'], values['-NAME-'], values['-IDA-'],\
                                                    values['-THEME-'], values['-GENRE-'], values['-PAGES-'],\
                                                    values['-IDP-'], values['-PY-'], values['-ANNOT-']
                cursor.execute(f"CALL addBook('{sh}', '{nm}', {ai}, '{th}', '{ge}', {cp}, {pi}, '{py}', '{an}');")
                print(f"CALL addBook('{sh}', '{nm}', {ai}, '{th}', '{ge}', {cp}, {pi}, '{py}', '{an}');")
                connection.commit()
                window.close()
            except(Exception):
                window['-ERR-'].update(visible = True)
                connection.rollback()

def take(shifr):#взять книгу
    print(shifr)
    zapros = f"UPDATE book SET availability = false WHERE b_shifr = '{shifr}';"
    print("\n", zapros) 
    cursor.execute(zapros)
    connection.commit()

def returnBook(shifr):#возврат книги
    print(shifr)
    zapros = f"UPDATE book SET availability = true WHERE b_shifr = '{shifr}';"
    print("\n", zapros) 
    cursor.execute(zapros)
    connection.commit()        

def login():#вход в аккаунт
    layout_login = [[sg.Text('Вход', justification='center', size = (26, 1))],
            [sg.Text('Логин', size = (6, 1)), sg.Input(key='-LOGIN-', size = (20, 1))],
            [sg.Text('Пароль', size = (6, 1)), sg.Input(key='-PASSWORD-', size = (20, 1), password_char='*')],
            [sg.Text('Логин или пароль неверные', size = (26, 1), justification='center', text_color='red', key = '-ERROR-', visible = False)],
            [psg.Button('ОК', key='-IN-', size=(26, 1))]]
    window = sg.Window("Авторизация", layout_login, finalize=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            break
        if event == '-IN-':
            try:
                lg = values['-LOGIN-']
                ps = values['-PASSWORD-']
                connection = psycopg2.connect(user = lg,
                                    password = ps,
                                    host="172.20.8.18",
                                    # host="127.0.0.1",
                                    port="5432",
                                    # database = "testing"
                                    database="kp_0091_14"
                                    )
               
                window.close()

                
            except(Exception):
                window['-ERROR-'].update(visible = True)

    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            break
    return connection, lg

def logOut(window):#выход из аккаунта
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
        window.close()

def userBookList(data):#окно читателя
    lout = 0
    headingsData = ['name', 'author', 'theme', 'genre', 'pages_num', 'publisher', 'publish_year', 'annotation']
    headings = ['Название', 'Автор', 'Тематика', 'Жанр', 'Количество страниц', 'Издательство', 'год издания', 'Аннотация']
    layout_reader_library = [[psg.Button('Библиотека', key = '-LIBRARY-', size = (10, 1), visible=True), psg.Button('Мои книги', key = '-MYBOOKS-', size = (10, 1), visible = True)],
                    [sg.Table(data, 
                    headings=headings, 
                    justification='mid', key='-TABLE-',
                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    enable_click_events=True,)],
                    [sg.Button('Фильтр', key='-FILTER-')],
                    [sg.Text('Выберите книгу в таблице, которую хотите взять', key = '-TAKET-', visible = True), psg.Button('Взять книгу', key='-TAKE-', visible = True), 
                    sg.Text('Выберите книгу в таблице, которую хотите вернуть',key = '-RETURNT-', visible=False), psg.Button('Вернуть книгу', key='-RETURN-', visible = False)],
                    [sg.Cancel(), psg.Button('Сменить аккаунт', key = '-CHANGEACC-')]]
    window = sg.Window("Список книг", layout_reader_library, finalize=True, size  = (1280, 720))
    
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            break
        elif event == '-FILTER-':
            data = filter()
            values['-TABLE-'] = data
            window['-TABLE-'].update(values['-TABLE-'])
        elif event == '-TAKE-':
            try:                            
                take(data[values['-TABLE-'][0]][8])
                data = booksList(0)
                values['-TABLE-'] = data
                window['-TABLE-'].update(values['-TABLE-'])
            except IndexError:
                print()
        elif event == '-RETURN-':
            try:            
                returnBook(data[values['-TABLE-'][0]][8])
                data = booksList(1)
                values['-TABLE-'] = data
                window['-TABLE-'].update(values['-TABLE-'])
            except IndexError:
                print()
        elif event == '-LIBRARY-':
            window['-TAKET-'].update(visible = True)
            window['-TAKE-'].update(visible = True)
            window['-RETURN-'].update(visible = False)
            window['-RETURNT-'].update(visible = False)
            data = booksList(0)
            values['-TABLE-'] = data
            window['-TABLE-'].update(values['-TABLE-'])

        elif event == '-MYBOOKS-':
            window['-TAKE-'].update(visible = False)
            window['-TAKET-'].update(visible = False)
            window['-RETURNT-'].update(visible = True)
            window['-RETURN-'].update(visible = True)
            data = booksList(1)
            values['-TABLE-'] = data
            window['-TABLE-'].update(values['-TABLE-'])
            
        elif event == '-CHANGEACC-':
            lout = 1
            logOut(window)
    return lout


def adminPanel(data):#окно админа
    lout = 0
    headingsBooks = ['Шифр', 'Название', 'Автор ID', 'Тематика', 'Жанр', 'Количество страниц', 'Издательство ID', 'Год издания', 'Аннотация', 'Наличие']
    headingsAuthors = ['ID', 'Фамилия', 'Имя', 'Дата рождения']
    headingsPublishers = ['ID','Название','Улица','Дом','Строение','Почтовый индекс','Номер телефона','Email']
    headingsRental = ['ID','Б. шифр','Дата выдачи','Дата возврата','ID читателя']
    headingsUsers = ['ID','Фамилия','Имя','Дата рождения','Улица','Дом','Строение','Квартира','Почтовый индекс','Номер телефона','Email','Логин']
    layout_admin = [[psg.Button('Книги', key = '-BOOKS-', size = (10, 1), visible=True),
                            psg.Button('Авторы', key = '-AUTHORS-', size = (10, 1), visible = True),
                            psg.Button('Издательства', key = '-PUBLISHERS-', size = (10, 1), visible = True),
                            psg.Button('Прокат', key = '-RENTAL-', size = (10, 1), visible = True),
                            psg.Button('Пользователи', key = '-USERS-', size = (10, 1), visible = True),],
                            [sg.Table(data, 
                            headings=headingsBooks, 
                            justification='mid', key='-TABLE-BOOKS-',
                            selected_row_colors='red on yellow',
                            enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            enable_click_events=True,
                            visible=True),
                            sg.Table(data, 
                            headings=headingsAuthors, 
                            justification='mid', key='-TABLE-AUTHORS-',
                            selected_row_colors='red on yellow',
                            enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            enable_click_events=True,
                            visible=False),
                            sg.Table(data, 
                            headings=headingsPublishers, 
                            justification='mid', key='-TABLE-PUBLISHERS-',
                            selected_row_colors='red on yellow',
                            enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            enable_click_events=True,
                            visible=False),
                            sg.Table(data, 
                            headings=headingsRental, 
                            justification='mid', key='-TABLE-RENTAL-',
                            selected_row_colors='red on yellow',
                            enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            enable_click_events=True,
                            visible=False),
                            sg.Table(data, 
                            headings=headingsUsers, 
                            justification='mid', key='-TABLE-USERS-',
                            selected_row_colors='red on yellow',
                            enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            enable_click_events=True,
                            visible=False)],
                            [psg.Button('Добавить книгу', key='-ADD-B-', visible = True), 
                            psg.Button('Удалить книгу', key='-DEL-B-', visible = True),
                            psg.Button('Добавить автора', key='-ADD-A-', visible = False), 
                            psg.Button('Удалить автора', key='-DEL-A-', visible = False),
                            psg.Button('Добавить издательство', key='-ADD-P-', visible = False), 
                            psg.Button('Удалить издательство', key='-DEL-P-', visible = False),
                            psg.Button('Добавить пользователя', key='-ADD-U-', visible = False), 
                            psg.Button('Удалить пользователя', key='-DEL-U-', visible = False)],
                            [sg.Cancel(), psg.Button('Сменить аккаунт', key = '-CHANGEACC-')]]
    window = sg.Window("Admin panelг", layout_admin, finalize=True, size = (1280, 720))
    event_last = '-BOOKS-'
    while True:
        event, values = window.read()
        print(event, values)
        
        if event in (None, 'Exit', 'Cancel'):
            break
        elif event == '-BOOKS-':
            data = adminList(event)
            values['-TABLE-BOOKS-'] = data
            window['-TABLE-BOOKS-'].update(values['-TABLE-BOOKS-'])
            window['-TABLE-BOOKS-'].update(visible = True)
            window['-TABLE-AUTHORS-'].update(visible = False)
            window['-TABLE-PUBLISHERS-'].update(visible = False)
            window['-TABLE-RENTAL-'].update(visible = False)
            window['-TABLE-USERS-'].update(visible = False)
            window['-ADD-B-'].update(visible = True)
            window['-DEL-B-'].update(visible = True)
            window['-ADD-A-'].update(visible = False)
            window['-DEL-A-'].update(visible = False)
            window['-ADD-P-'].update(visible = False)
            window['-DEL-P-'].update(visible = False)
            window['-ADD-U-'].update(visible = False)
            window['-DEL-U-'].update(visible = False)
            event_last = event

        elif event == '-AUTHORS-':
            data = adminList(event)
            values['-TABLE-AUTHORS-'] = data
            window['-TABLE-AUTHORS-'].update(values['-TABLE-AUTHORS-'])
            window['-TABLE-BOOKS-'].update(visible = False)
            window['-TABLE-AUTHORS-'].update(visible = True)
            window['-TABLE-PUBLISHERS-'].update(visible = False)
            window['-TABLE-RENTAL-'].update(visible = False)
            window['-TABLE-USERS-'].update(visible = False)
            window['-ADD-B-'].update(visible = False)
            window['-DEL-B-'].update(visible = False)
            window['-ADD-A-'].update(visible = True)
            window['-DEL-A-'].update(visible = True)
            window['-ADD-P-'].update(visible = False)
            window['-DEL-P-'].update(visible = False)
            window['-ADD-U-'].update(visible = False)
            window['-DEL-U-'].update(visible = False)
            event_last = event
        elif event == '-PUBLISHERS-':
            data = adminList(event)
            values['-TABLE-PUBLISHERS-'] = data
            window['-TABLE-PUBLISHERS-'].update(values['-TABLE-PUBLISHERS-'])
            window['-TABLE-BOOKS-'].update(visible = False)
            window['-TABLE-AUTHORS-'].update(visible = False)
            window['-TABLE-PUBLISHERS-'].update(visible = True)
            window['-TABLE-RENTAL-'].update(visible = False)
            window['-TABLE-USERS-'].update(visible = False)
            window['-ADD-B-'].update(visible = False)
            window['-DEL-B-'].update(visible = False)
            window['-ADD-A-'].update(visible = False)
            window['-DEL-A-'].update(visible = False)
            window['-ADD-P-'].update(visible = True)
            window['-DEL-P-'].update(visible = True)
            window['-ADD-U-'].update(visible = False)
            window['-DEL-U-'].update(visible = False)
            event_last = event
        elif event == '-RENTAL-':
            data = adminList(event)
            values['-TABLE-RENTAL-'] = data
            window['-TABLE-RENTAL-'].update(values['-TABLE-RENTAL-'])
            window['-TABLE-BOOKS-'].update(visible = False)
            window['-TABLE-AUTHORS-'].update(visible = False)
            window['-TABLE-PUBLISHERS-'].update(visible = False)
            window['-TABLE-RENTAL-'].update(visible = True)
            window['-TABLE-USERS-'].update(visible = False)
            window['-ADD-B-'].update(visible = False)
            window['-DEL-B-'].update(visible = False)
            window['-ADD-A-'].update(visible = False)
            window['-DEL-A-'].update(visible = False)
            window['-ADD-P-'].update(visible = False)
            window['-DEL-P-'].update(visible = False)
            window['-ADD-U-'].update(visible = False)
            window['-DEL-U-'].update(visible = False)
            event_last = event
        elif event == '-USERS-':
            data = adminList(event)
            values['-TABLE-USERS-'] = data
            window['-TABLE-USERS-'].update(values['-TABLE-USERS-'])
            window['-TABLE-BOOKS-'].update(visible = False)
            window['-TABLE-AUTHORS-'].update(visible = False)
            window['-TABLE-PUBLISHERS-'].update(visible = False)
            window['-TABLE-RENTAL-'].update(visible = False)
            window['-TABLE-USERS-'].update(visible = True)
            window['-ADD-B-'].update(visible = False)
            window['-DEL-B-'].update(visible = False)
            window['-ADD-A-'].update(visible = False)
            window['-DEL-A-'].update(visible = False)
            window['-ADD-P-'].update(visible = False)
            window['-DEL-P-'].update(visible = False)
            window['-ADD-U-'].update(visible = True)
            window['-DEL-U-'].update(visible = True)
            event_last = event
        elif event == '-ADD-B-':
            modal_add_book()
            data = adminList(event_last)
            values['-TABLE-BOOKS-'] = data
            window['-TABLE-BOOKS-'].update(values['-TABLE-BOOKS-'])

        elif event == '-DEL-B-':
            try:
                delete(event, data[values['-TABLE-BOOKS-'][0]][0])
                data = adminList(event_last)
                values['-TABLE-BOOKS-'] = data
                window['-TABLE-BOOKS-'].update(values['-TABLE-BOOKS-'])
            except (Exception):
                data = adminList(event_last)
                values['-TABLE-BOOKS-'] = data
                window['-TABLE-BOOKS-'].update(values['-TABLE-BOOKS-'])
        
        elif event == '-ADD-U-':
            modal_add_reader()
            data = adminList(event_last)
            values['-TABLE-USERS-'] = data
            window['-TABLE-USERS-'].update(values['-TABLE-USERS-'])
        elif event == '-DEL-U-':
            try:
                delete(event, data[values['-TABLE-USERS-'][0]])
                data = adminList(event_last)
                values['-TABLE-USERS-'] = data
                window['-TABLE-USERS-'].update(values['-TABLE-USERS-'])
            except(Exception):
                data = adminList(event_last)
                values['-TABLE-USERS-'] = data
                window['-TABLE-USERS-'].update(values['-TABLE-USERS-'])

        elif event == '-ADD-A-':
            modal_add_author()
            data = adminList(event_last)
            values['-TABLE-AUTHORS-'] = data
            window['-TABLE-AUTHORS-'].update(values['-TABLE-AUTHORS-'])
        elif event == '-DEL-A-':
            try:
                delete(event, data[values['-TABLE-AUTHORS-'][0]])
                data = adminList(event_last)
                values['-TABLE-AUTHORS-'] = data
                window['-TABLE-AUTHORS-'].update(values['-TABLE-AUTHORS-'])
            except(Exception):
                data = adminList(event_last)
                values['-TABLE-AUTHORS-'] = data
                window['-TABLE-AUTHORS-'].update(values['-TABLE-AUTHORS-'])
        
        elif event == '-ADD-P-':
            modal_add_publisher()
            data = adminList(event_last)
            values['-TABLE-PUBLISHERS-'] = data
            window['-TABLE-PUBLISHERS-'].update(values['-TABLE-PUBLISHERS-'])
        elif event == '-DEL-P-':
            try:
                delete(event, data[values['-TABLE-PUBLISHERS-'][0]])
                data = adminList(event_last)
                values['-TABLE-PUBLISHERS-'] = data
                window['-TABLE-PUBLISHERS-'].update(values['-TABLE-PUBLISHERS-'])
            except(Exception):
                data = adminList(event_last)
                values['-TABLE-PUBLISHERS-'] = data
                window['-TABLE-PUBLISHERS-'].update(values['-TABLE-PUBLISHERS-'])


        elif event == '-CHANGEACC-':
            lout = 1
            logOut(window)

    return lout
        

try:
    sg.theme('SandyBeach')  
    while True:
        connection, lg = login()
        cursor = connection.cursor()
        if lg == 'bestt':
            data = adminList('-BOOKS-')
            lout = adminPanel(data)            
        else:
            data = booksList(0)
            lout = userBookList(data)
        if lout == 0:
            break
    
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
