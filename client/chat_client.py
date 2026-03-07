#!/usr/bin/env python3
"""
Chat client.

Run two clients to start a chat. The number of participants can be changed
below. This is a GUI client that uses Tkinter. This demo shows that the API
works well with multithreading.
"""

import threading
import tkinter as tk

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='Chat', token='mychat', players=2)

def thread_output(text_area):
    while True:
        try:
            state = game.state()
        except GameServerError as e:
            print(e)
            window.destroy()

        messages = state['messages']
        message_list = []
        prev_name = ''

        for name, message in messages:
            if name != prev_name:
                message_list.append(('', 'text'))
                message_list.append((name, 'name'))

            message_list.append((message, 'text'))
            prev_name = name

        text_area.config(state=tk.NORMAL)
        text_area.delete(1.0, tk.END)

        if not messages:
            text_area.insert(1.0,
                '\nNo messages yet.\n\nType a message below,\nhit Enter to send it.')

        for line in message_list:
            text, attribute = line
            text_area.insert(tk.END, text + '\n', attribute)

        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)

def entry_handler(_):
    message = entry.get()
    entry.delete(0, tk.END)

    try:
        game.move(message=message)
    except IllegalMove as e:
        print(e)
    except GameServerError as e:
        window.destroy()
        raise e

print('waiting for another client to join ...')

my_id = game.join()

while True:
    try:
        game.move(name=input('Enter your name: '))
        break
    except IllegalMove as e:
        print(e)

colour_bg = '#272727'
colour_name = '#1CDC9A'
colour_text = '#3DAEE9'

window = tk.Tk()
window.title('Chat')
window.resizable(width=False, height=False)

text_area = tk.Text(
    width=40, height=25,
    foreground=colour_text, background=colour_bg,
    highlightthickness=10, highlightbackground=colour_bg, highlightcolor=colour_bg,
    border=0)

text_area.tag_configure('name', font=(None, 12, 'bold'), foreground=colour_name)
text_area.tag_configure('text', font=(None, 12), foreground=colour_text)

entry = tk.Entry(
    font=(None, 12),
    insertbackground=colour_name,
    relief='groove',
    foreground=colour_text, background=colour_bg,
    highlightthickness=10, highlightbackground=colour_bg, highlightcolor=colour_bg,
    border=1.5)

entry.bind('<Return>', func=entry_handler)
window.bind('<Escape>', func=lambda _: window.destroy())

text_area.pack(expand=True)
entry.pack(expand=True, fill=tk.X)
entry.focus_set()

threading.Thread(target=thread_output, args=(text_area, ), daemon=True).start()

window.mainloop()
