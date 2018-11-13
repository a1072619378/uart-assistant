#!/usr/bin/python
# -*- coding: UTF-8 -*-

# ============================================================
# Copyright 2018. All Rights Reserved.
# Date:
# Version: 
# ============================================================
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import font
import time
import serial
import serial.tools.list_ports
import threading
import pdb

#pdb.set_trace()
#color = colorchooser.askcolor(initialcolor='#ff00ff')
#print(color)

def set_logs_bg_color():
	"""
	"""
	color = colorchooser.askcolor(initialcolor='#ffffff')
	logs['background'] = color[1]
	print(color)

tag_rec_bg_color = '#000000'
def set_logs_rec_bg_color():
	"""
	"""
	global tag_rec_bg_color
	color = colorchooser.askcolor(initialcolor='#ffffff')
	tag_rec_bg_color = color[1]
	print(tag_rec_bg_color)

tag_rec_fg_color = '#00ff00'
def set_logs_rec_fg_color():
	"""
	"""
	global tag_rec_fg_color
	color = colorchooser.askcolor(initialcolor='#ffffff')
	tag_rec_fg_color = color[1]
	print(tag_rec_fg_color)

tag_send_bg_color = '#000000'
def set_logs_send_bg_color():
	"""
	"""
	global tag_send_bg_color
	color = colorchooser.askcolor(initialcolor='#ffffff')
	tag_send_bg_color = color[1]
	print(tag_send_bg_color)

tag_send_fg_color = '#ff0000'
def set_logs_send_fg_color():
	"""
	"""
	global tag_send_fg_color
	color = colorchooser.askcolor(initialcolor='#ffffff')
	tag_send_fg_color = color[1]
	print(tag_send_fg_color)

def crc_calculate():
	"""
	"""
	data = crc_input.get('1.0', 'end')
	crc_result['text'] = 'CRC: 047E '
	
def save_logs():
	"""
	"""
	logs_text = logs.get('1.0', 'end')
	if len(logs_text) is 1:
		messagebox.showinfo(message='日志为空！')
		return;
	filename = filedialog.asksaveasfilename()
	with open(filename, 'w+', encoding='UTF-8') as f:
		print('save the logs...')
		f.write(logs_text)
	messagebox.showinfo(message='保存成功！')

def clear_logs():
	"""
	"""
	logs.delete('1.0', 'end')
	print('clear the logs...')

recurrent_flag = False
def send_data():
	"""
	"""
	global serial_port
	global recurrent_flag

	if serial_port.is_open is False:
		messagebox.showinfo(message='串口没有打开！')
		return

	if re_send_flag.get():
		if send_strvar.get() == '  发送  ':
			open_button['state'] = DISABLED
			re_send_check['state'] = DISABLED
			send_strvar.set('  终止  ')
			send_button['bg'] = '#00ff00'
			recurrent_flag = True
			recurrent_send()
		else:
			open_button['state'] = NORMAL
			re_send_check['state'] = NORMAL
			send_strvar.set('  发送  ')
			send_button['bg'] = '#ffffff'
			recurrent_flag = False
	else:
		send_once()

def send_once():
	"""
	"""
	global tag_send_bg_color
	global tag_send_fg_color

	data_str = send_input.get('1.0', 'end')
	if len(data_str) is 1:
		messagebox.showinfo(message='发送区为空！')
		return
	data_bytes = bytes(data_str, encoding='utf-8')
	serial_port.write(data_bytes)
	
	print_s = ('> %s: %s') % (get_time_stamp(), data_str)
	logs.tag_config('sb', background=tag_send_bg_color, foreground=tag_send_fg_color)
	logs.insert('end -1 chars', print_s, 'sb')
	
	if auto_flag.get():
		logs.yview_moveto(1)
		
def action():
	global recurrent_flag

	while recurrent_flag:
		send_once()
		time_span = send_period_input.get('1.0', 'end')
		time.sleep(int(time_span)/1000)

def recurrent_send():
	"""
	"""
	t =threading.Thread(target=action)
	t.start()

def auto_scroll():
	"""
	"""
	#print(auto_flag.get())
	print(re_send_flag.get())

def list_coms():
	"""
	"""
	coms_name = []
	plist = list(serial.tools.list_ports.comports())
	for coms in range(len(plist)):
		coms_name.append(plist[coms][0])
	return coms_name

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp
	
