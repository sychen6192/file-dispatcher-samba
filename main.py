import tkinter as tk
from tkinter import ttk, Frame, messagebox
from tkinter import N,S,W,E
from tkinter import filedialog as fd
from libs.arp import scan_port
from concurrent.futures import ThreadPoolExecutor
import threading
import base64, os
from libs.icon.folder_icon import img
from tkinter import Toplevel
from libs.network import Network
import ipaddress
import speedcopy
from loguru import logger
from libs.credential import Encrypted, init_license
import warnings
warnings.filterwarnings('ignore')

ACTIVATION_CODE = "QNFUN-HQXLL-C3M1A-K7J9C-UMKGT"
class Network:
    def __init__(self, master):
        self.master = master
        self.w = 220  # width for the Tk root
        self.h = 100  # height for the Tk root
        self.ws = self.master.winfo_screenwidth()  # width of the screen
        self.hs = self.master.winfo_screenheight()  # height of the screen

        self.x = (self.ws / 2) - (self.w / 2)
        self.y = (self.hs / 2) - (self.h / 2)
        self.master.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))
        self.label = ttk.Label(self.master, text="Network segment")
        self.combo = ttk.Combobox(self.master,
                                    values=[
                                        "192.168.1.0/24",
                                        "192.168.61.0/24",
                                        "192.168.62.0/24",
                                        "192.168.63.0/24"])
        self.combo.current(0)
        self.close_button = ttk.Button(self.master, text="Save", command=self.save)
        self.label.pack(side='top', pady=3)
        self.combo.pack(side='top', pady=3)
        self.close_button.pack(side='top', pady=5)

    def save(self):
        app.network_segment = self.combo.get()
        self.master.destroy()


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
		self.filemenu.add_command(label='開啟檔案...', command=self.openf)
		self.filemenu.add_command(label='設定網芳目的資料夾', command=self.getf)

		self.scanmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='主機', menu=self.scanmenu)
		self.scanmenu.add_command(label='重新掃描主機', command=self.scan_hosts)
		self.scanmenu.add_command(label='設定主機網段', command=self.set_network_seg)

		self.helpmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='幫助', menu=self.helpmenu)
		self.helpmenu.add_command(label='驗證序號', command=self.show_license)

		self.master.config(menu=self.menubar)

		# var
		self.src = ""
		self.dest_folder = "dynacard"
		self.dest_path = ""
		self.hosts = []
		self.myq = []
		self.network_segment = "192.168.1.0/24"
		self.treeview.bind("<Double-1>", self.trigger_upload)
		threading.Thread(target=self.scan_hosts).start()

	def CreateUI(self):
		tv = ttk.Treeview(self)
		tv['show'] = 'headings'
		tv['columns'] = ('Hostname', 'IP', 'Status')
		tv.heading('Hostname', text='主機名稱')
		tv.column('Hostname', anchor='center', width=150)
		tv.heading('IP', text='主機IP位址')
		tv.column('IP', anchor='center', width=150)
		tv.heading('Status', text='傳輸狀態')
		tv.column('Status', anchor='center', width=100)
		tv.grid(sticky=(N, S, W, E))
		self.treeview = tv
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.i = 1

	def openf(self):
		filetypes = (
			('All files', '*.*'),
			('Executable files', '*.exe'),
			('Text files', '*.txt')
		)
		self.src = fd.askopenfilenames(title='開新檔案', initialdir='/', filetypes=filetypes)
		logger.info(f"Set Source to: {self.src}")

	def getf(self):
		destination = fd.askdirectory(title='設定檔案目的地', initialdir='/')
		if destination:
			self.dest_folder = destination.split("/")[3]
			self.dest_path = "/".join(destination.split("/")[4:])
			logger.info(f"Set Destination: {self.dest_folder}/{self.dest_path}")

	def scan_hosts(self):
		self.hosts = []
		self.master.config(cursor="watch")
		self.master.update()
		self.treeview.delete(*self.treeview.get_children())
		hosts_ip = [str(ip) for ip in ipaddress.IPv4Network(self.network_segment)]
		with ThreadPoolExecutor(max_workers=255) as executor:
			self.hosts = executor.map(scan_port, hosts_ip)
		for host in self.hosts:
			if host:
				self.treeview.insert('', tk.END, values=host)
		self.master.config(cursor="")

	def show_license(self):
		tk.messagebox.showinfo(title="SMB File Dispatcher", message=f"Your license code: {ACTIVATION_CODE}")


	def trigger_upload(self, event):
		threading.Thread(target=self.upload_file).start()

	def upload_file(self):
		try:
			status = "處理中..."
			iid = self.treeview.selection()[0]
			item = self.treeview.item(iid)
			hostname, ip_address, status = item["values"]
			if not self.src:
				raise FileNotFoundError
			self.treeview.item(iid, values=(hostname, ip_address, "Uploading..."))
			for src_item in self.src:
				destination = fr'//{hostname}/{self.dest_folder}/{self.dest_path}/{src_item.split("/")[-1]}'
				logger.info(f"Transfer file from {src_item} to {destination}")
				speedcopy.copyfile(src_item, f"{destination}")
			status = "上傳成功"

		except FileNotFoundError:
			status = "上傳失敗"
			messagebox.showerror(title="SMB File Dispatcher", message="請設定您要傳送的檔案以及目的地")
		except IndexError:
			pass
		except Exception as err:
			status = "上傳失敗"
			logger.error(err)
		finally:
			self.treeview.item(iid, values=(hostname, ip_address, status))

	def set_network_seg(self):
		self.networkpack = Toplevel(self)
		self.networkpack.title("網段設定")
		Network(self.networkpack)



def main():
	global app
	root = tk.Tk()
	w = 950
	h = 550 # height for the Tk root

	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	root.title("SMB File Dispatcher v1.2 beta")
	# 加上icon
	ico = open('folder.ico', 'wb+')
	ico.write(base64.b64decode(img))  # 寫一個icon出來
	ico.close()
	root.iconbitmap('folder.ico')  # 將icon嵌上視窗
	os.remove('folder.ico')  # 把剛剛用完的檔案刪掉
	app = App(root)
	root.mainloop()


if __name__ == '__main__':
	if init_license(ACTIVATION_CODE) == 1:
		main()
		#https://gist.githubusercontent.com/sychen6192/82a0a3e2428d2dee0e55df2cdf95050b/raw
	else:
		root = tk.Tk()
		root.withdraw()
		tk.messagebox.showerror("SMB File Dispatcher", "License Expired")