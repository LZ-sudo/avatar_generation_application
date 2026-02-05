"""
Step 4: Avatar Configuration

Allows the user to configure avatar generation options.
"""

import customtkinter as ctk
from pathlib import Path
from PIL import Image as PILImage

from ..app_state import AppState, RigType, InstrumentedArm
from ..components.ui_elements import ThemeColors, PageHeader, SectionTitle


class StepConfigure(ctk.CTkFrame):
    """
    Configuration step for the avatar generation wizard.

    Provides options for rig type, FK/IK hybrid, instrumented arm, hair asset, and T-pose.
    """

    RIG_OPTIONS = {
        "Default": RigType.DEFAULT.value,
        "Default (No Toes)": RigType.DEFAULT_NO_TOES.value,
        "Game Engine": RigType.GAME_ENGINE.value,
    }

    # Hair assets available in mpfb_hair_assets folder
    HAIR_ASSETS = [
        ("None", None),
        ("Short Hair B", "Short_Hair_B"),
        ("Female Hair 01", "fhair01"),
        ("Hair 08", "hair_08"),
        ("Male Hair 02", "mhair02"),
        ("Elven Ashley May Hair", "elvs_ashley_may_hair"),
        ("Elven Daisy Hair", "elvs_daisy_hair"),
        ("Elven Hazel Hair", "elvs_hazel_hair"),
        ("Elven Keylth Hair", "elvs_keylth_hair"),
        ("Elven Short Daisy Hair", "elvs_short_daisy_hair"),
        ("Elven That 80s Babe Hair", "elvs_that_80s_babe_hair"),
        ("Elven Wavy Bob", "elvs_wavy_bob"),
        ("Elven Witchy Lil Bob", "elvs_witchy_lil_bob"),
    ]

    # Mapping hair assets to preview images
    HAIR_PREVIEW_IMAGES = {
        "Short_Hair_B": "Short_Hair_B.jpg",
        "fhair01": "fhair01.jpeg",
        "hair_08": "hair_08.jpeg",
        "mhair02": "mhair02.jpeg",
        "elvs_ashley_may_hair": "elvs_ashley_may_hair.jpeg",
        "elvs_daisy_hair": "elvs_daisy_hair.jpeg",
        "elvs_hazel_hair": "elvs_hazel_hair.jpeg",
        "elvs_keylth_hair": "elvs_keylth_hair.jpeg",
        "elvs_short_daisy_hair": "elvs_short_daisy_hair.jpeg",
        "elvs_that_80s_babe_hair": "elvs_that_80s_babe_hair.jpeg",
        "elvs_wavy_bob": "elvs_wavy_bob.jpeg",
        "elvs_witchy_lil_bob": "elvs_witchy_lil_bob.jpeg",
    }

    INSTRUMENTED_ARM_OPTIONS = {
        "Left": InstrumentedArm.LEFT.value,
        "Right": InstrumentedArm.RIGHT.value,
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self._current_preview_image = None
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header = PageHeader(
            content_frame,
            title="Configure Avatar",
            subtitle="Set avatar options and output preferences.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        panels_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        panels_frame.pack(pady=20)

        avatar_options = self._create_avatar_options(panels_frame)
        avatar_options.pack(side="left", padx=15, anchor="n")

        preview_panel = self._create_hair_preview(panels_frame)
        preview_panel.pack(side="left", padx=15, anchor="n")

    def _create_avatar_options(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the avatar options panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = SectionTitle(content, text="Avatar Settings", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 15))

        # Rig Type
        rig_label = ctk.CTkLabel(
            content,
            text="Rig Type",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        rig_label.pack(anchor="w")

        rig_values = list(self.RIG_OPTIONS.keys())
        current_rig = next(
            (k for k, v in self.RIG_OPTIONS.items() if v == self.app_state.configure.rig_type.value),
            rig_values[1]  # Default to "Default (No Toes)"
        )

        self._rig_var = ctk.StringVar(value=current_rig)
        self._rig_dropdown = ctk.CTkOptionMenu(
            content,
            width=250,
            values=rig_values,
            variable=self._rig_var,
            command=self._on_rig_change,
        )
        self._rig_dropdown.pack(anchor="w", pady=(5, 15))

        # FK/IK Hybrid
        self._fk_ik_var = ctk.BooleanVar(value=self.app_state.configure.fk_ik_hybrid)
        self._fk_ik_checkbox = ctk.CTkCheckBox(
            content,
            text="FK/IK Hybrid (for IMU motion capture)",
            variable=self._fk_ik_var,
            command=self._on_fk_ik_change,
        )
        self._fk_ik_checkbox.pack(anchor="w", pady=(0, 15))

        # Instrumented Arm
        arm_label = ctk.CTkLabel(
            content,
            text="Instrumented Arm",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        arm_label.pack(anchor="w")

        arm_values = list(self.INSTRUMENTED_ARM_OPTIONS.keys())
        current_arm = next(
            (k for k, v in self.INSTRUMENTED_ARM_OPTIONS.items() if v == self.app_state.configure.instrumented_arm.value),
            arm_values[0]
        )

        self._arm_var = ctk.StringVar(value=current_arm)
        self._arm_dropdown = ctk.CTkOptionMenu(
            content,
            width=250,
            values=arm_values,
            variable=self._arm_var,
            command=self._on_arm_change,
        )
        self._arm_dropdown.pack(anchor="w", pady=(5, 15))

        # Hair Asset
        hair_label = ctk.CTkLabel(
            content,
            text="Hair Asset",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        hair_label.pack(anchor="w")

        hair_display_names = [name for name, _ in self.HAIR_ASSETS]
        current_hair_asset = self.app_state.configure.hair_asset
        current_hair_display = next(
            (name for name, asset in self.HAIR_ASSETS if asset == current_hair_asset),
            hair_display_names[0]  # Default to "None"
        )

        self._hair_var = ctk.StringVar(value=current_hair_display)
        self._hair_dropdown = ctk.CTkOptionMenu(
            content,
            width=250,
            values=hair_display_names,
            variable=self._hair_var,
            command=self._on_hair_change,
        )
        self._hair_dropdown.pack(anchor="w", pady=(5, 15))

        # T-Pose
        self._t_pose_var = ctk.BooleanVar(value=self.app_state.configure.t_pose)
        self._t_pose_checkbox = ctk.CTkCheckBox(
            content,
            text="Export in T-Pose",
            variable=self._t_pose_var,
            command=self._on_t_pose_change,
        )
        self._t_pose_checkbox.pack(anchor="w", pady=(0, 0))

        return panel

    def _create_hair_preview(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the hair preview panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = SectionTitle(content, text="Hair Preview", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 15))

        # Preview label
        self._preview_label = ctk.CTkLabel(
            content,
            text="",
            width=330,
            height=330,
        )
        self._preview_label.pack()

        # Load initial preview
        self._update_preview()

        return panel

    def _update_preview(self) -> None:
        """Update the hair preview image."""
        hair_asset = self.app_state.configure.hair_asset

        if hair_asset is None or hair_asset not in self.HAIR_PREVIEW_IMAGES:
            # No preview available
            self._preview_label.configure(
                text="No preview available",
                image=None,
            )
            self._current_preview_image = None
        else:
            # Load preview image
            image_filename = self.HAIR_PREVIEW_IMAGES[hair_asset]
            image_path = Path(__file__).parent.parent / "images" / image_filename

            if image_path.exists():
                try:
                    pil_image = PILImage.open(image_path)
                    # Resize to fit preview (max 330x330, maintain aspect ratio)
                    pil_image.thumbnail((330, 330), PILImage.Resampling.LANCZOS)
                    ctk_image = ctk.CTkImage(
                        light_image=pil_image,
                        dark_image=pil_image,
                        size=pil_image.size
                    )
                    self._current_preview_image = ctk_image
                    self._preview_label.configure(
                        text="",
                        image=ctk_image,
                    )
                except Exception as e:
                    self._preview_label.configure(
                        text=f"Error loading preview:\n{str(e)}",
                        image=None,
                    )
                    self._current_preview_image = None
            else:
                self._preview_label.configure(
                    text="Preview image not found",
                    image=None,
                )
                self._current_preview_image = None

    def _on_rig_change(self, value: str) -> None:
        """Handle rig type change."""
        rig_value = self.RIG_OPTIONS[value]
        self.app_state.configure.rig_type = RigType(rig_value)
        self.app_state.notify_change()

    def _on_fk_ik_change(self) -> None:
        """Handle FK/IK hybrid checkbox change."""
        self.app_state.configure.fk_ik_hybrid = self._fk_ik_var.get()
        self.app_state.notify_change()

    def _on_arm_change(self, value: str) -> None:
        """Handle instrumented arm change."""
        arm_value = self.INSTRUMENTED_ARM_OPTIONS[value]
        self.app_state.configure.instrumented_arm = InstrumentedArm(arm_value)
        self.app_state.notify_change()

    def _on_hair_change(self, value: str) -> None:
        """Handle hair asset change."""
        # Find the asset name for the selected display name
        hair_asset = next(
            (asset for name, asset in self.HAIR_ASSETS if name == value),
            None
        )
        self.app_state.configure.hair_asset = hair_asset
        self._update_preview()
        self.app_state.notify_change()

    def _on_t_pose_change(self) -> None:
        """Handle T-pose checkbox change."""
        self.app_state.configure.t_pose = self._t_pose_var.get()
        self.app_state.notify_change()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.configure.is_complete()
