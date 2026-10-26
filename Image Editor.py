import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import (
    Image,
    ImageTk,
    ImageOps,
    ImageEnhance,
    ImageFilter,
)


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZaBir | Image Editor")
        self.root.geometry("1250x800")
        self.root.minsize(950, 650)

        # -------------------------------------------------
        # CREAM WHITE THEME - ORIGINAL COLORS PRESERVED
        # -------------------------------------------------
        self.bg = "#F8F5EE"
        self.panel = "#FFFCF6"
        self.panel_2 = "#F1EBDD"
        self.panel_3 = "#E5DCCB"

        self.text = "#292524"
        self.muted = "#78716C"

        self.accent = "#8B7CFF"
        self.accent_hover = "#A69AFF"

        self.border = "#DED5C5"
        self.green = "#20A879"
        self.red = "#E05268"
        self.canvas_bg = "#F0EBE1"

        self.root.configure(bg=self.bg)

        # Image state
        self.original_image = None
        self.current_image = None
        self.preview_image = None
        self.image_tk = None
        self.current_path = None

        self.display_scale = 1.0
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        # -------------------------------------------------
        # NEW FEATURE: MOVABLE IMAGE
        # -------------------------------------------------
        # Image position is stored as an offset from the
        # center of the preview canvas.
        self.image_offset_x = 0
        self.image_offset_y = 0

        # Mouse dragging state
        self.drag_start = None
        self.drag_origin = None
        self.preview_item_id = None

        # Undo and redo history
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 10

        # Slider processing
        self.slider_after_id = None
        self.processing = False

        # Crop selection
        self.crop_mode = False
        self.crop_start = None
        self.crop_rectangle = None

        self.slider_vars = {}
        self.slider_labels = {}
        self.slider_widgets = {}

        # Original slider features preserved
        self.slider_defaults = {
            "Brightness": 100,
            "Contrast": 100,
            "Exposure": 100,
            "Highlights": 0,
            "Shadows": 0,
            "Saturation": 100,
            "Temperature": 0,
            "Vibrance": 100,
            "Sharpness": 100,
            "Clarity": 0,
            "Vignette": 0,
        }

        self._configure_styles()
        self._build_ui()
        self._bind_events()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    # -------------------------------------------------
    # STYLES
    # -------------------------------------------------

    def _configure_styles(self):
        style = ttk.Style(self.root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Original modern beige scrollbar
        style.configure(
            "Studio.Vertical.TScrollbar",
            background="#B8AFA0",
            troughcolor="#F1EBDD",
            bordercolor="#F1EBDD",
            lightcolor="#B8AFA0",
            darkcolor="#B8AFA0",
            arrowcolor="#FFFFFF",
            width=7,
            relief="flat",
        )

        style.map(
            "Studio.Vertical.TScrollbar",
            background=[
                ("active", "#9488D8"),
                ("pressed", "#7C6FD0"),
            ],
            troughcolor=[
                ("active", "#E5DCCB"),
            ],
        )

    def _make_button(
        self,
        parent,
        text,
        command,
        bg=None,
        fg=None,
        hover=None,
        width=None,
    ):
        bg = bg or self.panel_2
        fg = fg or self.text
        hover = hover or self.panel_3

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=9,
            width=width,
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=hover),
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=bg),
        )

        return button

    # -------------------------------------------------
    # USER INTERFACE
    # -------------------------------------------------

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=20, pady=(16, 12))

        brand_frame = tk.Frame(header, bg=self.bg)
        brand_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            brand_frame,
            text="📷 ZaBir HaSan",
            font=("Segoe UI", 23, "bold"),
            bg=self.bg,
            fg=self.text,
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="ZHB IMAGE EDITOR",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg,
            fg=self.muted,
        ).pack(anchor="w", pady=(0, 2))

        header_buttons = tk.Frame(header, bg=self.bg)
        header_buttons.pack(side="right")

        self._make_button(
            header_buttons,
            "Open Image",
            self.open_image,
            bg=self.accent,
            fg="#FFFFFF",
            hover=self.accent_hover,
        ).pack(side="left", padx=(0, 8))

        self._make_button(
            header_buttons,
            "Undo",
            self.undo,
        ).pack(side="left", padx=(0, 8))

        self._make_button(
            header_buttons,
            "Redo",
            self.redo,
        ).pack(side="left", padx=(0, 8))

        self._make_button(
            header_buttons,
            "Save Image",
            self.save_image,
            bg=self.green,
            fg="#FFFFFF",
            hover="#168B64",
        ).pack(side="left", padx=(0, 8))

        self._make_button(
            header_buttons,
            "Exit",
            self.exit_app,
            bg=self.red,
            fg="#FFFFFF",
            hover="#C83D53",
        ).pack(side="left")

        # Main body
        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        body.grid_columnconfigure(0, weight=8, uniform="main")
        body.grid_columnconfigure(1, weight=3, uniform="main")
        body.grid_rowconfigure(0, weight=1)

        # Preview panel
        self.preview_card = tk.Frame(
            body,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1,
        )

        self.preview_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 12),
        )

        preview_header = tk.Frame(
            self.preview_card,
            bg=self.panel,
        )

        preview_header.pack(
            fill="x",
            padx=18,
            pady=(15, 10),
        )

        tk.Label(
            preview_header,
            text="Image Preview",
            font=("Segoe UI", 14, "bold"),
            bg=self.panel,
            fg=self.text,
        ).pack(side="left")

        self.status_label = tk.Label(
            preview_header,
            text="READY",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_2,
            fg=self.green,
            padx=10,
            pady=5,
        )

        self.status_label.pack(side="right")

        canvas_container = tk.Frame(
            self.preview_card,
            bg=self.canvas_bg,
            highlightbackground=self.border,
            highlightthickness=1,
        )

        canvas_container.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 12),
        )

        self.preview_canvas = tk.Canvas(
            canvas_container,
            bg=self.canvas_bg,
            highlightthickness=0,
            bd=0,
            cursor="crosshair",
        )

        self.preview_canvas.pack(fill="both", expand=True)

        self.preview_canvas.bind(
            "<Configure>",
            self._on_canvas_resize,
        )

        # Original mouse bindings retained.
        # These methods now support both dragging and cropping.
        self.preview_canvas.bind(
            "<ButtonPress-1>",
            self._crop_start_event,
        )

        self.preview_canvas.bind(
            "<B1-Motion>",
            self._crop_drag_event,
        )

        self.preview_canvas.bind(
            "<ButtonRelease-1>",
            self._crop_release_event,
        )

        preview_footer = tk.Frame(
            self.preview_card,
            bg=self.panel,
        )

        preview_footer.pack(
            fill="x",
            padx=18,
            pady=(0, 14),
        )

        self.file_label = tk.Label(
            preview_footer,
            text="No image selected",
            font=("Segoe UI", 9),
            bg=self.panel,
            fg=self.muted,
            anchor="w",
        )

        self.file_label.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.zoom_label = tk.Label(
            preview_footer,
            text="FIT",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel,
            fg=self.accent,
        )

        self.zoom_label.pack(side="right")

        # Editor panel
        self.edit_card = tk.Frame(
            body,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1,
        )

        self.edit_card.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        edit_header = tk.Frame(
            self.edit_card,
            bg=self.panel,
        )

        edit_header.pack(
            fill="x",
            padx=16,
            pady=(15, 8),
        )

        tk.Label(
            edit_header,
            text="Edit Image",
            font=("Segoe UI", 14, "bold"),
            bg=self.panel,
            fg=self.text,
        ).pack(side="left")

        tk.Label(
            edit_header,
            text="ADJUSTMENTS",
            font=("Segoe UI", 8, "bold"),
            bg=self.panel,
            fg=self.muted,
        ).pack(side="right")

        # Scrollable editor area
        scroll_container = tk.Frame(
            self.edit_card,
            bg=self.panel,
        )

        scroll_container.pack(
            fill="both",
            expand=True,
            padx=(10, 4),
            pady=(0, 6),
        )

        self.edit_canvas = tk.Canvas(
            scroll_container,
            bg=self.panel,
            highlightthickness=0,
            bd=0,
        )

        self.edit_canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            scroll_container,
            orient="vertical",
            command=self.edit_canvas.yview,
            style="Studio.Vertical.TScrollbar",
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(3, 3),
            pady=5,
        )

        self.edit_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.controls_frame = tk.Frame(
            self.edit_canvas,
            bg=self.panel,
        )

        self.controls_window = self.edit_canvas.create_window(
            (0, 0),
            window=self.controls_frame,
            anchor="nw",
        )

        self.controls_frame.bind(
            "<Configure>",
            self._update_scroll_region,
        )

        self.edit_canvas.bind(
            "<Configure>",
            self._resize_controls_frame,
        )

        self._build_adjustment_controls()
        self._build_transform_controls()

        # Bottom action buttons
        action_frame = tk.Frame(
            self.edit_card,
            bg=self.panel,
        )

        action_frame.pack(
            fill="x",
            padx=12,
            pady=(4, 12),
        )

        self._make_button(
            action_frame,
            "Reset Edits",
            self.reset_edits,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5),
        )

        self._make_button(
            action_frame,
            "Reset All",
            self.reset_all,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
        )

        self._make_button(
            action_frame,
            "Save",
            self.save_image,
            bg=self.green,
            fg="#FFFFFF",
            hover="#168B64",
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0),
        )

        # Footer
        footer = tk.Frame(self.root, bg=self.bg)

        footer.pack(
            fill="x",
            padx=20,
            pady=(0, 12),
        )

        tk.Label(
            footer,
            text=(
                "TIP  •  Drag to move image  •  Scroll to zoom"
                "  •  Ctrl + O to open  •  Ctrl + S to save"
            ),
            font=("Segoe UI", 9),
            bg=self.bg,
            fg=self.muted,
        ).pack(side="left")

        tk.Label(
            footer,
            text="Powered by Python",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg,
            fg=self.accent,
        ).pack(side="right")

        self._show_empty_state()

    # -------------------------------------------------
    # ADJUSTMENT CONTROLS
    # -------------------------------------------------

    def _build_adjustment_controls(self):
        sections = [
            (
                "LIGHT",
                [
                    ("Brightness", 0, 200),
                    ("Contrast", 0, 200),
                    ("Exposure", 0, 200),
                    ("Highlights", -100, 100),
                    ("Shadows", -100, 100),
                ],
            ),
            (
                "COLOR",
                [
                    ("Saturation", 0, 200),
                    ("Temperature", -100, 100),
                    ("Vibrance", 0, 200),
                ],
            ),
            (
                "DETAILS",
                [
                    ("Sharpness", 0, 200),
                    ("Clarity", 0, 100),
                    ("Vignette", 0, 100),
                ],
            ),
        ]

        for section_title, sliders in sections:
            section = tk.Frame(
                self.controls_frame,
                bg=self.panel,
            )

            section.pack(
                fill="x",
                padx=8,
                pady=(6, 4),
            )

            tk.Label(
                section,
                text=section_title,
                font=("Segoe UI", 9, "bold"),
                bg=self.panel,
                fg=self.accent,
            ).pack(
                anchor="w",
                pady=(4, 6),
            )

            for name, minimum, maximum in sliders:
                self._create_slider(
                    section,
                    name,
                    minimum,
                    maximum,
                )

    def _create_slider(self, parent, name, minimum, maximum):
        card = tk.Frame(
            parent,
            bg=self.panel_2,
            highlightbackground=self.border,
            highlightthickness=1,
        )

        card.pack(fill="x", pady=4)

        top = tk.Frame(card, bg=self.panel_2)
        top.pack(fill="x", padx=10, pady=(7, 0))

        tk.Label(
            top,
            text=name,
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_2,
            fg=self.text,
        ).pack(side="left")

        value_label = tk.Label(
            top,
            text=str(self.slider_defaults[name]),
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_2,
            fg=self.accent,
            width=5,
            anchor="e",
        )

        value_label.pack(side="right")

        variable = tk.DoubleVar(
            value=self.slider_defaults[name]
        )

        slider = tk.Scale(
            card,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            resolution=1,
            showvalue=False,
            variable=variable,
            bg=self.panel_2,
            fg=self.text,
            troughcolor="#D8D0C2",
            activebackground="#8B7CFF",
            highlightthickness=0,
            bd=0,
            relief="flat",
            sliderrelief="flat",
            cursor="hand2",
            command=lambda value, key=name: self._on_slider_change(
                key, value
            ),
        )

        slider.pack(
            fill="x",
            padx=8,
            pady=(0, 5),
        )

        self.slider_vars[name] = variable
        self.slider_labels[name] = value_label
        self.slider_widgets[name] = slider

    # -------------------------------------------------
    # TRANSFORM CONTROLS
    # -------------------------------------------------

    def _build_transform_controls(self):
        section = tk.Frame(
            self.controls_frame,
            bg=self.panel,
        )

        section.pack(
            fill="x",
            padx=8,
            pady=(10, 12),
        )

        tk.Label(
            section,
            text="TRANSFORM",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel,
            fg=self.accent,
        ).pack(
            anchor="w",
            pady=(4, 8),
        )

        row1 = tk.Frame(section, bg=self.panel)
        row1.pack(fill="x", pady=3)

        self._make_button(
            row1,
            "Rotate Left",
            lambda: self.transform_image("rotate_left"),
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )

        self._make_button(
            row1,
            "Rotate Right",
            lambda: self.transform_image("rotate_right"),
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )

        row2 = tk.Frame(section, bg=self.panel)
        row2.pack(fill="x", pady=3)

        self._make_button(
            row2,
            "Flip Horizontal",
            lambda: self.transform_image("flip_horizontal"),
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )

        self._make_button(
            row2,
            "Flip Vertical",
            lambda: self.transform_image("flip_vertical"),
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )

        row3 = tk.Frame(section, bg=self.panel)
        row3.pack(fill="x", pady=3)

        self._make_button(
            row3,
            "Crop Image",
            self.start_crop,
            bg=self.accent,
            fg="#FFFFFF",
            hover=self.accent_hover,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )

        self._make_button(
            row3,
            "Apply Crop",
            self.apply_crop,
            bg=self.green,
            fg="#FFFFFF",
            hover="#168B64",
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )

        self._make_button(
            section,
            "Cancel Crop",
            self.cancel_crop,
        ).pack(fill="x", pady=(4, 0))

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def _bind_events(self):
        self.root.bind(
            "<Control-o>",
            lambda event: self.open_image(),
        )

        self.root.bind(
            "<Control-O>",
            lambda event: self.open_image(),
        )

        self.root.bind(
            "<Control-s>",
            lambda event: self.save_image(),
        )

        self.root.bind(
            "<Control-S>",
            lambda event: self.save_image(),
        )

        self.root.bind(
            "<Escape>",
            lambda event: self.cancel_crop(),
        )

        self.preview_canvas.bind(
            "<MouseWheel>",
            self._mouse_wheel_zoom,
        )

        self.preview_canvas.bind(
            "<Button-4>",
            lambda event: self._zoom_by(1.1),
        )

        self.preview_canvas.bind(
            "<Button-5>",
            lambda event: self._zoom_by(1 / 1.1),
        )

        self.edit_canvas.bind(
            "<MouseWheel>",
            self._editor_mousewheel,
        )

        self.controls_frame.bind(
            "<MouseWheel>",
            self._editor_mousewheel,
        )

    def _editor_mousewheel(self, event):
        self.edit_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units",
        )

    def _update_scroll_region(self, event=None):
        self.edit_canvas.configure(
            scrollregion=self.edit_canvas.bbox("all")
        )

    def _resize_controls_frame(self, event):
        self.edit_canvas.itemconfigure(
            self.controls_window,
            width=event.width,
        )

    def _on_canvas_resize(self, event=None):
        if self.current_image is not None:
            self.root.after_idle(self.render_preview)

    # -------------------------------------------------
    # OPEN IMAGE
    # -------------------------------------------------

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                (
                    "Image files",
                    "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp",
                ),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        try:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")

            self.original_image = image.copy()
            self.current_image = image.copy()
            self.current_path = path

            self.undo_stack.clear()
            self.redo_stack.clear()

            self._reset_slider_values()
            self.cancel_crop()

            self.zoom = 1.0

            # NEW: Center every newly opened image.
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.drag_start = None
            self.drag_origin = None
            self.preview_item_id = None

            self.status_label.configure(
                text="IMAGE LOADED",
                fg=self.green,
            )

            self.file_label.configure(
                text=(
                    f"{os.path.basename(path)}  •  "
                    f"{image.width} × {image.height} px"
                )
            )

            self.render_preview()

        except Exception as error:
            messagebox.showerror(
                "Open Image Error",
                f"Could not open this image.\n\n{error}",
            )

    # -------------------------------------------------
    # SLIDER HANDLING
    # -------------------------------------------------

    def _on_slider_change(self, name, value):
        self.slider_labels[name].configure(
            text=str(int(float(value)))
        )

        if self.slider_after_id is not None:
            try:
                self.root.after_cancel(self.slider_after_id)
            except tk.TclError:
                pass

        if self.current_image is None:
            return

        self.slider_after_id = self.root.after(
            65,
            self._render_slider_preview,
        )

    def _render_slider_preview(self):
        self.slider_after_id = None

        if self.current_image is None or self.processing:
            return

        self.processing = True

        try:
            self.render_preview()
        finally:
            self.processing = False

    def _reset_slider_values(self):
        for name, default in self.slider_defaults.items():
            self.slider_vars[name].set(default)
            self.slider_labels[name].configure(
                text=str(default)
            )

    def _get_adjustments(self):
        return {
            name: float(variable.get())
            for name, variable in self.slider_vars.items()
        }

    # -------------------------------------------------
    # IMAGE PROCESSING
    # -------------------------------------------------

    @staticmethod
    def _clip_array(array):
        return np.clip(array, 0, 255).astype(np.uint8)

    def process_image(self, image):
        adjustments = self._get_adjustments()

        arr = np.asarray(
            image.convert("RGB"),
            dtype=np.float32,
        ) / 255.0

        # Exposure
        exposure = adjustments["Exposure"] / 100.0
        arr *= 2.0 ** ((exposure - 1.0) * 2.0)

        # Brightness
        brightness = adjustments["Brightness"] / 100.0
        arr *= brightness

        # Contrast
        contrast = adjustments["Contrast"] / 100.0
        arr = (arr - 0.5) * contrast + 0.5

        # Highlights
        luminance = (
            0.2126 * arr[:, :, 0]
            + 0.7152 * arr[:, :, 1]
            + 0.0722 * arr[:, :, 2]
        )

        highlights = adjustments["Highlights"] / 100.0

        highlight_mask = np.clip(
            (luminance - 0.45) / 0.55,
            0,
            1,
        ) ** 2

        arr += (
            highlight_mask[:, :, None]
            * highlights
            * 0.45
        )

        # Shadows
        shadows = adjustments["Shadows"] / 100.0

        shadow_mask = np.clip(
            (0.65 - luminance) / 0.65,
            0,
            1,
        ) ** 2

        arr += (
            shadow_mask[:, :, None]
            * shadows
            * 0.40
        )

        arr = np.clip(arr, 0, 1)

        # Saturation
        saturation = adjustments["Saturation"] / 100.0

        gray = (
            0.2126 * arr[:, :, 0]
            + 0.7152 * arr[:, :, 1]
            + 0.0722 * arr[:, :, 2]
        )

        arr = (
            gray[:, :, None]
            + (arr - gray[:, :, None]) * saturation
        )

        # Temperature
        temperature = adjustments["Temperature"] / 100.0

        arr[:, :, 0] += temperature * 0.12
        arr[:, :, 1] += temperature * 0.025
        arr[:, :, 2] -= temperature * 0.12

        # Vibrance
        vibrance = adjustments["Vibrance"] / 100.0

        gray = (
            0.2126 * arr[:, :, 0]
            + 0.7152 * arr[:, :, 1]
            + 0.0722 * arr[:, :, 2]
        )

        saturation_amount = (
            np.max(arr, axis=2)
            - np.min(arr, axis=2)
        )

        vibrance_mask = 1.0 - np.clip(
            saturation_amount,
            0,
            1,
        )

        vibrance_strength = (vibrance - 1.0) * 0.8

        arr += (
            (arr - gray[:, :, None])
            * vibrance_mask[:, :, None]
            * vibrance_strength
        )

        arr = np.clip(arr, 0, 1)

        # Vignette
        vignette = adjustments["Vignette"] / 100.0

        if vignette > 0:
            height, width = arr.shape[:2]

            y, x = np.ogrid[
                -1:1:complex(height),
                -1:1:complex(width),
            ]

            distance = np.sqrt(x * x + y * y)

            mask = np.clip(
                1.0 - distance * vignette * 0.65,
                0.25,
                1.0,
            )

            arr *= mask[:, :, None]

        result = Image.fromarray(
            self._clip_array(arr * 255.0),
            mode="RGB",
        )

        # Sharpness
        sharpness = adjustments["Sharpness"] / 100.0

        if abs(sharpness - 1.0) > 0.01:
            result = ImageEnhance.Sharpness(
                result
            ).enhance(sharpness)

        # Clarity
        clarity = adjustments["Clarity"] / 100.0

        if clarity > 0:
            blurred = result.filter(
                ImageFilter.GaussianBlur(radius=2.0)
            )

            original_array = np.asarray(
                result,
                dtype=np.float32,
            )

            blurred_array = np.asarray(
                blurred,
                dtype=np.float32,
            )

            detail = original_array - blurred_array

            enhanced = (
                original_array
                + detail * clarity * 1.5
            )

            result = Image.fromarray(
                self._clip_array(enhanced)
            )

        return result

    # -------------------------------------------------
    # PREVIEW
    # -------------------------------------------------

    def _show_empty_state(self):
        self.preview_canvas.delete("all")

        self.preview_item_id = None

        width = max(
            self.preview_canvas.winfo_width(),
            300,
        )

        height = max(
            self.preview_canvas.winfo_height(),
            250,
        )

        self.preview_canvas.create_text(
            width // 2,
            height // 2 - 20,
            text="Your image will appear here",
            fill=self.text,
            font=("Segoe UI", 17, "bold"),
        )

        self.preview_canvas.create_text(
            width // 2,
            height // 2 + 15,
            text="Click 'Open Image' to get started",
            fill=self.muted,
            font=("Segoe UI", 10),
        )

    def render_preview(self):
        if self.current_image is None:
            self._show_empty_state()
            return

        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        if canvas_width < 50 or canvas_height < 50:
            return

        source = self.current_image
        source_width, source_height = source.size

        fit_scale = min(
            (canvas_width - 30) / source_width,
            (canvas_height - 30) / source_height,
            1.0,
        )

        display_scale = fit_scale * self.zoom

        display_width = max(
            1,
            int(source_width * display_scale),
        )

        display_height = max(
            1,
            int(source_height * display_scale),
        )

        # Reduce preview processing size for better performance.
        max_preview_dimension = 1200

        preview_scale = min(
            1.0,
            max_preview_dimension / max(
                source_width,
                source_height,
            ),
        )

        if preview_scale < 1.0:
            preview_source = source.resize(
                (
                    max(1, int(source_width * preview_scale)),
                    max(1, int(source_height * preview_scale)),
                ),
                Image.Resampling.BILINEAR,
            )
        else:
            preview_source = source

        processed = self.process_image(preview_source)

        processed = processed.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS,
        )

        self.preview_image = processed
        self.image_tk = ImageTk.PhotoImage(processed)

        self.preview_canvas.delete("all")

        # NEW: Render the image at its movable position.
        center_x = (
            canvas_width // 2
            + self.image_offset_x
        )

        center_y = (
            canvas_height // 2
            + self.image_offset_y
        )

        self.preview_item_id = (
            self.preview_canvas.create_image(
                center_x,
                center_y,
                image=self.image_tk,
                anchor="center",
                tags="preview_image",
            )
        )

        self.display_scale = display_scale

        # Change cursor when dragging or cropping.
        if self.crop_mode:
            self.preview_canvas.configure(cursor="crosshair")
        else:
            self.preview_canvas.configure(cursor="fleur")

        if self.zoom == 1.0:
            self.zoom_label.configure(text="FIT")
        else:
            self.zoom_label.configure(
                text=f"{int(self.zoom * 100)}%"
            )

    # -------------------------------------------------
    # ZOOM
    # -------------------------------------------------

    def _mouse_wheel_zoom(self, event):
        if self.current_image is None:
            return

        if event.delta > 0:
            self._zoom_by(1.1)
        elif event.delta < 0:
            self._zoom_by(1 / 1.1)

    def _zoom_by(self, factor):
        if self.current_image is None:
            return

        self.zoom *= factor

        self.zoom = max(
            self.min_zoom,
            min(self.max_zoom, self.zoom),
        )

        self.render_preview()

    # -------------------------------------------------
    # NEW FEATURE: MOVE IMAGE WITH MOUSE
    # -------------------------------------------------

    def _is_inside_preview_image(self, x, y):
        """
        Check whether the mouse position is inside the
        displayed image rather than the empty canvas.
        """

        if (
            self.current_image is None
            or self.preview_item_id is None
        ):
            return False

        bounds = self.preview_canvas.bbox(
            self.preview_item_id
        )

        if not bounds:
            return False

        left, top, right, bottom = bounds

        return (
            left <= x <= right
            and top <= y <= bottom
        )

    def _move_image_start(self, event):
        """
        Begin dragging the image if the mouse is inside it.
        """

        if not self._is_inside_preview_image(
            event.x,
            event.y,
        ):
            return

        self.drag_start = (event.x, event.y)

        self.drag_origin = (
            self.image_offset_x,
            self.image_offset_y,
        )

        self.preview_canvas.configure(cursor="fleur")

    def _move_image_drag(self, event):
        """
        Move the image directly on the canvas.

        The preview is repositioned without reprocessing
        the image, helping keep dragging responsive.
        """

        if (
            self.drag_start is None
            or self.drag_origin is None
            or self.preview_item_id is None
        ):
            return

        start_x, start_y = self.drag_start
        origin_x, origin_y = self.drag_origin

        delta_x = event.x - start_x
        delta_y = event.y - start_y

        self.image_offset_x = origin_x + delta_x
        self.image_offset_y = origin_y + delta_y

        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        self.preview_canvas.coords(
            self.preview_item_id,
            canvas_width // 2 + self.image_offset_x,
            canvas_height // 2 + self.image_offset_y,
        )

        # Move the crop selection with the image so that
        # an active crop selection remains visible.
        if (
            self.crop_rectangle is not None
            and self.preview_canvas.type(
                self.crop_rectangle
            ) == "rectangle"
        ):
            self.preview_canvas.tag_raise(
                self.crop_rectangle
            )

    def _move_image_end(self):
        """Finish dragging the image."""

        self.drag_start = None
        self.drag_origin = None

        if self.current_image is not None:
            if self.crop_mode:
                self.preview_canvas.configure(
                    cursor="crosshair"
                )
            else:
                self.preview_canvas.configure(
                    cursor="fleur"
                )

    # -------------------------------------------------
    # CROP
    # -------------------------------------------------

    def start_crop(self):
        if self.current_image is None:
            messagebox.showinfo(
                "Crop Image",
                "Please open an image first.",
            )
            return

        self.crop_mode = True
        self.crop_start = None

        # Prevent an unfinished drag from continuing.
        self._move_image_end()

        if self.crop_rectangle is not None:
            self.preview_canvas.delete(
                self.crop_rectangle
            )
            self.crop_rectangle = None

        self.status_label.configure(
            text="CROP MODE",
            fg=self.accent,
        )

        self.preview_canvas.configure(cursor="crosshair")

        messagebox.showinfo(
            "Crop Image",
            "Drag your mouse across the image to select "
            "the crop area, then click Apply Crop.",
        )

    def _crop_start_event(self, event):
        if (
            not self.crop_mode
            or self.current_image is None
        ):
            # NEW: Normal mouse press starts image dragging.
            self._move_image_start(event)
            return

        # Original crop-selection behavior
        if not self._is_inside_preview_image(
            event.x,
            event.y,
        ):
            return

        self.crop_start = (event.x, event.y)

        if self.crop_rectangle is not None:
            self.preview_canvas.delete(
                self.crop_rectangle
            )

        self.crop_rectangle = (
            self.preview_canvas.create_rectangle(
                event.x,
                event.y,
                event.x,
                event.y,
                outline=self.accent,
                width=2,
                dash=(5, 3),
            )
        )

    def _crop_drag_event(self, event):
        if not self.crop_mode:
            # NEW: Drag the image when crop mode is off.
            self._move_image_drag(event)
            return

        if (
            self.crop_start is None
            or self.crop_rectangle is None
        ):
            return

        x1, y1 = self.crop_start

        self.preview_canvas.coords(
            self.crop_rectangle,
            x1,
            y1,
            event.x,
            event.y,
        )

    def _crop_release_event(self, event):
        if not self.crop_mode:
            # NEW: End image dragging.
            self._move_image_end()
            return

        # Original crop behavior is preserved.
        if self.crop_start is None:
            return

    def apply_crop(self):
        if self.current_image is None:
            return

        if self.crop_rectangle is None:
            messagebox.showinfo(
                "Crop Image",
                "Select an area of the image first.",
            )
            return

        coords = self.preview_canvas.coords(
            self.crop_rectangle
        )

        if len(coords) != 4:
            return

        x1, y1, x2, y2 = coords

        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)

        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        image_width, image_height = self.current_image.size

        fit_scale = min(
            (canvas_width - 30) / image_width,
            (canvas_height - 30) / image_height,
            1.0,
        )

        scale = fit_scale * self.zoom

        if scale <= 0:
            return

        displayed_width = image_width * scale
        displayed_height = image_height * scale

        # NEW: Account for the image's moved position.
        image_left = (
            canvas_width - displayed_width
        ) / 2 + self.image_offset_x

        image_top = (
            canvas_height - displayed_height
        ) / 2 + self.image_offset_y

        # Convert the selected canvas area into image coordinates.
        crop_left = int(
            (left - image_left) / scale
        )

        crop_top = int(
            (top - image_top) / scale
        )

        crop_right = int(
            (right - image_left) / scale
        )

        crop_bottom = int(
            (bottom - image_top) / scale
        )

        crop_left = max(
            0,
            min(image_width, crop_left),
        )

        crop_top = max(
            0,
            min(image_height, crop_top),
        )

        crop_right = max(
            0,
            min(image_width, crop_right),
        )

        crop_bottom = max(
            0,
            min(image_height, crop_bottom),
        )

        if (
            crop_right - crop_left < 2
            or crop_bottom - crop_top < 2
        ):
            messagebox.showwarning(
                "Crop Image",
                "The selected crop area is too small "
                "or outside the image.",
            )
            return

        self._push_undo()

        self.current_image = self.current_image.crop(
            (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom,
            )
        )

        self.zoom = 1.0

        # Reset position after cropping.
        self.image_offset_x = 0
        self.image_offset_y = 0

        self.cancel_crop()
        self.render_preview()

    def cancel_crop(self):
        self.crop_mode = False
        self.crop_start = None

        # Stop any active image drag.
        self._move_image_end()

        if hasattr(self, "preview_canvas"):
            if self.crop_rectangle is not None:
                self.preview_canvas.delete(
                    self.crop_rectangle
                )
                self.crop_rectangle = None

            if self.current_image is not None:
                self.preview_canvas.configure(
                    cursor="fleur"
                )
            else:
                self.preview_canvas.configure(cursor="")

        if hasattr(self, "status_label"):
            self.status_label.configure(
                text=(
                    "IMAGE LOADED"
                    if self.current_image is not None
                    else "READY"
                ),
                fg=self.green,
            )

    # -------------------------------------------------
    # ROTATE AND FLIP
    # -------------------------------------------------

    def _push_undo(self):
        if self.current_image is None:
            return

        self.undo_stack.append(
            self.current_image.copy()
        )

        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        self.redo_stack.clear()

    def transform_image(self, operation):
        if self.current_image is None:
            messagebox.showinfo(
                "Edit Image",
                "Please open an image first.",
            )
            return

        self._push_undo()

        if operation == "rotate_left":
            self.current_image = self.current_image.rotate(
                90,
                expand=True,
            )

        elif operation == "rotate_right":
            self.current_image = self.current_image.rotate(
                -90,
                expand=True,
            )

        elif operation == "flip_horizontal":
            self.current_image = ImageOps.mirror(
                self.current_image
            )

        elif operation == "flip_vertical":
            self.current_image = ImageOps.flip(
                self.current_image
            )

        self.zoom = 1.0

        # Keep the original behavior of centering the
        # transformed image.
        self.image_offset_x = 0
        self.image_offset_y = 0

        self.cancel_crop()
        self.render_preview()

    # -------------------------------------------------
    # UNDO AND REDO
    # -------------------------------------------------

    def undo(self):
        if (
            not self.undo_stack
            or self.current_image is None
        ):
            return

        self.redo_stack.append(
            self.current_image.copy()
        )

        self.current_image = self.undo_stack.pop()

        self.zoom = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0

        self.cancel_crop()
        self.render_preview()

    def redo(self):
        if (
            not self.redo_stack
            or self.current_image is None
        ):
            return

        self.undo_stack.append(
            self.current_image.copy()
        )

        self.current_image = self.redo_stack.pop()

        self.zoom = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0

        self.cancel_crop()
        self.render_preview()

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset_edits(self):
        if self.current_image is None:
            return

        self._reset_slider_values()
        self.render_preview()

    def reset_all(self):
        if self.original_image is None:
            return

        answer = messagebox.askyesno(
            "Reset All",
            "Reset the image and all adjustments to the original?",
        )

        if not answer:
            return

        self.current_image = self.original_image.copy()

        self.undo_stack.clear()
        self.redo_stack.clear()

        self._reset_slider_values()
        self.cancel_crop()

        self.zoom = 1.0

        # Reset image position.
        self.image_offset_x = 0
        self.image_offset_y = 0

        self.render_preview()

    # -------------------------------------------------
    # SAVE IMAGE
    # -------------------------------------------------

    def save_image(self):
        if self.current_image is None:
            messagebox.showinfo(
                "Save Image",
                "Please open an image first.",
            )
            return

        default_name = "edited_image.png"

        if self.current_path:
            name = os.path.splitext(
                os.path.basename(self.current_path)
            )[0]

            default_name = f"{name}_edited.png"

        path = filedialog.asksaveasfilename(
            title="Save Edited Image",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg *.jpeg"),
                ("WEBP Image", "*.webp"),
                ("TIFF Image", "*.tif *.tiff"),
                ("BMP Image", "*.bmp"),
            ],
        )

        if not path:
            return

        try:
            self.status_label.configure(
                text="SAVING...",
                fg=self.accent,
            )

            self.root.update_idletasks()

            # Process at the original image resolution.
            final_image = self.process_image(
                self.current_image.copy()
            )

            extension = os.path.splitext(
                path
            )[1].lower()

            if extension in (".jpg", ".jpeg"):
                final_image.save(
                    path,
                    "JPEG",
                    quality=95,
                    optimize=True,
                )

            elif extension == ".webp":
                final_image.save(
                    path,
                    "WEBP",
                    quality=95,
                )

            elif extension in (".tif", ".tiff"):
                final_image.save(path, "TIFF")

            elif extension == ".bmp":
                final_image.save(path, "BMP")

            else:
                final_image.save(
                    path,
                    "PNG",
                    optimize=True,
                )

            self.status_label.configure(
                text="SAVED",
                fg=self.green,
            )

            messagebox.showinfo(
                "Image Saved",
                f"Your edited image was saved successfully:\n\n{path}",
            )

        except Exception as error:
            self.status_label.configure(
                text="SAVE ERROR",
                fg=self.red,
            )

            messagebox.showerror(
                "Save Error",
                f"Could not save the image.\n\n{error}",
            )

    # -------------------------------------------------
    # EXIT
    # -------------------------------------------------

    def exit_app(self):
        confirm = messagebox.askyesno(
            "Confirm Exit",
            "Are You Sure You Want to Exit ZaBir Image Editor?",
            icon="warning",
            parent=self.root,
        )

        if not confirm:
            return

        if self.slider_after_id is not None:
            try:
                self.root.after_cancel(
                    self.slider_after_id
                )
            except tk.TclError:
                pass

        self.root.destroy()


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()