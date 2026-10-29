"""A local desktop switch. No server, telemetry, or browser extension."""

from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from . import BetterWayError, __version__
from .manager import Manager
from .runner import execute


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.manager = Manager()
        self.events = Queue()
        self.busy = False
        root.title("BetterWay �� ���Ž⿪��")
        root.geometry("900x810")
        root.minsize(780, 760)
        root.configure(bg="#f4f6fa")
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", foreground="#27344b", font=("Microsoft YaHei UI", 10))
        style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(14, 8))
        style.configure("Accent.TButton", background="#2364cf", foreground="white")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 24, "bold"), foreground="#172b4d")
        style.configure("Status.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Small.TLabel", font=("Microsoft YaHei UI", 9), foreground="#556176")
        outer = ttk.Frame(root, padding=26)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="BetterWay", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="���Ž⿪��  ��  �����ҷ�������֤���ټ���", style="Small.TLabel").pack(anchor="w", pady=(0, 16))
        bar = ttk.Frame(outer)
        bar.pack(fill="x")
        self.status_text = tk.StringVar()
        ttk.Label(bar, textvariable=self.status_text, style="Status.TLabel").pack(side="left")
        self.on_button = ttk.Button(bar, text="����", style="Accent.TButton", command=lambda: self.switch(True))
        self.on_button.pack(side="right", padx=(8, 0))
        self.off_button = ttk.Button(bar, text="�ر�", command=lambda: self.switch(False))
        self.off_button.pack(side="right")
        self.details = tk.StringVar()
        ttk.Label(outer, textvariable=self.details, wraplength=820, style="Small.TLabel").pack(anchor="w", pady=(8, 10))
        ttk.Separator(outer).pack(fill="x", pady=(0, 12))
        ttk.Label(outer, text="ȫ�ֹ��������������Ϊָ����ӳ̶�ȡ���ڿͻ��˺�ģ�͡�", wraplength=820).pack(anchor="w")
        ttk.Label(outer, text="�·�������ڣ�����ʱ�ɳ�����������û����Ч��Դ��ֹͣ���ر�ʱֱ�ӵ��á�", wraplength=820).pack(anchor="w", pady=(4, 12))
        options = ttk.Frame(outer)
        options.pack(fill="x")
        ttk.Label(options, text="������Դ").pack(side="left")
        self.provider = tk.StringVar()
        self.provider_box = ttk.Combobox(options, textvariable=self.provider, values=["github", "brave", "deepseek"], state="readonly", width=13)
        self.provider_box.pack(side="left", padx=(8, 20))
        self.provider_box.bind("<<ComboboxSelected>>", self.change_provider)
        ttk.Label(options, text="ִ�й���").pack(side="left")
        self.agent = tk.StringVar(value="codex")
        ttk.Combobox(options, textvariable=self.agent, values=["codex", "claude", "deepseek"], state="readonly", width=13).pack(side="left", padx=8)
        ttk.Label(outer, text="GitHub ������Դ��Ŀ��Brave ������ҳ��Brave / DeepSeek ���������� API ��Կ���ȡ�", style="Small.TLabel", wraplength=820).pack(anchor="w", pady=(7, 12))
        ttk.Label(outer, text="����").pack(anchor="w")
        self.prompt = ScrolledText(outer, height=4, wrap="word", font=("Microsoft YaHei UI", 10), relief="flat", padx=10, pady=8)
        self.prompt.pack(fill="x", pady=(5, 10))
        query_line = ttk.Frame(outer)
        query_line.pack(fill="x")
        ttk.Label(query_line, text="�����ؼ���").pack(side="left")
        self.query = tk.StringVar()
        ttk.Entry(query_line, textvariable=self.query).pack(side="left", fill="x", expand=True, padx=(10, 0))
        ttk.Label(outer, text="�������̹ؼ��ʣ��� pdf extraction�����ջᷢ������ͷ����� 180 �ַ�������ɨ�豾���ļ���", style="Small.TLabel", wraplength=820).pack(anchor="w", pady=(4, 10))
        path_line = ttk.Frame(outer)
        path_line.pack(fill="x")
        ttk.Label(path_line, text="����Ŀ¼").pack(side="left")
        self.directory = tk.StringVar(value=str(Path.cwd()))
        ttk.Entry(path_line, textvariable=self.directory).pack(side="left", fill="x", expand=True, padx=10)
        ttk.Button(path_line, text="ѡ��", command=self.choose_directory).pack(side="right")
        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=12)
        self.run_button = ttk.Button(controls, text="ִ������", style="Accent.TButton", command=self.run)
        self.run_button.pack(side="left")
        ttk.Button(controls, text="ˢ��״̬", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(controls, text="ж�ع���", command=self.uninstall).pack(side="right")
        self.output = ScrolledText(outer, height=7, wrap="word", font=("Consolas", 10), relief="flat", padx=10, pady=8, state="disabled")
        ttk.Label(outer, text=f"v{__version__}  ��  ���ر������á����ݺ�����֤�ݣ�����¼�������Ļ���Կ��", style="Small.TLabel", wraplength=800).pack(side="bottom", anchor="w", pady=(10, 0))
        self.output.pack(fill="both", expand=True)
        self.refresh()
        root.after(150, self.poll)

    def write(self, text: str):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh(self):
        try:
            state = self.manager.status()
            self.status_text.set("�� �ѿ���" if state["enabled"] else "�� �ѹر�")
            self.provider.set(state["provider"])
            names = ", ".join(state["targets"]) or "��δ��װȫ�ֹ���"
            drift = any(not info["matches"] for info in state["targets"].values())
            self.details.set(f"���䣺{names}  |  {'���÷����仯�������ļ�����ʹ��' if drift else '����״̬һ��'}\n���ã�{state['home']}")
        except (BetterWayError, OSError) as exc:
            self.status_text.set("������Ҫ���")
            self.details.set(str(exc))

    def switch(self, enabled: bool):
        if self.busy:
            return
        try:
            self.manager.switch(enabled)
            self.refresh()
            self.write("�ѿ�����ȫ�ֹ������»Ự���أ�������ڻ���������" if enabled else "�ѹرգ����Ƴ������߹���������ڲ���׷���������衣ԭ������ָ���Ա�����")
        except (BetterWayError, OSError) as exc:
            messagebox.showerror("����δ���", str(exc), parent=self.root)

    def change_provider(self, event=None):
        try:
            self.manager.provider(self.provider.get())
        except (BetterWayError, OSError) as exc:
            messagebox.showerror("����δ����", str(exc), parent=self.root)
            self.refresh()

    def choose_directory(self):
        path = filedialog.askdirectory(parent=self.root)
        if path:
            self.directory.set(path)

    def uninstall(self):
        if self.busy:
            return
        try:
            self.manager.uninstall()
            self.refresh()
            self.write("���Ƴ� BetterWay �йܹ��򡣱��ݺ�֤�����ڱ��ر�����")
        except (BetterWayError, OSError) as exc:
            messagebox.showerror("ж��δ���", str(exc), parent=self.root)

    def run(self):
        if self.busy:
            return
        prompt = self.prompt.get("1.0", "end-1c")
        if not prompt.strip():
            messagebox.showinfo("��д����", "������������", parent=self.root)
            return
        agent, query, directory = self.agent.get(), self.query.get().strip() or None, self.directory.get()
        try:
            enabled = self.manager.store.load()["enabled"]
        except (BetterWayError, OSError) as exc:
            self.write(str(exc))
            return
        self.busy = True
        for widget in (self.run_button, self.on_button, self.off_button, self.provider_box):
            widget.configure(state="disabled")
        self.write("����������ȡ����Ч��Դ��ŵ��ÿͻ��ˡ���" if enabled else "����ֱ�ӵ��ÿͻ��ˣ������������ѹرգ�����")

        def work():
            try:
                code, output = execute(agent, prompt, query, directory, store=self.manager.store, capture=True)
                self.events.put(f"{output}\nִ�н������˳��� {code}��")
            except Exception as exc:
                self.events.put(f"ִ��ֹͣ��{exc}")
        Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            result = self.events.get_nowait()
        except Empty:
            pass
        else:
            self.write(result)
            self.busy = False
            for widget in (self.run_button, self.on_button, self.off_button):
                widget.configure(state="normal")
            self.provider_box.configure(state="readonly")
        self.root.after(150, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("����������", "��ȴ����������ǿ�н������ڲ��ܱ�֤���οͻ���һ��ֹͣ��", parent=self.root)
            return
        self.root.destroy()


def main():
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except tk.TclError as exc:
        raise BetterWayError("�޷�����ͼ�ν��档��ȷ���Ѱ�װ tkinter����ʹ�� betterway on / off��") from exc


if __name__ == "__main__":
    main()