lines = []
def serial_recieve():
	serial_data = ''
	global lines
	global tag_rec_bg_color
	global tag_rec_fg_color

	while serial_port.is_open:
		serial_data = serial_port.read(500)

		if len(serial_data) != 0:
			s = ''
			for i in serial_data:
				s += '{0:0>2}'.format(str(hex(i))[2:])
				
			print_s = ('< %s: %s\n') % (get_time_stamp(), s)
			logs.tag_config('g', background=tag_rec_bg_color, foreground=tag_rec_fg_color)
			logs.insert('end -1 chars', print_s, 'g')
	
			if auto_flag.get():
				logs.yview_moveto(1)
			
		if auto_send_strvar.get() == '  终止  ':
			lines_num = len(lines)
			for i in range(lines_num):
				if len(lines[i]) is not 0:
					split_line = lines[i].split(":")
					if split_line[0] is not '#':
						data_bytes = bytes(split_line[1], encoding='utf-8')
						if data_bytes == serial_data:
							print(split_line[1])

def open_serial():
	"""
	"""
	global serial_port
	select_com = com_combobox.get()
	if len(select_com) is 0:
		messagebox.showinfo(message='请先选择串口')
		return

	if open_strvar.get() == '打开串口':
		serial_port.baudrate = 115200
		serial_port.port = com_combobox.get()
		serial_port.timeout = 0.03
		#print(serial_port)
		serial_port.open()
		
		open_strvar.set('关闭串口')
		open_button['bg'] = '#00ff00'
	else:
		serial_port.close()

		open_strvar.set('打开串口')
		open_button['bg'] = '#ffffff'

	serial_recieve_thread =threading.Thread(target=serial_recieve)
	serial_recieve_thread.start()

auto_file_name = ''
def load_file_name():
	"""
	"""
	global auto_file_name
	auto_file_name = filedialog.askopenfilename()
	print(auto_file_name)

def start_auto_send():
	"""
	"""
	global lines
	global serial_port
	global auto_file_name

	if serial_port.is_open is False:
		messagebox.showinfo(message='串口没有打开！')
		return

	if auto_file_name is '':
		messagebox.showinfo(message='没有加载文件！')
		return

	if auto_send_strvar.get() == '  开始  ':
		load_button['state'] = DISABLED
		open_button['state'] = DISABLED
		auto_send_strvar.set('  终止  ')
		auto_start_button['bg'] = '#00ff00'
		
		fd = open(auto_file_name, 'r')
		lines = fd.read().splitlines()
	else:
		load_button['state'] = NORMAL
		open_button['state'] = NORMAL
		auto_send_strvar.set('  开始  ')
		auto_start_button['bg'] = '#ffffff'
		fd.close()

root = Tk()
# 运行平台检查，只能在windows上运行。
platform = root.tk.call('tk', 'windowingsystem')
print(platform)
if platform is "win32":
	print("This tool can only run on Windows.")
	time.sleep(3)
	quit()

root.title('TH-NET测试工具')
#root.geometry('600x300+900+500')
#root.minsize(500,250)
#root.maxsize(1000,1000)
#print(root.state())
#root.state('zoomed')
root.resizable(width = False, height = False)

frame = ttk.Frame(root, borderwidth=1, relief="flat", padding="30 30 30 30")
frame.grid(column=0, row=1)

text_font = font.Font(family='Courier', size=14)
logs_font = font.Font(family='Courier', size=12)
buttons_font = font.Font(family='Courier', size=12)#, weight='bold'
com_set_font = font.Font(family='Courier', size=10)

# 串口设置区--------------------------------------------
com_set_area = tk.LabelFrame(frame, font=com_set_font, text='串口设置')
com_set_area.grid(row=0, column=0, sticky=(W, N), padx=(0, 0), pady=(0, 0))
				
# 串口显示标签-------------------------------------------
crc_result = tk.Label(com_set_area, text='串  口', font=com_set_font)
crc_result.grid(row=0, column=0,  sticky=(W, N), padx=(10, 0), pady=(10, 0))
				
# 串口选择下拉列表---------------------------------------
com_select = StringVar()
com_combobox = ttk.Combobox(com_set_area, width=10, font=com_set_font,
							values=list_coms(), textvariable=com_select)
com_combobox.set(list_coms()[0])
com_combobox['state'] = 'readonly'
com_combobox.grid(row=0, column=1, sticky=(W, N), padx=(5, 10), pady=(10, 0))

# 串口波特率显示标签-------------------------------------
crc_result = tk.Label(com_set_area, text='波特率', font=com_set_font)
crc_result.grid(row=1, column=0, sticky=(W, N), padx=(10, 0), pady=(5, 0))
				
