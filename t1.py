import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog as fd
from smb.SMBConnection import SMBConnection
from arp import scan_port, scan
from concurrent.futures import ThreadPoolExecutor
from PIL import ImageTk, Image
import threading
import socket
from tkinter import N,S,W,E

def main():
	filename = ""
	selected_host = []

	def openf():
		global filename
		filetypes = (
			('text files', '*.txt'),
			('All files', '*.*')
		)
		filename = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
		print(filename)
		if filename:
			ent.delete("0", tk.END)
			ent.insert("0", filename)

	def scan_hosts():
		selected_host.clear()
		tree.delete(*tree.get_children())
		results = scan("192.168.1.1/24")
		with ThreadPoolExecutor(max_workers=6) as executor:
			hosts = executor.map(scan_port, results)
		hosts = [("host1", "192.168.1.1"), ("host2", "192.168.1.2"), ("host3", "192.168.1.3")]
		for host in hosts:
			if host:
				tree.insert('', tk.END, values=host, tags="unchecked")

	def upload_file(remote_name, ip, service, path='/'):
		conn = SMBConnection('username', 'password', 'any_name', remote_name)
		assert conn.connect(ip, timeout=3)
		with open(filename, 'rb') as f:
			try:
				conn.storeFile(service, filename.split('/')[-1], f)
			except Exception as err:
				print(err)

	def batch_upload_file(service="MB"):
		for server in selected_host:
			try:
				print(f'upload {filename} to {server[0]}/{service}')
				upload_file(server[0], server[1], service)
			except ConnectionRefusedError:
				print("chaonima")

	# def item_selected(event):
	# 	for selected_item in tree.selection():
	# 		item = tree.item(selected_item)
	# 		record = item['values']
	# 		try:
	# 			if filename:
	# 				upload_file(record[0], record[1], 'MP')
	# 				showinfo(title='File Dispatcher', message=f'Upload Success - {record[1]}')
	# 		except NameError:
	# 			showinfo('File Dispatcher', 'Please set your upload file.')
	# 		except Exception as err:
	# 			print(err)


	def toggleCheck(event):
		rowid = tree.identify_row(event.y)
		tag = tree.item(rowid, "tags")[0]
		tags = list(tree.item(rowid, "tags"))
		tags.remove(tag)
		tree.item(rowid, tags=tags)
		if tag == "checked":
			tree.item(rowid, tags="unchecked")
			selected_host.remove(tree.item(rowid)["values"])
		else:
			tree.item(rowid, tags="checked")
			selected_host.append(tree.item(rowid)["values"])
		print(selected_host)


	root = tk.Tk()
	w = 950 # width for the Tk root
	h = 550 # height for the Tk root

	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	root.title("File Dispatcher")
	root.iconbitmap('folder.ico')
	filemenu = tk.Menu(root)
	root.config(menu=filemenu)
	mb1 = tk.Menu(filemenu, tearoff=0)
	mb2 = tk.Menu(filemenu, tearoff=0)
	mb3 = tk.Menu(filemenu, tearoff=0)
	filemenu.add_cascade(label='檔案', menu=mb1)
	filemenu.add_cascade(label='掃描', menu=mb2)
	filemenu.add_cascade(label='幫助', menu=mb3)
	mb1.add_command(label='選擇檔案', command=openf)
	mb2.add_command(label='重新掃描主機', command=scan_hosts)
	mb3.add_command(label='獲得幫助')
	wrapper1 = tk.LabelFrame(root, text="Host List")
	wrapper2 = tk.LabelFrame(root, text="File")
	wrapper1.pack(fill="both", expand="yes", padx=20, pady=10)
	wrapper2.pack(fill="both", expand="yes", padx=20, pady=10)
	tree = ttk.Treeview(wrapper1, columns=(1, 2), height=5)
	style = ttk.Style(tree)
	style.configure("Treeview", rowheight=30)

	im_checked = ImageTk.PhotoImage(Image.open("check.png").resize((25, 25)))
	im_unchecked = ImageTk.PhotoImage(Image.open("uncheck.png").resize((25, 25)))
	tree.tag_configure('checked', image=im_checked)
	tree.tag_configure('unchecked', image=im_unchecked)

	tree.pack(expand=True, fill='both')
	tree.heading("#0", text="")
	tree.heading("#1", text="主機名稱")
	tree.heading("#2", text="IP")

	tree.bind('<Button 1>', toggleCheck)

	# File section
	ent = tk.Entry(wrapper2, width=50)
	ent.pack(side=tk.LEFT, padx=6)
	btn = tk.Button(wrapper2, text='Load File', command=openf)
	btn.pack(side=tk.LEFT, padx=6)

	dbtn = tk.Button(wrapper2, text='Dispatch', command=batch_upload_file)
	dbtn.pack(side=tk.RIGHT, padx=6)

	threading.Thread(target=scan_hosts).start()



	# tree.bind('<<TreeviewSelect>>', item_selected)


	root.mainloop()


if __name__ == '__main__':
	main()
