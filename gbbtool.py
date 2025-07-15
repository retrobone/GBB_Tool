import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class GBBTextureTool:
    def __init__(self, root, gbb_path=None):
        self.root = root
        self.root.title("GBB Texture Viewer & Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="#ececec")

        self.image = None
        self.image_path = None

        self.setup_ui()

        if gbb_path:
            self.load_gbb(gbb_path)

    def setup_ui(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open GBB", command=self.open_gbb)
        file_menu.add_command(label="Export Image", command=self.export_image)
        file_menu.add_command(label="Replace Texture", command=self.replace_texture)
        file_menu.add_command(label="Save GBB", command=self.save_gbb)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Metadata", command=self.toggle_metadata)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

        self.canvas = tk.Canvas(self.root, bg="#ececec", width=800, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.meta_label = tk.Label(self.root, text="", anchor=tk.W, justify=tk.LEFT, bg="#ececec")
        self.meta_label.pack(fill=tk.X)

        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_gbb(self, path):
        try:
            with open(path, "rb") as f:
                data = f.read()

            width = data[0] + (data[1] << 8)
            height = data[2] + (data[3] << 8)
            bpp = data[4]

            ptr = 8
            decompressed = bytearray()
            while ptr < len(data):
                b = data[ptr]
                ptr += 1
                if b < 0x80:
                    repeat_val = data[ptr]
                    ptr += 1
                    decompressed += bytes([repeat_val] * (b + 3))
                else:
                    count = 0x100 - b
                    decompressed += data[ptr:ptr+count]
                    ptr += count

            plane_size = width * height
            r = decompressed[:plane_size]
            g = decompressed[plane_size:plane_size*2]
            b = decompressed[plane_size*2:plane_size*3]

            rgb = bytearray()
            for i in range(plane_size):
                rgb.extend([b[i], g[i], r[i]])

            self.image = Image.frombytes("RGB", (width, height), bytes(rgb))
            self.image_path = path
            self.root.after(100, self.display_image)
            self.status.config(text=f"Loaded {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_gbb(self):
        path = filedialog.askopenfilename(filetypes=[("GBB Files", "*.GBB")])
        if path:
            self.load_gbb(path)

    def display_image(self):
        self.canvas.delete("all")
        if self.image:
            img = self.image.copy()
            img.thumbnail((780, 580))
            self.tk_image = ImageTk.PhotoImage(img)
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = (canvas_width - self.tk_image.width()) // 2
            y = (canvas_height - self.tk_image.height()) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)

    def replace_texture(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.bmp;*.png")])
        if not path:
            return
        try:
            img = Image.open(path).convert("RGB")
            if img.size != self.image.size:
                img = img.resize(self.image.size)
            self.image = img
            self.status.config(text=f"Replaced with {os.path.basename(path)}")
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_image(self):
        if self.image is None:
            messagebox.showwarning("Warning", "No image loaded to export")
            return

        export_path = filedialog.asksaveasfilename(
            defaultextension=".bmp",
            filetypes=[("Bitmap Image", "*.bmp")]
        )
        if export_path:
            try:
                self.image.save(export_path, format="BMP")
                self.status.config(text=f"Image exported to {export_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def save_gbb(self):
        if self.image is None or not self.image_path:
            self.status.config(text="No image loaded to save")
            return

        try:
            width, height = self.image.size
            b, g, r = self.image.split()
            planes = list(r.getdata()) + list(g.getdata()) + list(b.getdata())

            def rle_encode(data):
                encoded = bytearray()
                i = 0
                while i < len(data):
                    run_len = 1
                    while (i + run_len < len(data) and data[i] == data[i + run_len] and run_len < 130):
                        run_len += 1
                    if run_len >= 3:
                        encoded.append(run_len - 3)
                        encoded.append(data[i])
                        i += run_len
                    else:
                        raw_start = i
                        while (i < len(data) and (i + 2 >= len(data) or data[i] != data[i+1] or data[i] != data[i+2]) and (i - raw_start) < 127):
                            i += 1
                        count = i - raw_start
                        encoded.append(0x100 - count)
                        encoded += bytes(data[raw_start:i])
                return encoded

            encoded_data = rle_encode(planes)
            header = bytearray([width & 0xFF, width >> 8, height & 0xFF, height >> 8, 24, 0, 0, 0])
            final_data = header + encoded_data

            backup_path = self.image_path + ".bak"
            if not os.path.exists(backup_path):
                with open(backup_path, "wb") as f:
                    with open(self.image_path, "rb") as original:
                        f.write(original.read())

            with open(self.image_path, "wb") as f:
                f.write(final_data)

            self.status.config(text=f"Saved {os.path.basename(self.image_path)} (backup created)")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def toggle_metadata(self):
        if self.meta_label.cget("text"):
            self.meta_label.config(text="")
        elif self.image:
            w, h = self.image.size
            self.meta_label.config(text=f"Dimensions: {w}x{h}\nFormat: 24-bit RGB")

if __name__ == '__main__':
    import sys
    gbb_arg = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    app = GBBTextureTool(root, gbb_arg)
    root.mainloop()
