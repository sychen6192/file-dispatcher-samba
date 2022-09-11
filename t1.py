import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog as fd
from smb.SMBConnection import SMBConnection
from arp import scan_port, scan
from concurrent.futures import ThreadPoolExecutor
import socket


def main():
	root = tk.Tk()
	w = 950 # width for the Tk root
	h = 550 # height for the Tk root

	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	# set the dimensions of the screen
	# and where it is placed
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	root.title("File Dispatcher")
	root.iconbitmap('folder.ico')
	filemenu = tk.Menu(root, tearoff=False)
	root.config(menu=filemenu)
	mb1 = tk.Menu(filemenu)
	mb2 = tk.Menu(filemenu)
	mb3 = tk.Menu(filemenu)
	filemenu.add_cascade(label='File', menu=mb1)
	filemenu.add_cascade(label='Scan', menu=mb2)
	filemenu.add_cascade(label='Help', menu=mb3)

	def openf():
		global filename
		filetypes = (
			('text files', '*.txt'),
			('All files', '*.*')
		)

		filename = fd.askopenfilename(
			title='Open a file',
			initialdir='/',
			filetypes=filetypes)

		showinfo(
			title='Selected File',
			message=filename
		)

	def scan_hosts():
		tree.delete(*tree.get_children())
		results = scan("192.168.1.1/24")
		with ThreadPoolExecutor(max_workers=6) as executor:
			hosts = executor.map(scan_port, results)
		for host in hosts:
			if host:
				tree.insert('', tk.END, values=host)

	mb1.add_command(label='Open Files', command=openf)
	mb2.add_command(label='Rescan host', command=scan_hosts)
	mb3.add_command(label='Run')
	mb3.add_command(label='Help')
	columns = ('host', 'ip')
	tree = ttk.Treeview(root, columns=columns, show='headings')
	tree.heading("host", text="Host")
	tree.heading("ip", text="IP")
	scan_hosts()

	def upload_file(remote_name, ip, service, path='/'):
		conn = SMBConnection('username', 'password', 'any_name', remote_name)
		assert conn.connect(ip, timeout=3)
		with open(filename, 'rb') as f:
			try:
				conn.storeFile(service, filename.split('/')[-1], f)
			except Exception as err:
				print(err)

	def item_selected(event):
		for selected_item in tree.selection():
			item = tree.item(selected_item)
			record = item['values']
			try:
				if filename:
					print(record[0], record[1])
					upload_file(record[0], record[1], 'MP')
					showinfo(title='Upload Success', message=':'.join(record))
			except Exception as err:
				showinfo('File Dispatcher', 'File not exist!!')

	tree.bind('<<TreeviewSelect>>', item_selected)

	# add a scrollbar
	scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
	tree.configure(yscroll=scrollbar.set)
	scrollbar.grid(row=0, column=1, sticky='ns')
	tree.grid(row=0, column=0, sticky="w" + "e" + "n" + "s")

	root.mainloop()


if __name__ == '__main__':
	main()
