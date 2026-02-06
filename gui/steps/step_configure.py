"""
Step 4: Avatar Configuration

Allows the user to configure avatar generation options.
"""

import customtkinter as ctk
from pathlib import Path

from ..app_state import AppState, RigType, InstrumentedArm
from ..components.ui_elements import (
    ThemeColors,
    PageHeader,
    SectionHeader,
    Card,
    ImagePreview,
    FilePicker,
)


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

    INSTRUMENTED_ARM_OPTIONS = {
        "Left": InstrumentedArm.LEFT.value,
        "Right": InstrumentedArm.RIGHT.value,
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self._hair_assets = self._load_hair_assets()
        self._build()

    def _load_hair_assets(self) -> list[tuple[str, str]]:
        """
        Load hair assets from mpfb_hair_assets directory.

        Returns:
            List of tuples: (display_name, asset_name)
        """
        project_root = Path(__file__).parent.parent.parent
        hair_assets_dir = project_root / "mesh_generation_module" / "mpfb_hair_assets"

        assets = [("None", None)]

        if not hair_assets_dir.exists():
            return assets

        for asset_dir in sorted(hair_assets_dir.iterdir()):
            if not asset_dir.is_dir():
                continue

            asset_name = asset_dir.name
            display_name = asset_name.replace("_", " ").title()

            assets.append((display_name, asset_name))

        return assets

    def _get_preview_image_path(self, asset_name: str) -> Path:
        """
        Get the preview image path for a hair asset.

        Searches for .thumb files inside the hair asset directory.

        Args:
            asset_name: The name of the hair asset

        Returns:
            Path to the preview .thumb image, or None if not found
        """
        if asset_name is None:
            return None

        project_root = Path(__file__).parent.parent.parent
        hair_asset_dir = project_root / "mesh_generation_module" / "mpfb_hair_assets" / asset_name

        if not hair_asset_dir.exists():
            return None

        # Look for .thumb files in the asset directory
        thumb_files = list(hair_asset_dir.glob("*.thumb"))
        if thumb_files:
            return thumb_files[0]

        return None

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
        panel = Card(parent)

        content = panel.content

        header = SectionHeader(content, text="Avatar Settings", font_size=16)
        header.pack(anchor="w", fill="x")

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

        hair_display_names = [name for name, _ in self._hair_assets]
        current_hair_asset = self.app_state.configure.hair_asset
        current_hair_display = next(
            (name for name, asset in self._hair_assets if asset == current_hair_asset),
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

        # C3D File Upload (Placeholder for future functionality)
        self._c3d_picker = FilePicker(
            content,
            label="C3D Motion Capture File (Optional)",
            filetypes=[("C3D files", "*.c3d"), ("All files", "*.*")],
            entry_width=170,
            on_file_selected=self._on_c3d_selected,
        )
        self._c3d_picker.pack(anchor="w", fill="x")

        return panel

    def _create_hair_preview(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the hair preview panel."""
        panel = Card(parent)

        content = panel.content

        header = SectionHeader(content, text="Hair Preview", font_size=16)
        header.pack(anchor="w", fill="x")

        # Preview
        self._preview_label = ImagePreview(
            content,
            width=330,
            height=330,
            placeholder_text="No preview available",
        )
        self._preview_label.pack()

        # Load initial preview
        self._update_preview()

        return panel

    def _update_preview(self) -> None:
        """Update the hair preview image."""
        hair_asset = self.app_state.configure.hair_asset

        if hair_asset is None:
            self._preview_label.clear()
            return

        image_path = self._get_preview_image_path(hair_asset)
        self._preview_label.load_image(image_path)

    def _on_rig_change(self, value: str) -> None:
        """Handle rig type change."""
        rig_value = self.RIG_OPTIONS[value]
        self.app_state.configure.rig_type = RigType(rig_value)
        self.app_state.notify_change()

    def _on_arm_change(self, value: str) -> None:
        """Handle instrumented arm change."""
        arm_value = self.INSTRUMENTED_ARM_OPTIONS[value]
        self.app_state.configure.instrumented_arm = InstrumentedArm(arm_value)
        self.app_state.notify_change()

    def _on_hair_change(self, value: str) -> None:
        """Handle hair asset change."""
        hair_asset = next(
            (asset for name, asset in self._hair_assets if name == value),
            None
        )
        self.app_state.configure.hair_asset = hair_asset
        self._update_preview()
        self.app_state.notify_change()

    def _on_c3d_selected(self, file_path: Path) -> None:
        """Handle C3D file selection (placeholder for future functionality)."""
        # TODO: Store C3D file path in app state when functionality is implemented
        pass

    def validate(self) -> bool:
        """Validate the step is complete."""
        # Ensure FK/IK hybrid and T-Pose are always enabled
        self.app_state.configure.fk_ik_hybrid = True
        self.app_state.configure.t_pose = True
        return self.app_state.configure.is_complete()