# 波特率下拉选择列表--------------------------------------
baudrate_select = StringVar()
baudrate_combobox = ttk.Combobox(com_set_area, width=10, font=com_set_font,
								textvariable=baudrate_select)
baudrate_combobox['values'] = ('9600', '115200')
baudrate_combobox['state'] = 'readonly'
baudrate_combobox.set('115200')
baudrate_combobox.grid(row=1, column=1, sticky=(W, N), padx=(5, 10), pady=(5, 10))

# 打开串口按钮--------------------------------------------
open_strvar = StringVar()
open_button = tk.Button(com_set_area, font=buttons_font, bg='#ffffff', fg='#000000',
						textvariable=open_strvar, command=open_serial)
open_strvar.set('打开串口')
open_button.grid(row=2, column=1, sticky=(N, E), padx=(0, 0), pady=(0, 0))

# CRC计算工具区-------------------------------------------
crc_area = tk.LabelFrame(frame, font=com_set_font, text='计算CRC')
crc_area.grid(row=1, column=0, sticky=(W, N), padx=(0, 0), pady=(0, 0))
# CRC计算输入框-------------------------------------------
crc_input = Text(crc_area, width=50, height=3, wrap='word', font=text_font)
crc_input.grid(row=0, column=0, columnspan=2, sticky=(W, N, E), padx=(0, 0), pady=(20, 0))
#crc_input.insert('1.0', "输入数据帧并点击计算...")
# CRC计算结果显示-----------------------------------------
crc_result = tk.Label(crc_area, text='CRC:      ', font=text_font, bg='#ffffff')
crc_result.grid(row=1, column=0, sticky=(W, N), padx=(0, 0), pady=(10, 0))
# 计算crc按钮---------------------------------------------
crc_button = tk.Button(crc_area, text='  计算  ', font=buttons_font, 
						bg='#ffffff',  fg='#000000', command=crc_calculate)
crc_button.grid(row=1, column=1, sticky=(E, N), padx=(0, 0), pady=(10, 0))

# 手动发送区----------------------------------------------
send_area = tk.LabelFrame(frame, font=com_set_font, text='手动发送')
send_area.grid(row=2, column=0, sticky=(W, N), padx=(0, 0), pady=(0, 0))
# 手动发送输入窗口----------------------------------------
send_input = Text(send_area, width=50, height=3, wrap='word', font=text_font)
send_input.grid(row=0, column=0, columnspan=5, sticky=(W, N, E), padx=(0, 0), pady=(20, 0))
#send_input.insert('1.0', "输入数据帧并点击发送...")

# 发送格式下拉列表---------------------------------------
encoding_select = StringVar()
encoding_combobox = ttk.Combobox(send_area, width=8, font=com_set_font, 
								values=('ASCII', 'HEX'), textvariable=encoding_select)
encoding_combobox.set('ASCII')
encoding_combobox['state'] = 'readonly'
encoding_combobox.grid(row=1, column=0, sticky=(W, N), padx=(10, 0), pady=(15, 0))

# 循环发送复选按钮----------------------------------------
re_send_flag = BooleanVar()
re_send_check = tk.Checkbutton(send_area, text='循环发送',font=buttons_font,
							command=auto_scroll, onvalue=True, offvalue=False, 
							variable=re_send_flag)
re_send_check.grid(row=1, column=1, sticky=(E, N), padx=(0, 0), pady=(16, 0))
re_send_check.deselect()

# 显示"发送间隔(ms)"字符-----------------------------------
send_period = tk.Label(send_area, text='发送间隔(ms)', font=buttons_font)
send_period.grid(row=1, column=2, sticky=(E, N), padx=(0, 0), pady=(18, 0))

# 发送时间间隔输入窗口--------------------------------------
send_period_input = Text(send_area, width=7, height=1, wrap='word', font=text_font)
send_period_input.grid(row=1, column=3, sticky=(W, N), padx=(0, 0), pady=(15, 0))
send_period_input.insert('1.0', "1000")

# 手动发送按钮---------------------------------------------
send_strvar = StringVar()
send_button = tk.Button(send_area, font=buttons_font, bg='#ffffff', fg='#000000', 
						textvariable=send_strvar, command=send_data)
send_strvar.set('  发送  ')
send_button.grid(row=1, column=4, sticky=(E, N), padx=(0, 5), pady=(10, 5))

# 自动发送区-----------------------------------------------
auto_send_area = tk.LabelFrame(frame,font=com_set_font,text='自动发送')
auto_send_area.grid(row=3,column=0,sticky=(W, N),padx=(0, 0),pady=(0, 0))
# 加载文件按钮---------------------------------------------
load_button = tk.Button(auto_send_area,text=' 加载文件 ',font=buttons_font,
						bg='#ffffff',fg='#000000',command=load_file_name)
