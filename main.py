import tkinter as tk
from tkinter import ttk, Frame, messagebox
from tkinter import N,S,W,E
from tkinter import filedialog as fd
from smb.SMBConnection import SMBConnection
from arp import scan_port, scan
from concurrent.futures import ThreadPoolExecutor
# import socket
import threading

class App(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.CreateUI()
		self.grid(sticky=(N,S,W,E))
		parent.grid_rowconfigure(0, weight=1)
		parent.grid_columnconfigure(0, weight=1)

		self.menubar = tk.Menu(self)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='檔案', menu=self.filemenu)
		self.filemenu.add_command(label='開啟舊檔', command=self.openf)
		self.filemenu.add_command(label='設定目的資料夾', command=self.getf)

		self.scanmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='主機', menu=self.scanmenu)
		self.scanmenu.add_command(label='重新掃描主機', command=self.scan_hosts)
		self.scanmenu.add_command(label='設定網段', command=self.set_network_seg)

		self.helpmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='幫助', menu=self.helpmenu)


		self.master.config(menu=self.menubar)

		# var
		self.filename = ""
		self.dest = ""
		self.hosts = []
		self.myq = []
		self.network_segment = "192.168.1.1/24"
		self.treeview.bind("<Double-1>", self.trigger_upload)
		threading.Thread(target=self.scan_hosts).start()


	def CreateUI(self):
		tv = ttk.Treeview(self)
		tv['show'] = 'headings'
		tv['columns'] = ('Hostname', 'IP', 'Status')
		tv.heading('Hostname', text='Hostname')
		tv.column('Hostname', anchor='center', width=150)
		tv.heading('IP', text='IP')
		tv.column('IP', anchor='center', width=150)
		tv.heading('Status', text='Dispatch status')
		tv.column('Status', anchor='center', width=100)
		tv.grid(sticky=(N, S, W, E))
		self.treeview = tv
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.i = 1

	def openf(self):
		filetypes = (
			('Text files', '*.txt'),
			('All files', '*.*')
		)
		self.filename = fd.askopenfilename(title='開啟檔案', initialdir='/', filetypes=filetypes)
		print(self.filename)

	def getf(self):
		self.dest = fd.askdirectory(title='設定檔案目的地', initialdir='/')
		print(self.dest)

	def scan_hosts(self):
		self.master.config(cursor="watch")
		self.master.update()
		self.hosts.clear()
		self.treeview.delete(*self.treeview.get_children())
		results = scan(self.network_segment)
		with ThreadPoolExecutor(max_workers=64) as executor:
			self.hosts = executor.map(scan_port, results)
		# self.hosts = [("host1", "192.168.1.1", ""), ("host2", "192.168.1.2", ""), ("host3", "192.168.1.3", "")]
		for host in self.hosts:
			if host:
				self.treeview.insert('', tk.END, values=host)
		self.master.config(cursor="")

	def trigger_upload(self, event):
		threading.Thread(target=self.upload_file).start()

	def upload_file(self):
		try:
			status="Failed"
			iid = self.treeview.selection()[0]
			item = self.treeview.item(iid)
			print(item)
			hostname, ip, status = item["values"]
			if not self.filename or not self.dest:
				raise FileNotFoundError
			self.treeview.item(iid, values=(hostname, ip, "Uploading..."))
			conn = SMBConnection('username', 'password', 'any_name', hostname)
			assert conn.connect(ip, timeout=3)
			with open(self.filename, 'rb') as f:
				status = "Success"
				conn.storeFile(self.dest, self.filename.split('/')[-1], f)
		except FileNotFoundError:
			status = "Failed"
			messagebox.showerror(title="SMB File Dispatcher", message="請設定您要傳送的檔案以及目的地!")
		except IndexError:
			pass
		except ConnectionRefusedError:
			status = "Failed"
			messagebox.showerror(title="SMB File Dispatcher", message="連線失敗!")
		except Exception as err:
			status = "Failed"
			print(err)
		finally:
			self.treeview.item(iid, values=(hostname, ip, status))

	def set_network_seg(self):
		self.network_segment = tk.simpledialog.askstring(title="SMB File Dispatcher", prompt="設定區網網段", parent=self.master)



def main():
	root = tk.Tk()
	w = 950
	h = 550 # height for the Tk root

	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	root.title("SMB File Dispatcher")
	root.iconbitmap('folder.ico')
	App(root)
	root.mainloop()


if __name__ == '__main__':
	main()
