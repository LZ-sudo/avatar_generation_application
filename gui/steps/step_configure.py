"""
Step 4: Avatar Configuration

Allows the user to configure avatar generation options.
"""

import customtkinter as ctk
from pathlib import Path

from ..app_state import AppState, RigType
from typing import Callable, Optional
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
        "Default (No Toes)": RigType.DEFAULT_NO_TOES.value,
        "CMU MB": RigType.CMU_MB.value,
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        on_navigate_next: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate_next = on_navigate_next
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

        # Next button (centered)
        self._next_button = ctk.CTkButton(
            content_frame,
            text="Next",
            command=self._on_next_click,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._next_button.pack(pady=(30, 0))

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
            "CMU MB"
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

        # BVH Animation File
        self._bvh_picker = FilePicker(
            content,
            label="BVH Animation File (Optional)",
            filetypes=[("BVH files", "*.bvh"), ("All files", "*.*")],
            entry_width=170,
            on_file_selected=self._on_bvh_selected,
        )
        self._bvh_picker.pack(anchor="w", fill="x")

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

    def _on_hair_change(self, value: str) -> None:
        """Handle hair asset change."""
        hair_asset = next(
            (asset for name, asset in self._hair_assets if name == value),
            None
        )
        self.app_state.configure.hair_asset = hair_asset
        self._update_preview()
        self.app_state.notify_change()

    def _on_bvh_selected(self, file_path: Path) -> None:
        """Handle BVH animation file selection."""
        self.app_state.configure.bvh_animation_path = file_path
        self.app_state.notify_change()

    def _on_next_click(self) -> None:
        """Handle next button click."""
        if self.on_navigate_next:
            self.on_navigate_next()

    def validate(self) -> bool:
        """Validate the step is complete."""
        # Ensure FK/IK hybrid and T-Pose are always enabled
        self.app_state.configure.fk_ik_hybrid = True
        self.app_state.configure.t_pose = True
        return self.app_state.configure.is_complete()