load_button.grid(row=0,column=1,sticky=(W, N),padx=(10, 0),pady=(10, 20))
# 自动发送开始关闭按钮-------------------------------------
auto_send_strvar = StringVar()
auto_start_button = tk.Button(auto_send_area,font=buttons_font,bg='#ffffff',
								fg='#000000',textvariable=auto_send_strvar,
								command=start_auto_send)
auto_send_strvar.set('  开始  ')
auto_start_button.grid(row=0,column=2,sticky=(W, N),padx=(20, 332),pady=(10, 20))

# 日志显示区-----------------------------------------------
logs_area = tk.LabelFrame(frame,font=com_set_font,text='日志')
logs_area.grid(row=0,column=1,rowspan=4,sticky=(W, N),padx=(30, 0),pady=(0, 0))
# 日志显示窗口----------------------------------------------
logs = Text(logs_area,width=70,height=30,wrap='word',font=logs_font,
					background='#000000', foreground='#ffffff')
logs.grid(row=0,column=0,columnspan=4,sticky=(W, N),padx=(10, 0),pady=(10, 0))
# 日志窗口拖动条----------------------------------------------
logs_scrollbar = Scrollbar(logs_area,orient=VERTICAL,command=logs.yview)
logs_scrollbar.grid(row=0,column=3,sticky=(N, S, E))
logs.configure(yscrollcommand=logs_scrollbar.set) 

# 自动滚屏复选按钮----------------------------------------------
auto_flag = BooleanVar() # 用于存储复选框当前状态
auto_scroll_check = tk.Checkbutton(logs_area, text='自动滚屏',font=buttons_font,
			command=auto_scroll,onvalue=True,offvalue=False,variable=auto_flag)
auto_scroll_check.grid(row=1, column=1,sticky=(E, N),padx=(0, 0),pady=(10, 0))
auto_scroll_check.select()
# 清空日志按钮----------------------------------------------
clear_button = tk.Button(logs_area,text=' 清空日志 ',font=buttons_font,
						bg='#ffffff',fg='#000000',command=clear_logs)
clear_button.grid(row=1,column=2,sticky=(E, N),padx=(0, 0),pady=(10, 0))
# 保存日志按钮----------------------------------------------
save_button = tk.Button(logs_area,text=' 保存日志 ',font=buttons_font,
								bg='#ffffff',fg='#000000',command=save_logs)
save_button.grid(row=1, column=3, columnspan=2, sticky=(E, N),
				padx=(0, 0), pady=(10, 0))

def test():
    print("test!")

menubar = Menu(root)

# 创建文件下拉菜单
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="打开", command=test)
filemenu.add_command(label="保存", command=test)
filemenu.add_separator()
menubar.add_cascade(label="文件", menu=filemenu)

# 创建编辑下拉菜单
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="复制", command=test)
editmenu.add_command(label="粘贴", command=test)
editmenu.add_command(label="剪切", command=test)
menubar.add_cascade(label="编辑", menu=editmenu)

# 创建设置下拉菜单
setmenu = Menu(menubar, tearoff=0)
setmenu.add_command(label="日志背景颜色", command=set_logs_bg_color)
setmenu.add_command(label="接收字体颜色", command=set_logs_rec_fg_color)
setmenu.add_command(label="接收背景颜色", command=set_logs_rec_bg_color)
setmenu.add_command(label="发送字体颜色", command=set_logs_send_fg_color)
setmenu.add_command(label="发送背景颜色", command=set_logs_send_bg_color)
setmenu.add_command(label="日志字体", command=test)
menubar.add_cascade(label="设置", menu=setmenu)

# 创建帮助下拉菜单
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="关于", command=test)
menubar.add_cascade(label="帮助", menu=helpmenu)

menubar.add_cascade(label="退出", command=root.quit)

# 显示菜单
root.config(menu=menubar)


root.rowconfigure(0, weight=1, minsize=0)
root.columnconfigure(0, weight=1, minsize=0)

#frame.rowconfigure(0, weight=1, minsize=60)
#frame.rowconfigure(1, weight=1, minsize=60)
#frame.rowconfigure(2, weight=1, minsize=60)
#frame.columnconfigure(0, weight=1, minsize=60)
#frame.columnconfigure(1, weight=1, minsize=60)

ttk.Sizegrip(root).grid(column=999, row=999, sticky=(S, E))

if __name__ == '__main__':
	serial_port = serial.Serial()
	root.mainloop()