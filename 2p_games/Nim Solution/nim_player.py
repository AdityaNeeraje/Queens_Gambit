from random import randint
a =randint(5, 14)

import tkinter as tk
from PIL import Image, ImageTk
root=tk.Tk()
root.config(height=1000, width=1000, background="yellow")
picture=ImageTk.PhotoImage(Image.open('matchstick2.jpg').resize((50, 50), Image.ANTIALIAS))

def reduce_pile(index):
    global b_values, player_currently_playing, complete_xor, first_move
    if player_currently_playing == 0 or player_currently_playing==index+1:
        first_move=False
        if player_currently_playing==0:
            complete_xor=complete_xor^len(b_values[index])
        if len(b_values[index]) == 0:
            pass
        else:
            player_currently_playing=index+1
            label=b_values[index].pop()
            label.destroy()
            if len(b_values[index])!=0:
                return
    else:
        return
    if len(b_values[index]) == 0:
        buttons[index]['state']=tk.DISABLED
        ask_computer_to_play()
        return

def ask_computer_to_play():
    global complete_xor, b_values, first_move, player_currently_playing
    if first_move or player_currently_playing!=0:
        if not first_move:
            complete_xor=complete_xor^len(b_values[player_currently_playing-1])
        player_currently_playing=0
        first_move=False
        if complete_xor==0:
            for i in range(len(b_values)):
                if len(b_values[i])!=0:
                    label=b_values[i].pop()
                    label.destroy()
                    if len(b_values[i])!=0:
                        return
                    buttons[i]['state']=tk.DISABLED
                    return
        for b in b_values:
            len_b=len(b)
            if len_b^complete_xor<len_b:
                diff=len_b-(len_b^complete_xor)
                for i in range(diff):
                    label=b.pop()
                    label.destroy()
                complete_xor=0
                if len(b)==0:
                    buttons[b_values.index(b)]['state']=tk.DISABLED
                    return
                return

buttons=[]
b_values=[]
complete_xor=0
computer_to_play=False
player_currently_playing=0
first_move=True
for i in range(a):
    b = randint(1, 14)
    complete_xor=complete_xor^b
    y=50+60*i
    b_values.append([])
    for k in range(b):
        label = tk.Label(root, image = picture)
        label.place(x=450 + (k-b/2)*60, y=y)
        b_values[-1].append(label)
    new_button=tk.Button(text="REDUCE", background="red", relief=tk.RAISED, command=lambda i=i: reduce_pile(i))
    new_button.place(y=y, x=1000-140)
    buttons.append(new_button)

computer_play=tk.Button(text="Ask computer to play", background="green", relief=tk.RAISED, command=ask_computer_to_play)
computer_play.place(x=400, y=110+60*a)

root.mainloop()
